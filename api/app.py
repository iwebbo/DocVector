# api/app.py
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from werkzeug.utils import secure_filename
import sys
from pathlib import Path
import logging

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.config import OpenSearchConfig, EmbeddingConfig, ChunkingConfig
from src.opensearch_client import OpenSearchClient
from src.embeddings import EmbeddingGenerator
from src.chunker import TextChunker
from src.ingestion_pipeline import IngestionPipeline

app = Flask(__name__)
CORS(app)

app.config['UPLOAD_FOLDER'] = Path(__file__).parent.parent / 'data' / 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024
app.config['UPLOAD_FOLDER'].mkdir(parents=True, exist_ok=True)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

ALLOWED_EXTENSIONS = {'txt', 'pdf', 'md', 'markdown', 'doc', 'docx', 'xlsx', 'xls', 
                      'py', 'java', 'js', 'ts', 'go', 'rb', 'yml', 'yaml', 'json'}

os_client = None
embedder = None
pipeline = None

def init_clients():
    global os_client, embedder, pipeline
    try:
        os_config = OpenSearchConfig()
        embed_config = EmbeddingConfig()
        chunk_config = ChunkingConfig()
        
        os_client = OpenSearchClient(os_config)
        embedder = EmbeddingGenerator(embed_config)
        chunker = TextChunker(chunk_config.max_chunk_size, chunk_config.overlap)
        pipeline = IngestionPipeline(os_client, embedder, chunker)
        
        logger.info("Clients initialized")
        return True
    except Exception as e:
        logger.error(f"Init error: {e}")
        return False

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/health')
def health():
    return jsonify({"status": "healthy"}), 200

@app.route('/api/status')
def status():
    try:
        count = os_client.count_documents()
        stats = os_client.client.indices.stats(index=os_client.index_name)
        size_mb = stats['_all']['primaries']['store']['size_in_bytes'] / 1024 / 1024
        
        agg_results = os_client.client.search(
            index=os_client.index_name,
            body={
                "size": 0,
                "aggs": {
                    "by_type": {"terms": {"field": "metadata.source_type", "size": 10}},
                    "by_ext": {"terms": {"field": "metadata.file_extension", "size": 10}}
                }
            }
        )
        
        return jsonify({
            "connected": True,
            "index": os_client.index_name,
            "document_count": count,
            "size_mb": round(size_mb, 2),
            "by_type": [{"type": b['key'], "count": b['doc_count']} 
                       for b in agg_results['aggregations']['by_type']['buckets']],
            "by_extension": [{"ext": b['key'], "count": b['doc_count']} 
                            for b in agg_results['aggregations']['by_ext']['buckets']]
        })
    except Exception as e:
        return jsonify({"connected": False, "error": str(e)}), 500

@app.route('/api/upload', methods=['POST'])
def upload_files():
    try:
        if 'files[]' not in request.files:
            return jsonify({"error": "No files"}), 400
        
        files = request.files.getlist('files[]')
        uploaded = []
        errors = []
        
        for file in files:
            if file and file.filename and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file.save(app.config['UPLOAD_FOLDER'] / filename)
                uploaded.append(filename)
            else:
                errors.append(f"{file.filename}: Unsupported type")
        
        return jsonify({"uploaded": uploaded, "errors": errors, "count": len(uploaded)})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/ingest', methods=['POST'])
def ingest():
    try:
        data = request.json or {}
        recreate = data.get('recreate', False)
        
        upload_dir = app.config['UPLOAD_FOLDER']
        files = list(upload_dir.glob('*'))
        
        if not files:
            return jsonify({"error": "No files to ingest"}), 400
        
        if recreate:
            os_client.delete_index()
            os_client.create_index(dimension=embedder.dimension)
        
        total = pipeline.process_directory(upload_dir, batch_size=50)
        count = os_client.count_documents()
        
        return jsonify({"success": True, "indexed": total, "total_documents": count})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/search', methods=['POST'])
def search():
    try:
        data = request.json
        query = data.get('query', '')
        top_k = data.get('top_k', 5)
        
        if not query:
            return jsonify({"error": "Empty query"}), 400
        
        query_embedding = embedder.encode(query)
        
        search_body = {
            "size": top_k,
            "query": {
                "bool": {
                    "should": [
                        {
                            "script_score": {
                                "query": {"match_all": {}},
                                "script": {
                                    "source": "knn_score",
                                    "lang": "knn",
                                    "params": {
                                        "field": "embedding",
                                        "query_value": query_embedding,
                                        "space_type": "l2"
                                    }
                                },
                                "boost": 0.7
                            }
                        },
                        {
                            "multi_match": {
                                "query": query,
                                "fields": ["content^2", "title"],
                                "boost": 0.3
                            }
                        }
                    ]
                }
            },
            "_source": ["content", "metadata", "title"]
        }
        
        results = os_client.client.search(index=os_client.index_name, body=search_body)
        
        hits = [{
            "score": hit['_score'],
            "content": hit['_source']['content'][:500],
            "metadata": hit['_source']['metadata']
        } for hit in results['hits']['hits']]
        
        return jsonify({"query": query, "results": hits, "total": results['hits']['total']['value']})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/clear-uploads', methods=['POST'])
def clear_uploads():
    try:
        count = 0
        for file in app.config['UPLOAD_FOLDER'].iterdir():
            if file.is_file():
                file.unlink()
                count += 1
        return jsonify({"deleted": count})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    if init_clients():
        app.run(host='0.0.0.0', port=8000, debug=True)
    else:
        sys.exit(1)
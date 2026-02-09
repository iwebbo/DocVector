# DocVector

A multi‑format document ingestion pipeline for OpenSearch with automatic vectorisation and RAG search.

## Features

- **Multi‑format ingestion**: PDF, Word, Excel, Markdown, Code (Python, Java, JS), YAML  
- **Automatic vectorisation**: Embeddings via Sentence Transformers  
- **OpenSearch k‑NN**: Vector index with hybrid search (semantic + keyword)  
- **Web UI**: Upload, ingest and search through a simple GUI

## Prérequis

- Docker & Docker Compose
- OpenSearch 3.x 
- Python 3.11+ 

## Installation

### 1. Clone the repository
```bash
git clone https://github.com/iwebbo/DocVector.git
cd DocVector
```

### 2. Configure OpenSearch

Create a .env file at the project root:
```env
OPENSEARCH_HOST=opensearch.votre-domaine.com
OPENSEARCH_PORT=9200
OPENSEARCH_USER=admin
OPENSEARCH_PASSWORD=votre-password
OPENSEARCH_USE_SSL=true
OPENSEARCH_VERIFY_CERTS=false
INDEX_NAME=knowledge_base
```

### 3. Build and run
```bash
cd docker
docker-compose build
docker-compose up -d
```

### 4. Access

Interface Web : **http://localhost:5000**

## Via the Web UI

Upload – Drag & drop your files.
Ingest – Click “Start Ingestion”.
Search – Perform RAG search on your documents.
OpenSearch Configuration
Index Mapping
The index is created automatically with the following settings:

Embeddings: 384 dimensions (model all-MiniLM-L6-v2)
k‑NN Engine: FAISS (compatible with OpenSearch 3.x)
Distance metric: L2 (Euclidean)


## Contribution

Pull requests welcome !

## License

MIT

## Contact

Pour questions : [votre-email]
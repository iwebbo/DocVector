# scripts/validate_rag.py
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from src.config import OpenSearchConfig, EmbeddingConfig
from src.opensearch_client import OpenSearchClient
from src.embeddings import EmbeddingGenerator
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RAGValidator:
    def __init__(self, os_client: OpenSearchClient, embedder: EmbeddingGenerator):
        self.client = os_client.client
        self.embedder = embedder
        self.index_name = os_client.index_name
    
    def hybrid_search(self, query: str, top_k: int = 5):
        """Recherche hybride: vector + keyword"""
        
        # Générer embedding de la query
        query_embedding = self.embedder.encode(query)
        
        search_body = {
            "size": top_k,
            "query": {
                "bool": {
                    "should": [
                        # Vector search
                        {
                            "script_score": {
                                "query": {"match_all": {}},
                                "script": {
                                    "source": "knn_score",
                                    "lang": "knn",
                                    "params": {
                                        "field": "embedding",
                                        "query_value": query_embedding,
                                        "space_type": "cosinesimil"
                                    }
                                },
                                "boost": 0.7
                            }
                        },
                        # Keyword search
                        {
                            "multi_match": {
                                "query": query,
                                "fields": ["content^2", "title"],
                                "type": "best_fields",
                                "boost": 0.3
                            }
                        }
                    ]
                }
            },
            "_source": ["content", "metadata", "title"],
            "highlight": {
                "fields": {
                    "content": {
                        "fragment_size": 150,
                        "number_of_fragments": 2
                    }
                }
            }
        }
        
        response = self.client.search(index=self.index_name, body=search_body)
        return self._format_results(response)
    
    def _format_results(self, response):
        results = []
        for hit in response['hits']['hits']:
            results.append({
                "score": hit['_score'],
                "content": hit['_source']['content'][:500],  # Tronqué pour affichage
                "metadata": hit['_source']['metadata'],
                "title": hit['_source'].get('title', 'N/A'),
                "highlights": hit.get('highlight', {}).get('content', [])
            })
        return results
    
    def test_rag_pipeline(self):
        """Test complet du pipeline RAG"""
        
        test_queries = [
            "How to configure Jenkins pipeline?",
            "Python function for data processing",
            "Kubernetes deployment configuration",
            "Excel formula examples"
        ]
        
        logger.info("=" * 60)
        logger.info("TEST PIPELINE RAG")
        logger.info("=" * 60)
        
        for query in test_queries:
            logger.info(f"\n🔍 Query: {query}")
            logger.info("-" * 60)
            
            results = self.hybrid_search(query, top_k=3)
            
            if not results:
                logger.warning("❌ Aucun résultat trouvé")
                continue
            
            for idx, result in enumerate(results, 1):
                logger.info(f"\n📄 Résultat {idx} (score: {result['score']:.3f})")
                logger.info(f"Source: {result['metadata']['file_name']}")
                logger.info(f"Type: {result['metadata']['source_type']}")
                logger.info(f"Content: {result['content'][:200]}...")
                
                if result['highlights']:
                    logger.info(f"Highlights: {result['highlights'][0]}")
            
            logger.info("\n" + "=" * 60)

def main():
    # Config
    os_config = OpenSearchConfig()
    embed_config = EmbeddingConfig()
    
    # Clients
    logger.info("Connexion OpenSearch...")
    os_client = OpenSearchClient(os_config)
    
    # Vérifier que l'index existe
    if not os_client.client.indices.exists(index=os_config.index_name):
        logger.error(f"❌ Index {os_config.index_name} n'existe pas. Lance d'abord ingest.py")
        return
    
    count = os_client.count_documents()
    logger.info(f"✅ Index trouvé avec {count} documents")
    
    logger.info("Chargement modèle embeddings...")
    embedder = EmbeddingGenerator(embed_config)
    
    # Validation
    validator = RAGValidator(os_client, embedder)
    validator.test_rag_pipeline()
    
    logger.info("\n✅ Validation RAG terminée")

if __name__ == "__main__":
    main()
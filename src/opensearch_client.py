# src/opensearch_client.py - VERSION COMPLÈTE FINALE
from opensearchpy import OpenSearch, helpers
from typing import List, Dict
import logging
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

logger = logging.getLogger(__name__)

class OpenSearchClient:
    def __init__(self, config):
        self.config = config
        
        # LOGS DE DEBUG - DOIVENT S'AFFICHER
        logger.info("=" * 60)
        logger.info("INIT CLIENT OPENSEARCH")
        logger.info("=" * 60)
        logger.info(f"Host: {config.host}:{config.port}")
        
        # Configuration client
        self.client = OpenSearch(
            hosts=[{'host': config.host, 'port': config.port}],
            http_auth=(config.user, config.password),
            use_ssl=config.use_ssl,
            verify_certs=config.verify_certs,
            ssl_show_warn=False,
            timeout=30
        )
        self.index_name = config.index_name
        
        # Test connexion obligatoire
        try:
            info = self.client.info()
            logger.info(f"Connected to Opensearch Instance")
            logger.info(f"   Cluster: {info['cluster_name']}")
            logger.info(f"   Version: {info['version']['number']}")
            logger.info("=" * 60)
        except Exception as e:
            logger.error(f"Connexion issue, Please check: {e}")
            logger.error("=" * 60)
            raise
        
    def create_index(self, dimension: int = 384):
        """Crée l'index avec mapping k-NN"""
        logger.info(f"Create index {self.index_name}...")
        
        # Vérifier existence
        try:
            exists = self.client.indices.exists(index=self.index_name)
            if exists:
                logger.info(f"ℹ️  Index {self.index_name} existe déjà")
                return False
        except Exception as e:
            logger.debug(f"Erreur vérification existence: {e}")
        
        # Mapping complet
        index_body = {
            "settings": {
                "index": {
                    "knn": True,
                    "knn.algo_param.ef_search": 100,
                    "number_of_shards": 2,
                    "number_of_replicas": 1
                }
            },
            "mappings": {
                "properties": {
                    "chunk_id": {"type": "keyword"},
                    "content": {"type": "text", "analyzer": "standard"},
                    "embedding": {
                        "type": "knn_vector",
                        "dimension": dimension,
                        "method": {
                            "name": "hnsw",
                            "space_type": "cosinesimil",
                            "engine": "faiss",
                            "parameters": {"ef_construction": 128, "m": 16}
                        }
                    },
                    "metadata": {
                        "properties": {
                            "source_type": {"type": "keyword"},
                            "file_path": {"type": "keyword"},
                            "file_name": {"type": "keyword"},
                            "file_extension": {"type": "keyword"},
                            "language": {"type": "keyword"},
                            "parent_doc_id": {"type": "keyword"},
                            "chunk_index": {"type": "integer"},
                            "total_chunks": {"type": "integer"},
                            "created_at": {"type": "date"}
                        }
                    },
                    "title": {"type": "text"},
                    "summary": {"type": "text"}
                }
            }
        }
        
        # Création
        try:
            self.client.indices.create(index=self.index_name, body=index_body)
            logger.info(f"✅ Index {self.index_name} créé")
            return True
        except Exception as e:
            if "resource_already_exists_exception" in str(e):
                logger.info(f"ℹ️  Index {self.index_name} existe déjà")
                return False
            else:
                logger.error(f"❌ Erreur création index: {e}")
                raise
    
    def bulk_index(self, documents: List[Dict]) -> dict:
        """Indexation bulk"""
        actions = [
            {"_index": self.index_name, "_id": doc["chunk_id"], "_source": doc}
            for doc in documents
        ]
        
        success, failed = helpers.bulk(
            self.client, actions, raise_on_error=False, raise_on_exception=False
        )
        
        logger.info(f"Indexés: {success}, Échecs: {len(failed)}")
        return {"success": success, "failed": len(failed)}
    
    def count_documents(self) -> int:
        """Compte documents dans l'index"""
        try:
            if not self.client.indices.exists(index=self.index_name):
                return 0
            return self.client.count(index=self.index_name)['count']
        except Exception as e:
            logger.warning(f"Erreur comptage: {e}")
            return 0
    
    def delete_index(self):
        """Supprime l'index"""
        try:
            if self.client.indices.exists(index=self.index_name):
                self.client.indices.delete(index=self.index_name)
                logger.info(f"✅ Index {self.index_name} supprimé")
            else:
                logger.info(f"ℹ️  Index {self.index_name} n'existe pas")
        except Exception as e:
            logger.warning(f"⚠️  Erreur suppression: {e}")
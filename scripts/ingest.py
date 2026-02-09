# scripts/ingest.py
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from src.config import OpenSearchConfig, EmbeddingConfig, ChunkingConfig
from src.opensearch_client import OpenSearchClient
from src.embeddings import EmbeddingGenerator
from src.chunker import TextChunker
from src.ingestion_pipeline import IngestionPipeline
import logging
import argparse

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main():
    parser = argparse.ArgumentParser(description='Ingestion documents vers OpenSearch')
    parser.add_argument('--input-dir', type=str, default='./data/input', help='Répertoire source')
    parser.add_argument('--recreate-index', action='store_true', help='Recréer l\'index')
    parser.add_argument('--batch-size', type=int, default=50, help='Taille des batchs')
    args = parser.parse_args()
    
    # Config
    os_config = OpenSearchConfig()
    embed_config = EmbeddingConfig()
    chunk_config = ChunkingConfig()
    
    # Client OpenSearch
    logger.info("Initialisation OpenSearch...")
    os_client = OpenSearchClient(os_config)
    
    # Gestion index
    if args.recreate_index:
        logger.info("Mode recreate-index : suppression puis création")
        os_client.delete_index()
        os_client.create_index(dimension=embed_config.dimension)
    else:
        # Crée l'index seulement s'il n'existe pas
        logger.info("Vérification/création index...")
        os_client.create_index(dimension=embed_config.dimension)
    
    # Embeddings
    logger.info("Initialisation modèle embeddings...")
    embedder = EmbeddingGenerator(embed_config)
    
    # Chunker
    chunker = TextChunker(
        max_chunk_size=chunk_config.max_chunk_size,
        overlap=chunk_config.overlap
    )
    
    # Pipeline
    pipeline = IngestionPipeline(os_client, embedder, chunker)
    
    # Vérif répertoire input
    input_dir = Path(args.input_dir)
    if not input_dir.exists():
        logger.error(f"❌ Répertoire {input_dir} n'existe pas")
        return
    
    # Ingestion
    logger.info(f"Début ingestion depuis {input_dir}")
    total = pipeline.process_directory(input_dir, batch_size=args.batch_size)
    
    # Stats finales
    count = os_client.count_documents()
    logger.info(f"✅ Ingestion terminée - {count} documents dans l'index")

if __name__ == "__main__":
    main()
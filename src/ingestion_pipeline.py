# src/ingestion_pipeline.py
from pathlib import Path
from typing import List, Dict
import hashlib
from datetime import datetime
import logging
from tqdm import tqdm

from .parsers.document_parser import DocumentParser
from .parsers.markdown_parser import MarkdownParser
from .parsers.code_parser import CodeParser
from .parsers.devops_parser import DevOpsParser
from .chunker import TextChunker
from .embeddings import EmbeddingGenerator
from .opensearch_client import OpenSearchClient

logger = logging.getLogger(__name__)

class IngestionPipeline:
    def __init__(self, os_client: OpenSearchClient, embedder: EmbeddingGenerator, chunker: TextChunker):
        self.os_client = os_client
        self.embedder = embedder
        self.chunker = chunker
        
        # Mapping extensions -> parsers
        self.parsers = {
            'document': DocumentParser(),
            'markdown': MarkdownParser(),
            'code': CodeParser(),
            'devops': DevOpsParser()
        }
    
    def process_directory(self, directory: Path, batch_size: int = 50):
        """Process tous les fichiers d'un répertoire"""
        files = list(directory.rglob('*'))
        files = [f for f in files if f.is_file()]
        
        logger.info(f"Trouvé {len(files)} fichiers à traiter")
        
        batch = []
        total_indexed = 0
        
        for file_path in tqdm(files, desc="Ingestion"):
            try:
                documents = self.process_file(file_path)
                batch.extend(documents)
                
                if len(batch) >= batch_size:
                    result = self.os_client.bulk_index(batch)
                    total_indexed += result['success']
                    batch = []
                    
            except Exception as e:
                logger.error(f"Erreur traitement {file_path}: {e}")
        
        # Dernier batch
        if batch:
            result = self.os_client.bulk_index(batch)
            total_indexed += result['success']
        
        logger.info(f"Total indexé: {total_indexed} documents")
        return total_indexed
    
    def process_file(self, file_path: Path) -> List[Dict]:
        """Process un fichier"""
        parser = self._get_parser(file_path)
        
        # 1. Parse
        raw_chunks = parser.parse(file_path)
        
        # 2. Chunk
        all_chunks = []
        for raw_chunk in raw_chunks:
            chunks = self.chunker.chunk_text(raw_chunk["text"], raw_chunk["metadata"])
            all_chunks.extend(chunks)
        
        # 3. Embeddings + metadata enrichie
        documents = []
        for idx, chunk in enumerate(all_chunks):
            embedding = self.embedder.encode(chunk["text"])
            
            doc = {
                "chunk_id": self._generate_id(file_path, idx),
                "content": chunk["text"],
                "embedding": embedding,
                "metadata": {
                    **chunk["metadata"],
                    "parent_doc_id": hashlib.md5(str(file_path).encode()).hexdigest(),
                    "created_at": datetime.now().isoformat()
                }
            }
            
            documents.append(doc)
        
        return documents
    
    def _get_parser(self, file_path: Path):
        """Sélection parser selon extension"""
        ext = file_path.suffix.lower()
        
        if ext in ['.md', '.markdown']:
            return self.parsers['markdown']
        elif ext in ['.py', '.java', '.js', '.ts', '.go', '.rb']:
            return self.parsers['code']
        elif ext in ['.yml', '.yaml'] or 'jenkinsfile' in file_path.name.lower():
            return self.parsers['devops']
        else:
            return self.parsers['document']
    
    def _generate_id(self, file_path: Path, chunk_idx: int) -> str:
        return hashlib.md5(f"{file_path}_{chunk_idx}".encode()).hexdigest()
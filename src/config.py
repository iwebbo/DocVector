# src/config.py
from dataclasses import dataclass
from typing import Dict
import os
from dotenv import load_dotenv
from pathlib import Path


project_root = Path(__file__).parent.parent
env_path = project_root / '.env'
load_dotenv(dotenv_path=env_path)

@dataclass
class OpenSearchConfig:
    host: str = os.getenv("OPENSEARCH_HOST", "localhost")
    port: int = int(os.getenv("OPENSEARCH_PORT", "9200"))
    user: str = os.getenv("OPENSEARCH_USER", "admin")
    password: str = os.getenv("OPENSEARCH_PASSWORD", "admin")
    use_ssl: bool = os.getenv("OPENSEARCH_USE_SSL", "false").lower() == "true"
    verify_certs: bool = os.getenv("OPENSEARCH_VERIFY_CERTS", "false").lower() == "true"
    index_name: str = os.getenv("INDEX_NAME", "knowledge_base")
    
@dataclass
class EmbeddingConfig:
    model_name: str = "all-MiniLM-L6-v2"
    dimension: int = 384
    device: str = "cpu"

@dataclass
class ChunkingConfig:
    max_chunk_size: int = 512
    overlap: int = 50
    
CHUNKING_STRATEGIES: Dict[str, dict] = {
    "markdown": {"max_tokens": 512, "overlap": 50},
    "code": {"max_tokens": 1024, "overlap": 0},
    "document": {"max_tokens": 512, "overlap": 50},
    "yaml": {"max_tokens": 768, "overlap": 20},
}
# src/embeddings.py
from sentence_transformers import SentenceTransformer
import numpy as np
from typing import List, Union
import logging

logger = logging.getLogger(__name__)

class EmbeddingGenerator:
    def __init__(self, config):
        self.config = config
        logger.info(f"Chargement du modèle {config.model_name}...")
        self.model = SentenceTransformer(config.model_name, device=config.device)
        logger.info("Modèle chargé")
        
    def encode(self, texts: Union[str, List[str]]) -> Union[List[float], List[List[float]]]:
        """Génère embeddings"""
        if isinstance(texts, str):
            texts = [texts]
            
        embeddings = self.model.encode(texts, convert_to_numpy=True, show_progress_bar=False)
        
        if len(texts) == 1:
            return embeddings[0].tolist()
        return embeddings.tolist()
    
    @property
    def dimension(self) -> int:
        return self.model.get_sentence_embedding_dimension()
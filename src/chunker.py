# src/chunker.py
from typing import List, Dict
import re

class TextChunker:
    def __init__(self, max_chunk_size: int = 512, overlap: int = 50):
        self.max_chunk_size = max_chunk_size
        self.overlap = overlap
    
    def chunk_text(self, text: str, metadata: Dict) -> List[Dict]:
        """Split texte en chunks avec overlap"""
        
        # Tokenisation simple (par mots)
        words = text.split()
        
        if len(words) <= self.max_chunk_size:
            return [{
                "text": text,
                "metadata": {**metadata, "chunk_index": 0, "total_chunks": 1}
            }]
        
        chunks = []
        start = 0
        chunk_index = 0
        
        while start < len(words):
            end = start + self.max_chunk_size
            chunk_words = words[start:end]
            chunk_text = " ".join(chunk_words)
            
            chunks.append({
                "text": chunk_text,
                "metadata": {
                    **metadata,
                    "chunk_index": chunk_index,
                    "total_chunks": -1  # sera mis à jour
                }
            })
            
            start = end - self.overlap
            chunk_index += 1
        
        # Mise à jour total_chunks
        for chunk in chunks:
            chunk["metadata"]["total_chunks"] = len(chunks)
        
        return chunks
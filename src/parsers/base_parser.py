# src/parsers/base_parser.py
from abc import ABC, abstractmethod
from typing import List, Dict
from pathlib import Path

class BaseParser(ABC):
    @abstractmethod
    def parse(self, file_path: Path) -> List[Dict]:
        """Retourne liste de chunks avec metadata"""
        pass
    
    def get_file_metadata(self, file_path: Path) -> Dict:
        """Metadata communes"""
        return {
            "file_path": str(file_path),
            "file_name": file_path.name,
            "file_extension": file_path.suffix.lstrip('.'),
            "file_size": file_path.stat().st_size
        }
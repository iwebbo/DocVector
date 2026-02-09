# src/parsers/code_parser.py
from .base_parser import BaseParser
from pathlib import Path
from typing import List, Dict
import re

class CodeParser(BaseParser):
    def parse(self, file_path: Path) -> List[Dict]:
        ext = file_path.suffix.lower()
        
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        
        language = self._detect_language(ext)
        
        # Parse simple par fonction/classe
        if ext == '.py':
            chunks = self._parse_python(content, file_path)
        elif ext in ['.java', '.js', '.ts']:
            chunks = self._parse_generic_code(content, file_path, language)
        else:
            chunks = [{
                "text": content,
                "metadata": {
                    **self.get_file_metadata(file_path),
                    "source_type": "code",
                    "language": language
                }
            }]
        
        return chunks
    
    def _parse_python(self, content: str, file_path: Path) -> List[Dict]:
        # Regex simple pour détecter fonctions/classes
        pattern = r'((?:class|def)\s+\w+.*?(?=\n(?:class|def)\s|\Z))'
        matches = re.findall(pattern, content, re.DOTALL)
        
        chunks = []
        for match in matches:
            if match.strip():
                chunks.append({
                    "text": match.strip(),
                    "metadata": {
                        **self.get_file_metadata(file_path),
                        "source_type": "code",
                        "language": "python"
                    }
                })
        
        return chunks if chunks else [{
            "text": content,
            "metadata": {
                **self.get_file_metadata(file_path),
                "source_type": "code",
                "language": "python"
            }
        }]
    
    def _parse_generic_code(self, content: str, file_path: Path, language: str) -> List[Dict]:
        return [{
            "text": content,
            "metadata": {
                **self.get_file_metadata(file_path),
                "source_type": "code",
                "language": language
            }
        }]
    
    def _detect_language(self, ext: str) -> str:
        lang_map = {
            '.py': 'python',
            '.java': 'java',
            '.js': 'javascript',
            '.ts': 'typescript',
            '.go': 'go',
            '.rb': 'ruby',
            '.php': 'php',
            '.c': 'c',
            '.cpp': 'cpp',
            '.cs': 'csharp'
        }
        return lang_map.get(ext, 'unknown')
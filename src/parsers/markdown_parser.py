# src/parsers/markdown_parser.py
from .base_parser import BaseParser
from pathlib import Path
from typing import List, Dict
import re

class MarkdownParser(BaseParser):
    def parse(self, file_path: Path) -> List[Dict]:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Split par headers
        sections = re.split(r'\n(?=#+\s)', content)
        chunks = []
        
        for section in sections:
            if section.strip():
                # Extraire titre
                title_match = re.match(r'#+\s+(.+)', section)
                title = title_match.group(1) if title_match else ""
                
                chunks.append({
                    "text": section.strip(),
                    "metadata": {
                        **self.get_file_metadata(file_path),
                        "source_type": "markdown",
                        "title": title
                    }
                })
        
        return chunks if chunks else [{
            "text": content,
            "metadata": {
                **self.get_file_metadata(file_path),
                "source_type": "markdown"
            }
        }]
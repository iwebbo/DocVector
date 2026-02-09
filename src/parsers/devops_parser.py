# src/parsers/devops_parser.py
from .base_parser import BaseParser
from pathlib import Path
from typing import List, Dict
import yaml
import re

class DevOpsParser(BaseParser):
    def parse(self, file_path: Path) -> List[Dict]:
        if 'jenkinsfile' in file_path.name.lower():
            return self._parse_jenkinsfile(file_path)
        elif file_path.suffix in ['.yml', '.yaml']:
            return self._parse_yaml(file_path)
        else:
            return self._parse_text(file_path)
    
    def _parse_jenkinsfile(self, file_path: Path) -> List[Dict]:
        with open(file_path, 'r') as f:
            content = f.read()
        
        # Split par stage
        stages = re.findall(r"stage\s*\(['\"](.+?)['\"]\)\s*\{(.+?)\}", content, re.DOTALL)
        chunks = []
        
        for stage_name, stage_content in stages:
            chunks.append({
                "text": f"Stage: {stage_name}\n{stage_content.strip()}",
                "metadata": {
                    **self.get_file_metadata(file_path),
                    "source_type": "devops",
                    "devops_type": "jenkins",
                    "stage": stage_name
                }
            })
        
        return chunks if chunks else [{
            "text": content,
            "metadata": {
                **self.get_file_metadata(file_path),
                "source_type": "devops",
                "devops_type": "jenkins"
            }
        }]
    
    def _parse_yaml(self, file_path: Path) -> List[Dict]:
        with open(file_path, 'r') as f:
            content = f.read()
            try:
                data = yaml.safe_load(content)
            except:
                data = None
        
        devops_type = "ansible" if "tasks" in str(data) or "playbook" in file_path.name.lower() else "kubernetes" if "apiVersion" in str(data) else "yaml"
        
        return [{
            "text": content,
            "metadata": {
                **self.get_file_metadata(file_path),
                "source_type": "devops",
                "devops_type": devops_type
            }
        }]
    
    def _parse_text(self, file_path: Path) -> List[Dict]:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        
        return [{
            "text": content,
            "metadata": {
                **self.get_file_metadata(file_path),
                "source_type": "devops"
            }
        }]
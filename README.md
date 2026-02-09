# DocVector

A multi‑format document ingestion pipeline for OpenSearch with automatic vectorisation and RAG search.

![License](https://img.shields.io/badge/MIT-00599C?style=for-the-badge&logo=MIT&logoColor=black)
![Python](https://img.shields.io/badge/Python-4EAA25?style=for-the-badge&logo=Python&logoColor=black)
![Kubernetes](https://img.shields.io/badge/Kubernetes-4EAA25?style=for-the-badge&logo=Kubernetes&logoColor=black)
![Docker](https://img.shields.io/badge/Docker-0078D6?style=for-the-badge&logo=Docker&logoColor=black)
![Opensearch](https://img.shields.io/badge/Opensearch-0078D6?style=for-the-badge&logo=Opensearch&logoColor=black)

## Features

- **Multi‑format ingestion**: PDF, Word, Excel, Markdown, Code (Python, Java, JS), YAML  
- **Automatic vectorisation**: Embeddings via Sentence Transformers  
- **OpenSearch k‑NN**: Vector index with hybrid search (semantic + keyword)  
- **Web UI**: Upload, ingest and search through a simple GUI

## Prérequis

- Docker & Docker Compose
- OpenSearch 3.x 
- Python 3.11+ 

## Installation

### ☸️ **Quick start with Kubernetes** *(Production-ready)*

> **Helm Chart + Documentation**

[ **Documentation Kubernetes officiel** →](https://iwebbo.github.io/DocVector/)

### ☸️ **Quick Start with Docker**

### 1. Clone the repository
```bash
    git clone https://github.com/iwebbo/DocVector.git
    cd DocVector
```

### 2. Configure OpenSearch

Create a .env file at the project root:
```env
OPENSEARCH_HOST=opensearch.votre-domaine.com
OPENSEARCH_PORT=9200
OPENSEARCH_USER=admin
OPENSEARCH_PASSWORD=votre-password
OPENSEARCH_USE_SSL=true
OPENSEARCH_VERIFY_CERTS=false
INDEX_NAME=knowledge_base
```

### 3. Build and run
```bash
cd docker
docker-compose build
docker-compose up -d
```

## Via the Web UI

- **Upload – Drag & drop your files**.
- **Ingest – Click “Start Ingestion”.**
- **Search – Perform RAG search on your documents.**

##  OpenSearch Configuration
Index Mapping
The index is created automatically with the following settings:

- **Embeddings: 384 dimensions (model all-MiniLM-L6-v2)**
- **k‑NN Engine: FAISS (compatible with OpenSearch 3.x)**
- **Distance metric: L2 (Euclidean)**

## Contribution
Pull requests welcome !

**Built with ❤️ for system administrators and DevOps engineers**

For questions, suggestions, or support, please open an issue or contact the maintainers.
<center><img width="300" height="300" alt="docvectorio" src="https://github.com/user-attachments/assets/7184990c-2db0-49da-a099-e4b1f901394b" /></center>

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

### Clone the repository
```bash
    git clone https://github.com/iwebbo/DocVector.git
    cd DocVector
```

### Prepare the Network
```bash
docker network create docvector-network
```

### Run the Backend (API)
```bash
docker run -d \
  --name docvector-api \
  --network docvector-network \
  -v $(pwd)/data:/app/data \
  -e OPENSEARCH_HOST="opensearch.aecoding.local" \
  -e OPENSEARCH_PORT=9200 \
  -e OPENSEARCH_USER="admin" \
  -e OPENSEARCH_PASSWORD="YOUR_SAFE_PASSWORD" \
  -e OPENSEARCH_USE_SSL="true" \
  -e OPENSEARCH_VERIFY_CERTS="false" \
  -e INDEX_NAME="knowledge_base" \
  -e PYTHONUNBUFFERED=1 \
  --restart unless-stopped \
  ghcr.io/iwebbo/docvector/api:main-ebc57c8
```

### Run the Frontend (Web UI)
The user interface will be accessible on port 8080
```bash
docker run -d \
  --name docvector-web \
  --network docvector-network \
  -p 8080:80 \
  --restart unless-stopped \
  ghcr.io/iwebbo/docvector/frontend:main-6261d08
```

### Configuration environments variables 
```env
OPENSEARCH_HOST	: Hostname or IP of your OpenSearch instance.
OPENSEARCH_PORT : Port (default: 9200).
OPENSEARCH_USER	: Admin username for OpenSearch.
INDEX_NAME : The name of the index where vectors are stored.
PYTHONUNBUFFERED : Ensures logs are sent straight to the terminal.
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

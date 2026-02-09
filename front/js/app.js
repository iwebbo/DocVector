// front/js/app.js
const API_URL = window.location.origin;

class App {
    constructor() {
        this.selectedFiles = [];
        this.init();
    }

    init() {
        this.setupNavigation();
        this.setupUpload();
        this.setupButtons();
        this.loadStatus();
        setInterval(() => this.loadStatus(), 30000);
    }

    setupNavigation() {
        document.querySelectorAll('.nav-item').forEach(item => {
            item.addEventListener('click', () => {
                const view = item.dataset.view;
                this.switchView(view);
            });
        });
    }

    switchView(view) {
        document.querySelectorAll('.nav-item').forEach(i => 
            i.classList.toggle('active', i.dataset.view === view));
        
        document.querySelectorAll('.view').forEach(v => 
            v.classList.toggle('active', v.id === `view-${view}`));
        
        const titles = {
            dashboard: 'Dashboard',
            upload: 'Upload & Ingest',
            search: 'Search'
        };
        document.getElementById('page-title').textContent = titles[view];
    }

    async loadStatus() {
        try {
            const res = await fetch(`${API_URL}/api/status`);
            const data = await res.json();

            const statusEl = document.getElementById('status');
            if (data.connected) {
                statusEl.classList.add('connected');
                statusEl.querySelector('span').textContent = 'Connected';

                document.getElementById('metric-docs').textContent = data.document_count.toLocaleString();
                document.getElementById('metric-size').textContent = `${data.size_mb} MB`;
                document.getElementById('metric-index').textContent = data.index;

                this.updateStats(data);
            } else {
                statusEl.classList.remove('connected');
                statusEl.querySelector('span').textContent = 'Disconnected';
            }
        } catch (err) {
            console.error('Status error:', err);
        }
    }

    updateStats(data) {
        const statsEl = document.getElementById('stats-by-type');
        statsEl.innerHTML = data.by_type.map(t => `
            <div class="stat-item">
                <span>${t.type}</span>
                <span>${t.count} docs</span>
            </div>
        `).join('');
    }

    setupUpload() {
        const zone = document.getElementById('upload-zone');
        const input = document.getElementById('file-input');

        zone.addEventListener('click', () => input.click());
        input.addEventListener('change', (e) => {
            this.selectedFiles = Array.from(e.target.files);
            this.renderFiles();
        });

        zone.addEventListener('dragover', (e) => {
            e.preventDefault();
            zone.style.borderColor = 'var(--primary)';
        });

        zone.addEventListener('dragleave', () => {
            zone.style.borderColor = 'var(--border)';
        });

        zone.addEventListener('drop', (e) => {
            e.preventDefault();
            zone.style.borderColor = 'var(--border)';
            this.selectedFiles = Array.from(e.dataTransfer.files);
            this.renderFiles();
        });
    }

    renderFiles() {
        const listEl = document.getElementById('file-list');
        const btn = document.getElementById('btn-upload');

        if (this.selectedFiles.length === 0) {
            listEl.innerHTML = '';
            btn.disabled = true;
            return;
        }

        listEl.innerHTML = this.selectedFiles.map(f => `
            <div class="file-item">
                <span>${f.name}</span>
                <span>${this.formatBytes(f.size)}</span>
            </div>
        `).join('');

        btn.disabled = false;
    }

    setupButtons() {
        document.getElementById('btn-refresh').addEventListener('click', () => this.loadStatus());
        document.getElementById('btn-upload').addEventListener('click', () => this.upload());
        document.getElementById('btn-clear').addEventListener('click', () => this.clear());
        document.getElementById('btn-ingest').addEventListener('click', () => this.ingest());
        document.getElementById('btn-search').addEventListener('click', () => this.search());
        
        document.getElementById('search-input').addEventListener('keypress', (e) => {
            if (e.key === 'Enter') this.search();
        });
    }

    async upload() {
        const formData = new FormData();
        this.selectedFiles.forEach(f => formData.append('files[]', f));

        const btn = document.getElementById('btn-upload');
        btn.disabled = true;
        btn.textContent = 'Uploading...';

        try {
            const res = await fetch(`${API_URL}/api/upload`, {
                method: 'POST',
                body: formData
            });
            const data = await res.json();

            this.log(`Uploaded ${data.count} files`);
            this.selectedFiles = [];
            this.renderFiles();
        } catch (err) {
            this.log(`Error: ${err.message}`);
        } finally {
            btn.disabled = false;
            btn.textContent = 'Upload';
        }
    }

    async clear() {
        if (!confirm('Clear all uploaded files?')) return;

        try {
            const res = await fetch(`${API_URL}/api/clear-uploads`, { method: 'POST' });
            const data = await res.json();
            this.log(`Cleared ${data.deleted} files`);
        } catch (err) {
            this.log(`Error: ${err.message}`);
        }
    }

    async ingest() {
        const recreate = document.getElementById('recreate-index').checked;
        const btn = document.getElementById('btn-ingest');
        const logEl = document.getElementById('log');

        logEl.classList.add('active');
        logEl.innerHTML = '';

        btn.disabled = true;
        btn.textContent = 'Ingesting...';

        this.log('Starting ingestion...');

        try {
            const res = await fetch(`${API_URL}/api/ingest`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ recreate })
            });
            const data = await res.json();

            if (data.success) {
                this.log('Complete');
                this.log(`Indexed: ${data.indexed} chunks`);
                this.log(`Total: ${data.total_documents} documents`);
                this.loadStatus();
            } else {
                this.log(`Error: ${data.error}`);
            }
        } catch (err) {
            this.log(`Error: ${err.message}`);
        } finally {
            btn.disabled = false;
            btn.textContent = 'Start Ingestion';
        }
    }

    async search() {
        const query = document.getElementById('search-input').value.trim();
        const topK = parseInt(document.getElementById('top-k').value);
        const resultsEl = document.getElementById('search-results');

        if (!query) return;

        resultsEl.innerHTML = '<p>Searching...</p>';

        try {
            const res = await fetch(`${API_URL}/api/search`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ query, top_k: topK })
            });
            const data = await res.json();

            if (data.results.length === 0) {
                resultsEl.innerHTML = '<div class="card">No results</div>';
                return;
            }

            resultsEl.innerHTML = data.results.map(r => `
                <div class="result">
                    <div class="result-score">Score: ${r.score.toFixed(3)}</div>
                    <div class="result-meta">${r.metadata.file_name} | ${r.metadata.source_type}</div>
                    <div class="result-content">${this.escapeHtml(r.content)}</div>
                </div>
            `).join('');
        } catch (err) {
            resultsEl.innerHTML = `<div class="card">Error: ${err.message}</div>`;
        }
    }

    log(msg) {
        const logEl = document.getElementById('log');
        const time = new Date().toLocaleTimeString();
        logEl.innerHTML += `[${time}] ${msg}\n`;
        logEl.scrollTop = logEl.scrollHeight;
    }

    formatBytes(bytes) {
        if (bytes === 0) return '0 B';
        const k = 1024;
        const sizes = ['B', 'KB', 'MB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i];
    }

    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
}

new App();
# DocVector Helm Charts

Kubernetes deployment chart for DocVector (API + Frontend + OpenSearch integration).

## Add Repository
```bash
helm repo add docvector https://iwebbo.github.io/DocVector/
helm repo update
```

## Install Chart
```bash
helm upgrade --install docvector docvector/docvector \
  --namespace docvector \
  --create-namespace \
  -f values.yaml \
  -f ingress.yaml
  ```

## Default Values (values.yaml)
```yaml
# Default values for DocVector Helm chart
replicaCount:
  api: 2
  nginx: 2

image:
  api:
    repository: ghcr.io/iwebbo/docvector/api
    tag: "latest"
    pullPolicy: Always
  nginx:
    repository: ghcr.io/iwebbo/docvector/frontend
    tag: "latest"
    pullPolicy: Always

imagePullSecrets: []

namespace:
  create: true
  name: docvector

opensearch:
  host: "opensearch.opensearch.svc.cluster.local"
  port: "9200"
  user: "admin"
  password: "ChangeMe123!"
  useSSL: "true"
  verifyCerts: "false"
  indexName: "knowledge_base"

persistence:
  enabled: true
  storageClass: "standard"
  accessMode: ReadWriteOnce
  size: 10Gi

api:
  resources:
    requests:
      memory: "1Gi"
      cpu: "500m"
    limits:
      memory: "2Gi"
      cpu: "1000m"

nginx:
  resources:
    requests:
      memory: "128Mi"
      cpu: "100m"
    limits:
      memory: "256Mi"
      cpu: "200m"
  clientMaxBodySize: "100m"

service:
  api:
    type: ClusterIP
    port: 8000
  nginx:
    type: ClusterIP
    port: 80

autoscaling:
  enabled: false
  minReplicas: 2
  maxReplicas: 10
  targetCPUUtilizationPercentage: 70
  targetMemoryUtilizationPercentage: 80
  ```

## Ingress Configuration (ingress.yaml)
```yaml
ingress:
  enabled: true
  className: "nginx"
  annotations:
    nginx.ingress.kubernetes.io/proxy-body-size: "100m"
    nginx.ingress.kubernetes.io/proxy-read-timeout: "120"
    nginx.ingress.kubernetes.io/proxy-send-timeout: "120"
    # cert-manager.io/cluster-issuer: "letsencrypt-prod"
  hosts:
    - host: docvector.local
      paths:
        - path: /
          pathType: Prefix
  tls: []
  # - secretName: docvector-tls
  #   hosts:
  #     - docvector.your-domain.com
  ```

## Prerequisites

- Kubernetes 1.20+
- Helm 3.0+
- Ingress Controller (nginx-ingress recommended)
- OpenSearch cluster (external or in-cluster)

## Configuration Files (at repo root)

- `values.yaml` - Helm values (mandatory)
- `ingress.yaml` - Ingress configuration (mandatory)

## Quick Start

### 1. Clone and configure
```bash
git clone https://github.com/iwebbo/DocVector.git
cd DocVector

# Edit OpenSearch connection
vim values.yaml

# Edit domain
vim ingress.yaml
```

### 2. Install
```bash
helm install docvector docvector/docvector \
  -n docvector \
  --create-namespace \
  -f values.yaml \
  -f ingress.yaml
```

### 3. Verify
```bash
kubectl get pods -n docvector
kubectl get ingress -n docvector
```

## Deploy with Ansible (Generic Pipeline)
```bash
ansible-playbook deploy_helm_generic.yml

# Using: https://github.com/iwebbo/Ansible/tree/main/roles/deploy_helmchart_stack_standalone
```

## Chart Values

| Parameter | Description | Default |
|-----------|-------------|---------|
| `replicaCount.api` | API replicas | 2 |
| `replicaCount.nginx` | Frontend replicas | 2 |
| `image.api.tag` | API image tag | latest |
| `image.nginx.tag` | Frontend image tag | latest |
| `opensearch.host` | OpenSearch host | opensearch.opensearch.svc.cluster.local |
| `persistence.size` | Data volume size | 10Gi |
| `ingress.enabled` | Enable Ingress | true |

## Build & Push Flow

1. Push to `api/**` or `src/**` → GitHub Actions builds API image
2. Push to `front/**` → GitHub Actions builds frontend image
3. Push to `charts/**` → GitHub Actions packages and publishes chart

## Upgrade
```bash
helm upgrade docvector docvector/docvector \
  -n docvector \
  -f values.yaml \
  -f ingress.yaml
```

## Uninstall
```bash
helm uninstall docvector -n docvector
kubectl delete namespace docvector
```

## Storage Class Options

### Auto-provisioning (Default)
```yaml
persistence:
  storageClass: "standard"  # or "gp2" on AWS, "managed-premium" on Azure
```

### Manual PV (for on-premise)
```yaml
# values.yaml
persistence:
  storageClass: "local-storage"
```
```yaml
# pv-data.yaml
apiVersion: v1
kind: PersistentVolume
metadata:
  name: docvector-data-pv
spec:
  storageClassName: local-storage
  capacity:
    storage: 10Gi
  accessModes:
    - ReadWriteOnce
  persistentVolumeReclaimPolicy: Retain
  hostPath:
    path: "/mnt/data/docvector"
    type: DirectoryOrCreate
  nodeAffinity:
    required:
      nodeSelectorTerms:
      - matchExpressions:
        - key: kubernetes.io/hostname
          operator: In
          values:
          - k8s-worker-01
  ```
```bash
kubectl apply -f pv-data.yaml
helm install docvector docvector/docvector -f values.yaml -f ingress.yaml
```

## Troubleshooting
```bash
# Check pods
kubectl get pods -n docvector

# Check logs
kubectl logs -f -n docvector deployment/docvector-api
kubectl logs -f -n docvector deployment/docvector-nginx

# Check OpenSearch connection
kubectl exec -it -n docvector deployment/docvector-api -- curl -k https://opensearch:9200

# Port-forward for local testing
kubectl port-forward -n docvector svc/docvector-nginx 8080:80
```

## Support

Repository: https://github.com/iwebbo/DocVector

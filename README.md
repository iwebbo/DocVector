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
  -f ingress.yaml
  ```

## Default Values (values.yaml)
```yaml

opensearch:
  host: "opensearch.opensearch.svc.cluster.local"
  port: "9200"
  user: "admin"
  password: "ChangeMe123!"
  useSSL: "true"
  verifyCerts: "false"
  indexName: "knowledge_base"

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

- `values.yaml` - Helm values (default)
- `ingress.yaml` - Ingress configuration (mandatory)

```

## Support

Repository: https://github.com/iwebbo/DocVector

# Deployment Guide

This guide covers different deployment options for the PDF Q&A System.

## Table of Contents
1. [Local Development](#local-development)
2. [Docker Deployment](#docker-deployment)
3. [Google Cloud Run](#google-cloud-run)
4. [Azure Container Apps](#azure-container-apps)
5. [Production Considerations](#production-considerations)

---

## Local Development

### Quick Start (Bash/Linux/macOS)
```bash
chmod +x setup.sh
./setup.sh
```

### Manual Setup
```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Setup environment
cp .env.example .env
# Edit .env and add your OPENAI_API_KEY

# Run the app
streamlit run src/app.py
```

---

## Docker Deployment

### Build and Run with Docker
```bash
# Build the image
docker build -t pdf-qa-system .

# Run the container
docker run -p 8501:8501 \
  -e OPENAI_API_KEY=your-api-key \
  -v pdf-qa-data:/app/data/chroma_db \
  pdf-qa-system
```

### Using Docker Compose (Recommended)
```bash
# Create .env file with your API key
echo "OPENAI_API_KEY=your-api-key" > .env

# Start the application
docker-compose up -d

# View logs
docker-compose logs -f

# Stop the application
docker-compose down
```

---

## Google Cloud Run

### Prerequisites
- Google Cloud account
- `gcloud` CLI installed
- Project with billing enabled

### Step 1: Build and Push to Container Registry
```bash
# Set your project ID
PROJECT_ID="your-project-id"
IMAGE_NAME="pdf-qa-system"

# Build for Cloud Run (multi-platform)
docker build --platform linux/amd64 -t gcr.io/${PROJECT_ID}/${IMAGE_NAME} .

# Push to Google Container Registry
docker push gcr.io/${PROJECT_ID}/${IMAGE_NAME}
```

### Step 2: Deploy to Cloud Run
```bash
# Deploy
gcloud run deploy pdf-qa-system \
  --image gcr.io/${PROJECT_ID}/${IMAGE_NAME} \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars OPENAI_API_KEY=your-api-key \
  --memory 2Gi \
  --cpu 2 \
  --timeout 300

# Get the service URL
gcloud run services describe pdf-qa-system --region us-central1 --format 'value(status.url)'
```

### Step 3: Add Persistent Storage (Optional)
For persistent ChromaDB storage across container restarts:

```bash
# Create a Cloud Storage bucket
gsutil mb gs://${PROJECT_ID}-pdf-qa-data

# Deploy with Cloud Storage mount
gcloud run deploy pdf-qa-system \
  --image gcr.io/${PROJECT_ID}/${IMAGE_NAME} \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars OPENAI_API_KEY=your-api-key,CHROMA_PERSIST_DIRECTORY=/mnt/chroma \
  --memory 2Gi \
  --execution-environment gen2 \
  --cpu 2
```

---

## Azure Container Apps

### Prerequisites
- Azure account
- Azure CLI installed
- Resource group created

### Step 1: Create Container Registry
```bash
# Variables
RESOURCE_GROUP="pdf-qa-rg"
LOCATION="eastus"
ACR_NAME="pdfqaacr"
APP_NAME="pdf-qa-system"

# Create Container Registry
az acr create \
  --resource-group $RESOURCE_GROUP \
  --name $ACR_NAME \
  --sku Basic

# Enable admin access
az acr update -n $ACR_NAME --admin-enabled true
```

### Step 2: Build and Push Image
```bash
# Login to ACR
az acr login --name $ACR_NAME

# Build and push
docker build -t ${ACR_NAME}.azurecr.io/pdf-qa-system:latest .
docker push ${ACR_NAME}.azurecr.io/pdf-qa-system:latest
```

### Step 3: Deploy to Container Apps
```bash
# Create Container Apps environment
az containerapp env create \
  --name pdf-qa-env \
  --resource-group $RESOURCE_GROUP \
  --location $LOCATION

# Deploy the app
az containerapp create \
  --name $APP_NAME \
  --resource-group $RESOURCE_GROUP \
  --environment pdf-qa-env \
  --image ${ACR_NAME}.azurecr.io/pdf-qa-system:latest \
  --target-port 8501 \
  --ingress external \
  --env-vars OPENAI_API_KEY=your-api-key \
  --cpu 2 \
  --memory 4Gi
```

---

## Production Considerations

### 1. Security
- **API Key Management**: Use secret managers (GCP Secret Manager, Azure Key Vault)
- **Authentication**: Add user authentication (OAuth, JWT)
- **Network Security**: Use VPC/VNet for database connections
- **Rate Limiting**: Implement rate limiting to prevent abuse

### 2. Performance
- **Caching**: Cache embeddings and frequently asked questions
- **Load Balancing**: Use multiple instances behind a load balancer
- **CDN**: Serve static assets through a CDN
- **Database Optimization**: Use managed vector databases for production

### 3. Monitoring
- **Logging**: Structured logging with levels
- **Metrics**: Track query latency, error rates, token usage
- **Alerting**: Set up alerts for errors and performance degradation
- **Tracing**: Use LangSmith for detailed LLM tracing

### 4. Cost Optimization
- **Model Selection**: Use smaller models when appropriate
- **Caching**: Cache LLM responses for repeated queries
- **Auto-scaling**: Scale down during low traffic periods
- **Token Limits**: Set max token limits per query

### Example Production Environment Variables
```bash
# Production .env
OPENAI_API_KEY=sk-prod-key
LANGCHAIN_TRACING_V2=true
LANGCHAIN_API_KEY=ls-prod-key

# Use cost-effective models
EMBEDDING_MODEL=text-embedding-3-small
LLM_MODEL=gpt-3.5-turbo

# Optimize chunks for cost
CHUNK_SIZE=800
CHUNK_OVERLAP=150

# Production database
CHROMA_PERSIST_DIRECTORY=/mnt/persistent-storage/chroma_db
```

---

## Scaling Strategies

### Horizontal Scaling
- Run multiple instances behind a load balancer
- Use a shared vector database (Pinecone, Weaviate)
- Implement session management for multi-instance deployments

### Vertical Scaling
- Increase memory for larger document sets
- Add more CPU cores for concurrent requests
- Use GPU instances for faster embedding generation

### Database Scaling
- For production, consider migrating to:
  - **Pinecone**: Fully managed, serverless
  - **Weaviate**: Self-hosted, feature-rich
  - **Qdrant**: High performance, cloud-native

---

## Troubleshooting Production Issues

### High Memory Usage
- Reduce `CHUNK_SIZE` to decrease memory footprint
- Limit number of retrieved documents (`k` parameter)
- Implement pagination for large result sets

### Slow Query Performance
- Add caching layer (Redis) for frequent queries
- Optimize chunk size and overlap
- Use smaller embedding model
- Implement query preprocessing to filter obvious non-matches

### Container Crashes
- Check memory limits (increase if needed)
- Review error logs for out-of-memory errors
- Implement graceful error handling
- Add health checks and automatic restart policies

---

## Next Steps

After deploying to production:
1. Set up monitoring and alerting
2. Implement user authentication
3. Add rate limiting and quotas
4. Create backup strategy for ChromaDB
5. Set up CI/CD pipeline for automated deployments
6. Implement A/B testing for prompt optimization
7. Add analytics to track usage patterns

For questions or issues, refer to the main README.md or open an issue on GitHub.

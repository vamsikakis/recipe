# Deployment Guide - ITC Yippee Recipe Generator

This guide provides step-by-step instructions for deploying the AI-Powered Personalized Recipe Generator to Microsoft Azure.

## Prerequisites

- Azure subscription with appropriate permissions
- Azure CLI installed and configured
- Git repository with the project code
- Azure DevOps organization (for CI/CD pipelines)

## 1. Azure Resource Setup

### 1.1 Deploy Infrastructure

1. **Clone the repository and navigate to infrastructure folder:**
   ```bash
   cd infrastructure
   ```

2. **Deploy the ARM template:**
   ```bash
   az deployment group create \
     --resource-group yippee-recipe-generator-rg \
     --template-file azure-infrastructure.json \
     --parameters location=EastUS
   ```

3. **Note the output values** for the next steps:
   - Backend App URL
   - Frontend App URL
   - Cosmos DB Connection String
   - AI Services Endpoint
   - Key Vault URI
   - Application Insights Connection String

### 1.2 Configure Azure OpenAI Service

1. **Create Azure OpenAI Service resource** (if not already created):
   ```bash
   az cognitiveservices account create \
     --name yippee-openai \
     --resource-group yippee-recipe-generator-rg \
     --kind OpenAI \
     --sku S0 \
     --location EastUS
   ```

2. **Deploy GPT-3.5 Turbo model:**
   ```bash
   az cognitiveservices account deployment create \
     --resource-group yippee-recipe-generator-rg \
     --name yippee-openai \
     --deployment-name gpt-35-turbo \
     --model-name gpt-35-turbo \
     --model-version 0613 \
     --model-format OpenAI
   ```

3. **Deploy DALL-E 3 model:**
   ```bash
   az cognitiveservices account deployment create \
     --resource-group yippee-recipe-generator-rg \
     --name yippee-openai \
     --deployment-name dall-e-3 \
     --model-name dall-e-3 \
     --model-version 1106 \
     --model-format OpenAI
   ```

### 1.3 Configure Key Vault Secrets

1. **Store sensitive configuration in Key Vault:**
   ```bash
   # Cosmos DB Connection String
   az keyvault secret set \
     --vault-name yippee-key-vault \
     --name cosmos-db-connection-string \
     --value "your-cosmos-db-connection-string"

   # Azure AI Language Key
   az keyvault secret set \
     --vault-name yippee-key-vault \
     --name azure-language-key \
     --value "your-language-key"

   # Azure OpenAI Key
   az keyvault secret set \
     --vault-name yippee-key-vault \
     --name azure-openai-key \
     --value "your-openai-key"
   ```

## 2. Backend Deployment

### 2.1 Local Development Setup

1. **Navigate to backend directory:**
   ```bash
   cd backend
   ```

2. **Create virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Create .env file:**
   ```bash
   cp env.example .env
   # Edit .env with your actual values
   ```

5. **Run locally:**
   ```bash
   uvicorn main:app --reload
   ```

### 2.2 Azure App Service Deployment

1. **Configure Azure DevOps Pipeline:**
   - Create a new pipeline in Azure DevOps
   - Use the `azure-pipelines-backend.yml` file
   - Configure the following variables:
     - `COSMOS_DB_CONNECTION_STRING`
     - `AZURE_LANGUAGE_ENDPOINT`
     - `AZURE_LANGUAGE_KEY`
     - `AZURE_OPENAI_ENDPOINT`
     - `AZURE_OPENAI_KEY`
     - `AZURE_OPENAI_DEPLOYMENT_NAME`
     - `AZURE_OPENAI_DALLE_DEPLOYMENT_NAME`
     - `APPLICATIONINSIGHTS_CONNECTION_STRING`

2. **Deploy using Azure CLI:**
   ```bash
   az webapp deployment source config-zip \
     --resource-group yippee-recipe-generator-rg \
     --name yippee-backend-api \
     --src backend.zip
   ```

## 3. Frontend Deployment

### 3.1 Local Development Setup

1. **Navigate to frontend directory:**
   ```bash
   cd frontend
   ```

2. **Install dependencies:**
   ```bash
   npm install
   ```

3. **Create environment file:**
   ```bash
   # Create .env.local file
   echo "REACT_APP_API_URL=http://localhost:8000" > .env.local
   ```

4. **Run locally:**
   ```bash
   npm start
   ```

### 3.2 Azure Static Web Apps Deployment

1. **Configure Azure DevOps Pipeline:**
   - Create a new pipeline in Azure DevOps
   - Use the `azure-pipelines-frontend.yml` file
   - Configure the following variables:
     - `AZURE_STATIC_WEB_APPS_API_TOKEN`
     - `BACKEND_API_URL`

2. **Deploy using Azure CLI:**
   ```bash
   az staticwebapp create \
     --name yippee-frontend \
     --resource-group yippee-recipe-generator-rg \
     --source https://github.com/your-org/yippee-recipe-generator \
     --location EastUS \
     --branch main \
     --app-location frontend \
     --output-location build
   ```

## 4. Database Setup

### 4.1 Seed Initial Data

1. **Create base recipes in Cosmos DB:**
   ```bash
   # Use Azure Data Explorer or Cosmos DB Data Explorer
   # Insert sample recipes into the 'recipes' container
   ```

2. **Sample recipe document:**
   ```json
   {
     "id": "base-1",
     "title": "Classic Yippee Masala",
     "cuisine": "Indian",
     "difficulty": "Easy",
     "cooking_time": 15,
     "tags": ["quick", "vegetarian", "indian"],
     "ingredients": ["Yippee noodles", "onions", "tomatoes", "spices"],
     "type": "base_recipe"
   }
   ```

## 5. Monitoring and Logging

### 5.1 Application Insights Setup

1. **Configure Application Insights:**
   - The Application Insights resource is already created
   - Connection string is available in the ARM template outputs
   - Backend automatically sends telemetry data

2. **Set up monitoring dashboards:**
   - Create custom dashboards in Azure Monitor
   - Monitor API response times, error rates, and user interactions

### 5.2 Health Checks

1. **Backend health check:**
   ```bash
   curl https://yippee-backend-api.azurewebsites.net/health
   ```

2. **Frontend health check:**
   ```bash
   curl https://yippee-frontend.azurestaticapps.net
   ```

## 6. Security Configuration

### 6.1 Network Security

1. **Configure CORS in backend:**
   - Update CORS settings in `main.py` for production domains
   - Remove wildcard (*) origins for production

2. **Set up Azure API Management (Optional):**
   ```bash
   az apim create \
     --name yippee-api-gateway \
     --resource-group yippee-recipe-generator-rg \
     --publisher-email your-email@domain.com \
     --publisher-name "ITC Yippee"
   ```

### 6.2 Authentication (Future Enhancement)

1. **Azure Active Directory integration:**
   - Configure Azure AD app registration
   - Implement JWT token validation
   - Add user authentication to the application

## 7. Testing

### 7.1 API Testing

1. **Test recipe generation:**
   ```bash
   curl -X POST https://yippee-backend-api.azurewebsites.net/api/generate-recipe \
     -H "Content-Type: application/json" \
     -d '{
       "preferences": {
         "cuisine": "Indian",
         "spice_level": "Medium",
         "meal_type": ["Lunch"],
         "max_cooking_time": "30 mins",
         "dietary_restrictions": [],
         "available_ingredients": ["chicken", "onions", "tomatoes"]
       }
     }'
   ```

### 7.2 Frontend Testing

1. **Access the application:**
   - Open https://yippee-frontend.azurestaticapps.net
   - Test the recipe generation flow
   - Verify all form validations work correctly

## 8. Troubleshooting

### 8.1 Common Issues

1. **Backend deployment fails:**
   - Check Python version compatibility
   - Verify all environment variables are set
   - Check Application Insights for error logs

2. **Frontend build fails:**
   - Ensure Node.js version is 18.x or higher
   - Check for missing dependencies
   - Verify API URL configuration

3. **Database connection issues:**
   - Verify Cosmos DB connection string
   - Check network connectivity
   - Ensure containers are created

### 8.2 Logs and Debugging

1. **Backend logs:**
   ```bash
   az webapp log tail --name yippee-backend-api --resource-group yippee-recipe-generator-rg
   ```

2. **Application Insights:**
   - Use Azure Portal to view live metrics
   - Check for failed requests and exceptions
   - Monitor performance metrics

## 9. Scaling and Optimization

### 9.1 Performance Optimization

1. **Enable Redis caching:**
   - Add Azure Cache for Redis
   - Configure user profile caching
   - Cache frequently accessed recipes

2. **CDN configuration:**
   - Set up Azure CDN for static assets
   - Configure image optimization
   - Enable compression

### 9.2 Auto-scaling

1. **Configure App Service scaling:**
   - Set up auto-scaling rules
   - Monitor CPU and memory usage
   - Configure scale-out triggers

## 10. Maintenance

### 10.1 Regular Tasks

1. **Security updates:**
   - Keep dependencies updated
   - Monitor security advisories
   - Apply patches regularly

2. **Backup and recovery:**
   - Set up automated backups for Cosmos DB
   - Test disaster recovery procedures
   - Document recovery processes

### 10.2 Monitoring

1. **Set up alerts:**
   - Configure Azure Monitor alerts
   - Set up email notifications
   - Monitor cost and usage

This deployment guide provides a comprehensive approach to deploying the ITC Yippee Recipe Generator on Azure. Follow each section carefully and ensure all prerequisites are met before proceeding. 
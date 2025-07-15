# ITC Yippee AI-Powered Personalized Recipe Generator

## Overview

This project implements an AI-Powered Personalized Recipe Generator designed to enhance ITC Yippee!'s brand value and consumer engagement. The system leverages Microsoft Azure's AI services to create dynamic, real-time recipe customization based on user preferences, dietary needs, and available ingredients.

## Architecture

The system follows a modern, cloud-native architecture hosted on Microsoft Azure:

- **Frontend**: React.js with Tailwind CSS
- **Backend**: Python FastAPI
- **Database**: Azure Cosmos DB
- **AI Services**: Azure AI Language, Azure OpenAI Service
- **Deployment**: Azure App Service, Azure Static Web Apps
- **CI/CD**: Azure Pipelines

## Project Structure

```
recipe/
├── frontend/                 # React frontend application
├── backend/                  # Python FastAPI backend
├── infrastructure/           # Azure ARM templates and deployment scripts
├── docs/                     # Documentation
└── README.md                 # This file
```

## Quick Start

### Prerequisites

- Node.js 18+ and npm
- Python 3.9+
- Azure CLI
- Azure subscription

### Local Development

1. **Backend Setup**:
   ```bash
   cd backend
   pip install -r requirements.txt
   uvicorn main:app --reload
   ```

2. **Frontend Setup**:
   ```bash
   cd frontend
   npm install
   npm start
   ```

### Azure Deployment

1. Deploy infrastructure:
   ```bash
   cd infrastructure
   az deployment group create --resource-group <rg-name> --template-file azure-infrastructure.json
   ```

2. Deploy applications using the provided CI/CD pipelines.

## Features

- **Personalized Recipe Generation**: AI-powered recipe creation based on user preferences
- **Natural Language Processing**: Entity extraction from user input
- **Image Generation**: DALL-E 3 powered recipe visuals
- **Recommendation Engine**: Rule-based recipe suggestions
- **User Profile Management**: Save and manage favorite recipes
- **Responsive Design**: Works across desktop, tablet, and mobile

## Technology Stack

- **Frontend**: React.js, Tailwind CSS, Axios
- **Backend**: Python, FastAPI, Azure SDK
- **Database**: Azure Cosmos DB
- **AI Services**: Azure AI Language, Azure OpenAI Service
- **Deployment**: Azure App Service, Azure Static Web Apps
- **Monitoring**: Azure Application Insights

## Contributing

Please refer to the development brief for detailed implementation guidelines and Cursor IDE prompts.

## License

Proprietary - ITC Limited 
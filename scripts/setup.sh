#!/bin/bash

# ITC Yippee Recipe Generator - Local Development Setup Script

set -e

echo "🚀 Setting up ITC Yippee Recipe Generator development environment..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if required tools are installed
check_requirements() {
    print_status "Checking system requirements..."
    
    # Check Python
    if ! command -v python3 &> /dev/null; then
        print_error "Python 3.9+ is required but not installed."
        exit 1
    fi
    
    # Check Node.js
    if ! command -v node &> /dev/null; then
        print_error "Node.js 18+ is required but not installed."
        exit 1
    fi
    
    # Check npm
    if ! command -v npm &> /dev/null; then
        print_error "npm is required but not installed."
        exit 1
    fi
    
    print_success "All requirements are met!"
}

# Setup backend
setup_backend() {
    print_status "Setting up backend..."
    
    cd backend
    
    # Create virtual environment
    if [ ! -d "venv" ]; then
        print_status "Creating Python virtual environment..."
        python3 -m venv venv
    fi
    
    # Activate virtual environment
    print_status "Activating virtual environment..."
    source venv/bin/activate
    
    # Install dependencies
    print_status "Installing Python dependencies..."
    pip install --upgrade pip
    pip install -r requirements.txt
    
    # Create .env file if it doesn't exist
    if [ ! -f ".env" ]; then
        print_status "Creating .env file..."
        cp env.example .env
        print_warning "Please update .env file with your actual configuration values."
    fi
    
    cd ..
    print_success "Backend setup completed!"
}

# Setup frontend
setup_frontend() {
    print_status "Setting up frontend..."
    
    cd frontend
    
    # Install dependencies
    print_status "Installing Node.js dependencies..."
    npm install
    
    # Create .env.local file if it doesn't exist
    if [ ! -f ".env.local" ]; then
        print_status "Creating .env.local file..."
        echo "REACT_APP_API_URL=http://localhost:8000" > .env.local
    fi
    
    cd ..
    print_success "Frontend setup completed!"
}

# Create necessary directories
create_directories() {
    print_status "Creating necessary directories..."
    
    mkdir -p logs
    mkdir -p docs
    mkdir -p scripts
    
    print_success "Directories created!"
}

# Main setup function
main() {
    echo "=========================================="
    echo "  ITC Yippee Recipe Generator Setup"
    echo "=========================================="
    echo ""
    
    # Check requirements
    check_requirements
    
    # Create directories
    create_directories
    
    # Setup backend
    setup_backend
    
    # Setup frontend
    setup_frontend
    
    echo ""
    echo "=========================================="
    print_success "Setup completed successfully!"
    echo "=========================================="
    echo ""
    echo "Next steps:"
    echo "1. Update backend/.env with your Azure service credentials"
    echo "2. Start the backend: cd backend && source venv/bin/activate && uvicorn main:app --reload"
    echo "3. Start the frontend: cd frontend && npm start"
    echo "4. Open http://localhost:3000 in your browser"
    echo ""
    echo "For deployment instructions, see docs/DEPLOYMENT.md"
    echo ""
}

# Run main function
main "$@" 
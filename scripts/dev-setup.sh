#!/bin/bash
set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}"
cat << "EOF"
   ___             ____
  / _ \ _ __  ___ / ___|  __ _  __ _  ___
 | | | | '_ \/ __| |  _  / _` |/ _` |/ _ \
 | |_| | |_) \__ \ |_| || (_| | (_| |  __/
  \___/| .__/|___/\____(_)__,_|\__, |\___|
       |_|                     |___/
  Development Environment Setup
EOF
echo -e "${NC}"

echo -e "${GREEN}=== OpsSage Development Environment Setup ===${NC}\n"

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to print step
print_step() {
    echo -e "${BLUE}==>${NC} $1"
}

# Function to print success
print_success() {
    echo -e "${GREEN}✓${NC} $1"
}

# Function to print warning
print_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

# Function to print error
print_error() {
    echo -e "${RED}✗${NC} $1"
}

# Check prerequisites
print_step "Checking prerequisites..."

MISSING_DEPS=()

if ! command_exists docker; then
    MISSING_DEPS+=("docker")
fi

if ! command_exists docker-compose; then
    if ! docker compose version &>/dev/null; then
        MISSING_DEPS+=("docker-compose")
    fi
fi

if ! command_exists python3; then
    MISSING_DEPS+=("python3")
fi

if ! command_exists node; then
    MISSING_DEPS+=("node")
fi

if ! command_exists npm; then
    MISSING_DEPS+=("npm")
fi

if [ ${#MISSING_DEPS[@]} -ne 0 ]; then
    print_error "Missing required dependencies: ${MISSING_DEPS[*]}"
    echo ""
    echo "Please install the missing dependencies:"
    echo "  - Docker: https://docs.docker.com/get-docker/"
    echo "  - Docker Compose: https://docs.docker.com/compose/install/"
    echo "  - Python 3: https://www.python.org/downloads/"
    echo "  - Node.js: https://nodejs.org/"
    exit 1
fi

print_success "All prerequisites installed"

# Optional: Check for Kind and kubectl
print_step "Checking optional tools..."

if ! command_exists kind; then
    print_warning "kind not installed (optional for Kubernetes testing)"
    echo "  Install from: https://kind.sigs.k8s.io/docs/user/quick-start/"
else
    print_success "kind installed: $(kind --version)"
fi

if ! command_exists kubectl; then
    print_warning "kubectl not installed (optional for Kubernetes testing)"
    echo "  Install from: https://kubernetes.io/docs/tasks/tools/"
else
    print_success "kubectl installed: $(kubectl version --client --short 2>/dev/null || kubectl version --client)"
fi

# Check if uv is installed
if ! command_exists uv; then
    print_warning "uv not installed, installing..."
    pip install uv
    print_success "uv installed"
fi

# Setup Python environment
print_step "Setting up Python environment..."

if [ ! -d ".venv" ]; then
    uv venv
    print_success "Virtual environment created"
else
    print_success "Virtual environment already exists"
fi

# Activate virtual environment
source .venv/bin/activate

# Install Python dependencies
print_step "Installing Python dependencies..."
uv pip install -r pyproject.toml
print_success "Python dependencies installed"

# Setup Dashboard
print_step "Setting up Dashboard..."

cd dashboard

if [ ! -d "node_modules" ]; then
    npm install
    print_success "Dashboard dependencies installed"
else
    print_success "Dashboard dependencies already installed"
fi

cd ..

# Setup environment file
print_step "Setting up environment configuration..."

if [ ! -f ".env" ]; then
    cp env.example .env
    print_warning ".env file created from env.example"
    echo "  Please edit .env and add your Google Cloud credentials"
else
    print_success ".env file already exists"
fi

# Create credentials directory
mkdir -p credentials
if [ ! -f "credentials/credentials.json" ] && [ ! -f "credentials.json" ]; then
    print_warning "Google Cloud credentials not found"
    echo "  Please add your credentials.json file to the project root or credentials/ directory"
fi

# Create data directories
print_step "Creating data directories..."
mkdir -p data/chromadb
print_success "Data directories created"

# Make scripts executable
print_step "Making scripts executable..."
chmod +x scripts/*.sh
print_success "Scripts are now executable"

echo ""
echo -e "${GREEN}=== Setup Complete ===${NC}\n"
echo "You can now run OpsSage in different modes:"
echo ""
echo -e "${BLUE}1. Docker Compose (Recommended for local development):${NC}"
echo "   docker-compose up -d"
echo "   Access: http://localhost:8000 (backend), http://localhost:3000 (dashboard)"
echo ""
echo -e "${BLUE}2. Local Development (Backend only):${NC}"
echo "   source .venv/bin/activate"
echo "   uvicorn apis.main:app --reload"
echo ""
echo -e "${BLUE}3. Dashboard Development:${NC}"
echo "   cd dashboard"
echo "   npm run dev"
echo ""
echo -e "${BLUE}4. Kubernetes with Kind (Multi-node testing):${NC}"
echo "   ./scripts/kind-setup.sh      # Create cluster"
echo "   ./scripts/kind-deploy.sh     # Deploy OpsSage"
echo "   ./scripts/kind-teardown.sh   # Cleanup"
echo ""
echo -e "${YELLOW}Next steps:${NC}"
echo "  1. Add your Google Cloud credentials"
echo "  2. Start services: docker-compose up -d"
echo "  3. Open dashboard: http://localhost:3000"
echo "  4. Check API docs: http://localhost:8000/docs"
echo ""

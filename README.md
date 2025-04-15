# MyPetParlor App AI Agents Platform

This monorepo contains the MyPetParlor App AI Agents platform, implementing a multi-agent system using both Azure AI Agent Service and Semantic Kernel approaches.

## Quick Start

The project uses Make commands to simplify development workflows. To see all available commands:
```bash
cd mypetparlorapp
make help
```

Common commands:
```bash
make setup      # Setup development environment
make dev        # Start development environment
make test      # Run all tests
make clean     # Clean up development environment
```

## Project Structure

- `.github/`: GitHub Actions workflows for CI/CD
- `apps/`: Application code (frontend and backend)
- `agents/`: AI Agents implementations
  - `azure/`: Azure AI Agent Service implementations
  - `semantic-kernel/`: Semantic Kernel implementations
- `common/`: Shared code and utilities
  - `mcp/`: MCP server for MyBusiness App API
- `infrastructure/`: Infrastructure as Code (Azure Bicep)
- `tests/`: Test suites
- `docker/`: Docker configuration files
  - `compose/`: Docker Compose files
  - `frontend/`: Frontend Dockerfile
  - `backend/`: Backend Dockerfile
  - `mcp-server/`: MCP Server Dockerfile

## Key Features

- Chainlit-based chatbot UI
- LangChain/LangGraph backend
- Multiple AI agent implementations:
  - Azure AI Agent Service
  - Semantic Kernel orchestration
- Smart Scheduling AI agent (primary focus)
- Human-in-the-loop support
- Agent evaluation framework
- MCP server integration

## Prerequisites

- Python 3.13+
- Docker
- Azure CLI
- Azure subscription

Check prerequisites with:
```bash
cd mypetparlorapp
make check-prereqs
```

## Environment Setup

1. Setup the development environment:
```bash
make setup
```
This will:
- Check prerequisites
- Create a Python virtual environment
- Install dependencies
- Create necessary directories
- Create a .env file from template

2. Configure your environment variables by editing the `.env` file:
```bash
make configure-environment
```
This will:
- Configure Microsoft Azure environment variables
- Configure Google Cloud environment variables

## Development

### Starting the Development Environment

Start all services:
```bash
make dev
```

Rebuild and start services:
```bash
make dev-build
```

This will start:
- Frontend (Chainlit UI): http://localhost:8501
- Backend (FastAPI + LangChain/LangGraph): http://localhost:8000
- MCP Server: http://localhost:8002

### Code Quality

Format code:
```bash
make format
```

Run linting:
```bash
make lint
```

### Testing

Run all tests:
```bash
make test
```

Run specific test suites:
```bash
make test-unit        # Unit tests only
make test-integration # Integration tests only
```

### Dependency Management

Update dependencies:
```bash
make update-deps
```

### Cleanup

Clean development environment:
```bash
make clean
```

## Deployment

### Build

Build Docker images:
```bash
make build
```

### Deploy

Deploy to Azure:
```bash
make deploy
```

## Architecture

The system implements two different approaches:

1. Azure AI Agent Service per agent
2. Semantic Kernel for multi-agent orchestration

Both implementations share the same interface, allowing easy switching between approaches.

### Smart Scheduling Agent

The Smart Scheduling agent optimizes routes for MyPetParlor App by:
- Combining reservations with day/date schedules
- Finding optimal travel times
- Considering weather forecasts
- Prioritizing nearby bookings

### System Components

1. Frontend (Chainlit UI):
   - Provides chat interface
   - Handles file uploads
   - Displays scheduling results

2. Backend (FastAPI):
   - Manages agent orchestration
   - Handles business logic
   - Integrates with Azure services

3. MCP Server:
   - Interfaces with MyBusiness App API
   - Handles API authentication
   - Provides unified API interface

4. AI Agents:
   - Smart Scheduling Agent
   - First Aid Guidance Agent
   - Health Monitoring Agent
   - And more...

## Development Guidelines

### Adding New Agents

1. Create a new directory under both implementations:
```bash
mkdir -p agents/azure/new-agent
mkdir -p agents/semantic-kernel/new-agent
```

2. Implement the agent interface in both directories
3. Add tests under `tests/unit/` and `tests/integration/`
4. Update the agent registry in the backend

### Modifying Existing Agents

1. Make changes in both implementations
2. Update tests as needed
3. Test locally using the development environment
4. Submit a PR with your changes

## Monitoring and Evaluation

The platform includes built-in monitoring and evaluation capabilities:

1. Agent Evaluation:
   - Performance metrics
   - Response quality
   - Tool usage statistics

2. System Monitoring:
   - Container health
   - API response times
   - Error rates

Access monitoring dashboards through Azure Container Apps monitoring.

## Troubleshooting

### Common Issues

1. Container startup failures:
   - Check environment variables in .env
   - Verify Docker daemon is running
   - Check port conflicts

2. Agent failures:
   - Verify Azure credentials
   - Check API rate limits
   - Review agent logs

3. Development environment issues:
   - Run `make clean` and retry
   - Clear Docker cache if needed
   - Verify Python version

### Getting Help

- File an issue in the repository
- Check existing issues for solutions
- Review the documentation

## License

[License details here]
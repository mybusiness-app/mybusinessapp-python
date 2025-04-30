# MyBusiness App Monorepo for Python projects

This monorepo contains the MyPetParlor App AI Assistant, a sophisticated chatbot interface built with Chainlit that provides intelligent assistance for managing the MyPetParlor App portal.

## Quick Start

The project uses Make commands to simplify development workflows. To see all available commands:
```bash
make help
```

Common commands:
```bash
make setup                 # Setup development environment
make compose-build         # Build docker compose
make compose-up            # Run docker componse
make test                  # Run all tests
make clean                 # Clean up development environment
```

## Project Structure

- `.github/`: GitHub Actions workflows for CI/CD
- `apps/`: Application code
  - `chainlit/`: Chainlit-based AI Assistant implementation
- `tests/`: Test suites
- `docker/`: Docker configuration files
- `scripts/`: Utility scripts
- `keys/`: Authentication keys and certificates

## Key Features

### AI Assistant Capabilities

The Chainlit-based AI Assistant provides:

- **Intelligent Request Routing**: Uses a triage system to direct queries to specialized agents
- **Multiple Specialized Agents**:
  - Setup Guide Agent: Helps users configure their portal
  - Booking API Agent: Manages pet care bookings and scheduling
  - Customer API Agent: Handles customer data and relationships
  - Document API Agent: Manages legal documents and policies
  - Team API Agent: Configures team settings and operations
  - Tenant API Agent: Manages tenant-level configurations
  - Data Analysis Agent: Provides data insights and analysis

### Core Functionality

- **Smart Scheduling** (Coming Soon):
  - Route optimization for pet care visits
  - Weather-aware scheduling
  - Time and distance calculations
  - Booking management and coordination

- **Data Analysis**:
  - Built-in code interpreter for data processing
  - Trend analysis and insights
  - Performance metrics tracking
  - Business intelligence reporting

- **API Integration**:
  - Seamless integration with MyPetParlor App APIs
  - Azure AI Agent Service integration
  - Semantic Kernel orchestration
  - OpenAPI tool integration

## Prerequisites

- Python 3.13+
- Docker
- Azure CLI
- Azure subscription with:
  - Azure AI Agent Service enabled
  - Appropriate API access credentials

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

Required environment variables:
- `AZURE_AI_AGENT_MODEL_DEPLOYMENT_NAME`: Azure AI model deployment name
- Azure authentication credentials
- MyPetParlor App API credentials

## Development

### Starting the Development Environment

Start the AI Assistant:
```bash
make dev
```

This will start:
- Chainlit UI: http://localhost:8501

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

## Architecture

### AI Assistant Components

1. **Triage System**:
   - Main coordinator for routing requests
   - Intelligent request analysis
   - Multi-agent orchestration
   - Response synthesis

2. **Specialized Agents**:
   - Each agent focuses on specific API domain
   - Built-in data analysis capabilities
   - Code interpretation abilities
   - Plugin support for extended functionality

3. **Tools and Plugins**:
   - OpenAPI tools for API access
   - Code interpreter for data analysis
   - Scheduling plugin for optimization
   - File import plugin for data processing

### Authentication and Security

- Firebase token authentication
- API key management
- Header-based authentication
- Deployment location awareness

## Monitoring and Evaluation

The AI Assistant includes:

1. **Logging and Monitoring**:
   - Detailed logging of agent interactions
   - Error tracking and reporting
   - Performance monitoring
   - Usage analytics

2. **Response Quality**:
   - Echo detection and prevention
   - Response synthesis verification
   - Data validation
   - Schedule optimization metrics

## Troubleshooting

### Common Issues

1. Authentication Failures:
   - Verify Azure credentials
   - Check API keys
   - Validate Firebase tokens
   - Confirm header parameters

2. Agent Response Issues:
   - Check environment variables
   - Verify API access
   - Review agent logs
   - Check response synthesis

3. Development Environment:
   - Run `make clean` and retry
   - Verify Python version
   - Check dependency versions
   - Validate environment setup

### Getting Help

- File an issue in the repository
- Check existing issues for solutions
- Review the documentation
- Contact support team

## License

[License details here]
# MyBusiness App Monorepo for Python projects

This monorepo contains the MyPetParlor App AI Assistant, a sophisticated chatbot interface built with Chainlit that provides intelligent assistance for managing the MyPetParlor App portal.

- [MyPetParlor App Website](https://mypetparlorapp.com)
- [MyPetParlor App without AI Assistant](https://portal.mypetparlorapp.com/mppdemo/dashboard/overview)
- [MyPetParlor App with AI Assistant](https://staging.portal.mypetparlorapp.com/mppdemo/dashboard/overview)

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
    - `custom_agents/`: Specialized agent implementations
      - `base_client.py`: Base class for all agent clients
      - `read_api/`: Read-only API agents implementation
      - `setup_guide/`: Setup guide agents implementation
      - `triage/`: Triage agent implementation
    - `telemetry/`: Azure Monitor and OpenTelemetry integration
      - `appinsights.py`: Azure Application Insights configuration
      - `__init__.py`: Package initialization
    - `openapi/`: OpenAPI specifications for API integration
      - `mypetparlorapp/`: MyPetParlor App API specifications
        - `address/`: Address API OpenAPI specs
        - `booking/`: Booking API OpenAPI specs
        - `customer/`: Customer API OpenAPI specs
        - `document/`: Document API OpenAPI specs
        - `employee/`: Employee API OpenAPI specs
        - `pet/`: Pet API OpenAPI specs
        - `team/`: Team API OpenAPI specs
        - `tenants/`: Tenant API OpenAPI specs
    - `app.py`: Main Chainlit application
- `tests/`: Test suites
- `docker/`: Docker configuration files
- `scripts/`: Utility scripts
- `keys/`: Authentication keys and certificates

## Architecture

The MyPetParlor App system architecture consists of several integrated components deployed on Azure using the [Deployment Stamp](https://learn.microsoft.com/en-us/azure/architecture/patterns/deployment-stamp) pattern for high availability and global scale.

### Azure Container Apps Environment (Per Stamp)

The system utilizes a unified Azure Container Apps environment that hosts multiple containerized applications:

1. **Chainlit AI Assistant Backend**
   - Runs as a containerized service within Azure Container Apps
   - Provides the AI assistant functionality through a REST API
   - Handles natural language processing and query routing
   - Communicates with Azure AI services for advanced reasoning

2. **Server-Side Rendered (SSR) Web Application**
   - Built with the Vike framework [https://vike.dev/](https://vike.dev/)
   - Deployed to the same Azure Container Apps environment
   - Accessible at [https://staging.portal.mypetparlorapp.com/mppdemo/dashboard/overview](https://staging.portal.mypetparlorapp.com/mppdemo/dashboard/overview)
   - Provides the user interface for the MyPetParlor App portal
   - Implements server-side rendering for improved performance and SEO

3. **Go-based Multi-tenant API Backend**
   - Deployed as a containerized service within Azure Container Apps
   - Robust Go-based container image powering the backend services
   - Features a multi-tenant architecture supporting multiple business tenants
   - Provides logical isolation of tenant data and configurations
   - Enables tenant-specific customizations and settings

- **Multi-stamp Deployment**
  - Geographically distributed deployments for global scale
  - Regional data residency compliance
  - Low-latency access for users worldwide

- **Security Features**
  - Role-based access control (RBAC) for fine-grained permissions
  - JWT authentication integrated with Firebase Authentication
  - Request validation and sanitization
  - Comprehensive audit logging

- **API Gateway**
  - Hosted at https://mpp-api-mybusinessapp-san.azure-api.net/v2/
  - RESTful endpoints with OpenAPI specifications
  - Domain-specific APIs (Booking, Customer, Document, Team, etc.)

### Azure AI Services Integration

The system leverages Azure's AI capabilities:

- **Azure OpenAI Service**
  - Utilizes the GPT-4o model for advanced natural language understanding
  - Powers the AI Assistant's reasoning and response generation
  - Enables complex query handling and contextual understanding
  - Fine-tuned for domain-specific knowledge about pet care services

- **Azure AI Agent Service**
  - Orchestrates specialized AI agents for different domains
  - Manages agent routing and specialization
  - Provides a unified interface for agent interactions
  - Implements guardrails for responsible AI usage

### Authentication and Authorization Flow

1. Users authenticate via Firebase Authentication
2. JWT tokens are issued with appropriate role claims
3. AI Assistant inherits user permissions through token passing
4. Go API validates tokens and enforces RBAC policies
5. API responses are filtered based on user permissions
6. AI Assistant only accesses and presents data the user is authorized to see

### Data Flow Architecture

1. User interacts with the SSR web application
2. Web app communicates with the Chainlit AI Assistant backend
3. AI Assistant processes queries using Azure OpenAI (GPT-4o)
4. Specialized agents are invoked based on query intent
5. Agents interact with the Go-based API using the user's JWT token
6. Go API enforces access controls and retrieves authorized data
7. Results are returned to the user through the web interface

This architecture provides a scalable, globally distributed system with enterprise-grade security while leveraging Azure's managed services for reliability and performance.

## Key Features

### AI Assistant Capabilities

The Chainlit-based AI Assistant provides:

- **Intelligent Request Routing**: Uses a triage system to direct queries to specialized agents
- **Multiple Specialized Agents**:
  - Setup Guide Agent: Coordinates specialized setup agents
    - User Setup Agent: Guides through user profile configuration
    - Organization Setup Agent: Assists with organization profile setup
    - Staff Profile Agent: Helps configure staff profiles and roles
    - Team Setup Agent: Manages team creation and configuration
    - Customer Setup Agent: Guides through customer profile setup
    - Booking Setup Agent: Configures booking and scheduling systems
  - API Agents (Read-only):
    - Address API Agent: Manages customer address resources
    - Booking API Agent: Handles booking resources with scheduling capabilities
    - Customer API Agent: Manages customer data with import functionality
    - Document API Agent: Handles legal documents and policies
    - Employee API Agent: Manages employee resources
    - Pet API Agent: Handles pet profiles and care requirements
    - Team API Agent: Manages team resources and configurations
    - Tenant API Agent: Handles tenant-level resources
  - Data Analysis Agent: Provides advanced data analysis using Code Interpreter

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

### Telemetry and Monitoring

The AI Assistant uses Azure Monitor with OpenTelemetry for comprehensive telemetry (logging, metrics, and tracing):

1. **Azure Application Insights Integration**:
   - Automatic instrumentation of Python applications
   - Distributed tracing across services
   - Request and dependency tracking
   - Performance monitoring and metrics
   - Custom event tracking
   - Exception logging and monitoring

2. **OpenTelemetry Configuration**:
   - Standardized observability framework
   - Custom trace attributes for AI operations
   - Metric collection for agent performance
   - Context propagation across components
   - Integration with Azure Monitor

3. **Monitoring Capabilities**:
   - End-to-end request tracing
   - Agent operation metrics
   - API call monitoring
   - Performance analytics
   - Error tracking and alerting
   - Resource utilization metrics

### API Integration

The AI Assistant integrates with MyPetParlor App APIs through OpenAPI specifications:

1. **OpenAPI Structure**:
   - Organized by domain-specific APIs
   - Each API has its own OpenAPI/Swagger specification
   - Standardized authentication parameters
   - Detailed endpoint documentation
   - Request/response schemas
   - Error definitions

2. **API Domains**:
   - **Address API**: Customer location management
     - Address validation
     - Geocoding integration
     - Location-based services
   
   - **Booking API**: Service scheduling
     - Appointment management
     - Schedule optimization
     - Availability checking
   
   - **Customer API**: Client management
     - Profile management
     - Preference tracking
     - Service history
   
   - **Document API**: Legal document handling
     - Policy management
     - Terms and conditions
     - Document versioning
   
   - **Employee API**: Staff management
     - Profile management
     - Skill tracking
     - Availability management
   
   - **Pet API**: Pet profile management
     - Health records
     - Care preferences
     - Service requirements
   
   - **Team API**: Team organization
     - Team structure
     - Role management
     - Service area definition
   
   - **Tenant API**: Business management
     - Organization settings
     - Business rules
     - Configuration management

3. **Integration Features**:
   - Automatic tool generation from OpenAPI specs
   - Type-safe API interactions
   - Authentication handling
   - Error mapping
   - Response validation
   - Rate limiting support

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
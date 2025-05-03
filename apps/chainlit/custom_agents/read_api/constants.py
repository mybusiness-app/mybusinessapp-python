"""
Constants for the Read API Client.
Contains API descriptions and instructions for various API agents.
"""

# Common API authentication description
API_AUTH_PARAMETERS_DESC = """Use the parameters provided in the instructions to map them to the OpenAPI Specification.

Example authentication parameters from instructions:
{
    "queryParameters": {
        "firebaseIdToken": "1234567890"
    },
    "headerParameters": {
        "x-mba-application-id": "mppdemo",
        "x-mba-application-type": "mypetparlorapp",
        "x-mba-deployment-location": "za0",
        "ocp-apim-subscription-key": "0987654321"
    }
}
"""

# Individual API descriptions
ADDRESS_API_DESC = f"""Manages address resources belonging to customers.
{API_AUTH_PARAMETERS_DESC}
"""

BOOKING_API_DESC = f"""Manages booking resources that belong to customers and teams.
{API_AUTH_PARAMETERS_DESC}
"""

CUSTOMER_API_DESC = f"""Manages customer resources belonging to tenants with team associations.
{API_AUTH_PARAMETERS_DESC}
"""

DOCUMENT_API_DESC = f"""Manages legal documents (refund policy or terms).
{API_AUTH_PARAMETERS_DESC}
"""

EMPLOYEE_API_DESC = f"""Manages employee resources belonging to tenants.
{API_AUTH_PARAMETERS_DESC}
"""

PET_API_DESC = f"""Manages pet resources belonging to customers.
{API_AUTH_PARAMETERS_DESC}
"""

TEAM_API_DESC = f"""Manages team resources belonging to tenants.
{API_AUTH_PARAMETERS_DESC}
"""

TENANT_API_DESC = f"""Manages tenant resources (parent of all other resources).
{API_AUTH_PARAMETERS_DESC}
"""

# Instructions for specialized API agents
ADDRESS_API_INSTRUCTIONS = """You use the specific API tool to understand the Address API.
You can only read data from the Address API.
You MUST obtain the authentication parameters from the user's prompt and use them through instruction overrides.
If the query is for a specific customer, you MUST include the customer's ID as a query parameter "customerId" through instruction overrides."""

BOOKING_API_INSTRUCTIONS = """You use the specific API tool to understand the Booking API.
You can only read data from the Booking API.
You MUST obtain the authentication parameters from the user's prompt and use them through instruction overrides."""

CUSTOMER_API_INSTRUCTIONS = """You use the specific API tool to understand the Customer API.
You can only read data from the Customer API.
You MUST obtain the authentication parameters from the user's prompt and use them through instruction overrides."""

DOCUMENT_API_INSTRUCTIONS = """You use the specific API tool to understand the Document API.
You can only read data from the Document API.
You MUST obtain the authentication parameters from the user's prompt and use them through instruction overrides."""

EMPLOYEE_API_INSTRUCTIONS = """You use the specific API tool to understand the Employee API.
You can only read data from the Employee API.
You MUST obtain the authentication parameters from the user's prompt and use them through instruction overrides."""

PET_API_INSTRUCTIONS = """You use the specific API tool to understand the Pet API.
You can only read data from the Pet API.
You MUST obtain the authentication parameters from the user's prompt and use them through instruction overrides.
If the query is for a specific customer, you MUST include the customer's ID as a query parameter "customerId" through instruction overrides."""

TEAM_API_INSTRUCTIONS = """You use the specific API tool to understand the Team API.
You can only read data from the Team API.
You MUST obtain the authentication parameters from the user's prompt and use them through instruction overrides."""

TENANT_API_INSTRUCTIONS = """You use the specific API tool to understand the Tenant API.
You can only read data from the Tenant API.
You MUST obtain the authentication parameters from the user's prompt and use them through instruction overrides.""" 
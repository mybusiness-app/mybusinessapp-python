#!/bin/bash

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check if az CLI is installed
if ! command_exists az; then
    echo -e "${RED}Error: Azure CLI (az) is not installed.${NC}"
    echo "Please install it from: https://docs.microsoft.com/cli/azure/install-azure-cli"
    exit 1
fi

# Check if user is logged in to Azure
if ! az account show >/dev/null 2>&1; then
    echo -e "${YELLOW}You need to login to Azure first.${NC}"
    az login
fi

# Set default subscription
DEFAULT_SUBSCRIPTION_ID="d0aca6aa-9d10-40ee-b0c0-d518722eba85"
DEFAULT_SUBSCRIPTION_NAME="My Pet Parlour Production Subscription"
echo -e "${YELLOW}Available subscriptions:${NC}"
az account list --output table
echo
echo -e "${YELLOW}Default subscription is set to: $DEFAULT_SUBSCRIPTION_NAME ($DEFAULT_SUBSCRIPTION_ID)${NC}"
read -p "Enter the subscription ID to use (press Enter to use default): " SUBSCRIPTION_ID

SUBSCRIPTION_ID=${SUBSCRIPTION_ID:-$DEFAULT_SUBSCRIPTION_ID}

# Set the subscription
echo -e "\n${YELLOW}Setting subscription to: $SUBSCRIPTION_ID${NC}"
az account set --subscription $SUBSCRIPTION_ID

# Get or create resource group
read -p "Enter the resource group name (default is 'mypetparlor-ai-agents-rg'): " RESOURCE_GROUP
RESOURCE_GROUP=${RESOURCE_GROUP:-"mypetparlor-ai-agents-rg"}

read -p "Enter the location (default is 'eastus'): " LOCATION
LOCATION=${LOCATION:-"eastus"}

# Create resource group if it doesn't exist
if ! az group show --name $RESOURCE_GROUP >/dev/null 2>&1; then
    echo -e "\n${YELLOW}Creating resource group: $RESOURCE_GROUP${NC}"
    az group create --name $RESOURCE_GROUP --location $LOCATION
fi

# Select environment
echo -e "\n${YELLOW}Select environment to deploy:${NC}"
select ENVIRONMENT in "dev" "staging" "prod"; do
    case $ENVIRONMENT in
        dev|staging|prod ) break;;
        * ) echo "Invalid selection. Please choose 1, 2, or 3.";;
    esac
done

# Create service principal for the application
echo -e "\n${YELLOW}Creating service principal for the application...${NC}"
SP_NAME="mypetparlor-ai-agents-$ENVIRONMENT-sp"

# Check if service principal already exists
echo "Creating/resetting new service principal: $SP_NAME"
SP_CREATION=$(az ad sp create-for-rbac \
    --name $SP_NAME \
    --role contributor \
    --scopes /subscriptions/$SUBSCRIPTION_ID/resourceGroups/$RESOURCE_GROUP \
    --json-auth \
    --output json)

# Extract credentials
echo $SP_CREATION
CLIENT_ID=$(echo $SP_CREATION | jq -r '.clientId')
CLIENT_SECRET=$(echo $SP_CREATION | jq -r '.clientSecret')
TENANT_ID=$(echo $SP_CREATION | jq -r '.tenantId')

# Assign the Azure AI Developer role to the service principal
az role assignment create \
    --assignee $CLIENT_ID \
    --role "Azure AI Developer" \
    --scope /subscriptions/$SUBSCRIPTION_ID/resourceGroups/$RESOURCE_GROUP

# Deploy Bicep template
echo -e "\n${YELLOW}Deploying Azure resources for ${ENVIRONMENT} environment...${NC}"
DEPLOYMENT_OUTPUT=$(az deployment group create \
    --resource-group $RESOURCE_GROUP \
    --template-file ./infrastructure/bicep/main.bicep \
    --parameters @./infrastructure/bicep/azuredeploy.${ENVIRONMENT}.parameters.json \
    --query "properties.outputs" \
    --output json)

# Extract values from deployment output
AI_PROJECT_CONNECTION_STRING="$(echo $DEPLOYMENT_OUTPUT | jq -r '.azureAIProjectConnectionString.value')"
MODEL_DEPLOYMENT_NAME="$(echo $DEPLOYMENT_OUTPUT | jq -r '.azureAIModelDeploymentName.value')"
OPENAI_SERVICE_NAME="$(echo $DEPLOYMENT_OUTPUT | jq -r '.azureOpenAIServiceName.value')"
OPENAI_ENDPOINT="$(echo $DEPLOYMENT_OUTPUT | jq -r '.azureOpenAIEndpoint.value')"

# Get OpenAI key using Azure CLI
echo -e "\n${YELLOW}Retrieving Azure OpenAI key...${NC}"
OPENAI_KEY=$(az cognitiveservices account keys list \
    --name $OPENAI_SERVICE_NAME \
    --resource-group $RESOURCE_GROUP \
    --query "key1" \
    --output tsv)

if [ -z "$OPENAI_KEY" ]; then
    echo -e "${RED}Error: Failed to retrieve Azure OpenAI key${NC}"
    exit 1
fi

# Update .env file
echo -e "\n${YELLOW}Updating .env file with Azure configuration...${NC}"

# Create .env from example if it doesn't exist
if [ ! -f ./.env ]; then
    cp ./.env.example ./.env
fi

# Update Azure settings in .env
sed -i.bak -e "s|^AZURE_AI_PROJECT_CONNECTION_STRING=.*|AZURE_AI_PROJECT_CONNECTION_STRING=$AI_PROJECT_CONNECTION_STRING|" \
    -e "s|^MODEL_DEPLOYMENT_NAME=.*|MODEL_DEPLOYMENT_NAME=$MODEL_DEPLOYMENT_NAME|" \
    -e "s|^AZURE_CLIENT_ID=.*|AZURE_CLIENT_ID=$CLIENT_ID|" \
    -e "s|^AZURE_TENANT_ID=.*|AZURE_TENANT_ID=$TENANT_ID|" \
    -e "s|^AZURE_CLIENT_SECRET=.*|AZURE_CLIENT_SECRET=$CLIENT_SECRET|" ./.env

# Remove backup file
rm -f ./.env.bak

echo -e "\n${GREEN}Setup complete!${NC}"
echo -e "Azure configuration:"
echo -e "  Resource Group: ${YELLOW}$RESOURCE_GROUP${NC}"
echo -e "  Environment: ${YELLOW}$ENVIRONMENT${NC}"
echo -e "  Location: ${YELLOW}$LOCATION${NC}"
echo -e "  Model Deployment: ${YELLOW}$MODEL_DEPLOYMENT_NAME${NC}"
echo -e "  OpenAI Service: ${YELLOW}$OPENAI_SERVICE_NAME${NC}"
echo -e "  OpenAI Endpoint: ${YELLOW}$OPENAI_ENDPOINT${NC}"
echo -e "  Service Principal: ${YELLOW}$SP_NAME${NC}"
echo
echo -e "${YELLOW}Important:${NC}"
echo "1. The .env file has been updated with your Azure settings"
echo "2. Make sure to keep your .env file secure and never commit it to version control"
echo "3. Service principal credentials have been saved to your .env file"
echo
echo -e "${YELLOW}Next steps:${NC}"
echo "1. Review the .env file and ensure all settings are configured correctly"
echo "2. Run 'make setup' to complete the rest of the application setup"
echo "3. When deploying to containers, ensure the environment variables are properly set"

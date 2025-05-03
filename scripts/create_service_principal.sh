#!/bin/bash

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Default environment
ENVIRONMENT=
# Parse command line arguments
while [[ "$#" -gt 0 ]]; do
    case $1 in
        --environment)
            ENVIRONMENT="$2"
            shift 2
            ;;
        *)
            echo "Unknown parameter: $1"
            exit 1
            ;;
    esac
done

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
echo -e "${YELLOW}Setting subscription to: $SUBSCRIPTION_ID${NC}\n"
az account set --subscription $SUBSCRIPTION_ID

# Get or create resource group
read -p "Enter the resource group name (default is 'mpp-stamp-0-ai-eastus2-rg'): " RESOURCE_GROUP
RESOURCE_GROUP=${RESOURCE_GROUP:-"mpp-stamp-0-ai-eastus2-rg"}
echo -e "${YELLOW}Setting resource group to: $RESOURCE_GROUP${NC}\n"

read -p "Enter the location (default is 'eastus2'): " LOCATION
LOCATION=${LOCATION:-"eastus2"}
echo -e "${YELLOW}Setting location to: $LOCATION${NC}\n"

read -p "Enter the project name (default is 'aihp-mppdev-odm3'): " PROJECT_NAME
PROJECT_NAME=${PROJECT_NAME:-"aihp-mppdev-odm3"}
echo -e "${YELLOW}Setting project name to: $PROJECT_NAME${NC}\n"

read -p "Enter the application insights name (default is 'appi-mppdev-odm3'): " APPLICATION_INSIGHTS_NAME
APPLICATION_INSIGHTS_NAME=${APPLICATION_INSIGHTS_NAME:-"appi-mppdev-odm3"}
echo -e "${YELLOW}Setting application insights name to: $APPLICATION_INSIGHTS_NAME${NC}\n"

# Create resource group if it doesn't exist
if ! az group show --name $RESOURCE_GROUP >/dev/null 2>&1; then
    echo -e "\n${YELLOW}Creating resource group: $RESOURCE_GROUP${NC}"
    az group create --name $RESOURCE_GROUP --location $LOCATION
fi

# Select environment
echo -e "\n${YELLOW}Select environment to deploy:${NC}"
select ENVIRONMENT in "development" "production"; do
    case $ENVIRONMENT in
        development|production ) break;;
        * ) echo "Invalid selection. Please choose 1, 2, or 3.";;
    esac
done

# Create service principal for the application
echo -e "\n${YELLOW}Creating service principal for the application...${NC}"
SP_NAME="mpp-stamp-0-ai-$LOCATION-sp"

# Check if service principal already exists
echo "Creating/resetting new service principal: $SP_NAME"
SP_CREATION=$(az ad sp create-for-rbac \
    --name $SP_NAME \
    --role "Azure AI Developer" \
    --scopes /subscriptions/$SUBSCRIPTION_ID/resourceGroups/$RESOURCE_GROUP/providers/Microsoft.MachineLearningServices/workspaces/$PROJECT_NAME \
    --json-auth \
    --output json)

# Extract credentials
CLIENT_ID=$(echo $SP_CREATION | jq -r '.clientId')
CLIENT_SECRET=$(echo $SP_CREATION | jq -r '.clientSecret')
TENANT_ID=$(echo $SP_CREATION | jq -r '.tenantId')


echo "Assigning Monitoring Contributor role to the service principal"
az role assignment create \
    --assignee $CLIENT_ID \
    --role "Monitoring Contributor" \
    --scope /subscriptions/$SUBSCRIPTION_ID/resourceGroups/$RESOURCE_GROUP/providers/Microsoft.Insights/components/$APPLICATION_INSIGHTS_NAME

# Update .env file
echo -e "\n${YELLOW}Updating .env.$ENVIRONMENT file with Azure configuration...${NC}"

# Create .env from example if it doesn't exist
if [ ! -f ./.env.$ENVIRONMENT ]; then
    cp ./.env.example ./.env.$ENVIRONMENT
fi

# Update Azure settings in .env
sed -i.bak -e "s|^AZURE_CLIENT_ID=.*|AZURE_CLIENT_ID=$CLIENT_ID|" \
    -e "s|^AZURE_TENANT_ID=.*|AZURE_TENANT_ID=$TENANT_ID|" \
    -e "s|^AZURE_CLIENT_SECRET=.*|AZURE_CLIENT_SECRET=$CLIENT_SECRET|" ./.env.$ENVIRONMENT

# Remove backup file
rm -f ./.env.$ENVIRONMENT.bak

echo -e "\n${GREEN}Setup complete!${NC}"
echo -e "Azure configuration:"
echo -e "  Resource Group: ${YELLOW}$RESOURCE_GROUP${NC}"
echo -e "  Environment: ${YELLOW}$ENVIRONMENT${NC}"
echo -e "  Location: ${YELLOW}$LOCATION${NC}"
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

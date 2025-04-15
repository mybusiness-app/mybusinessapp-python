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

# Check if gcloud is installed
if ! command_exists gcloud; then
    echo -e "${RED}Error: Google Cloud SDK (gcloud) is not installed.${NC}"
    echo "Please install it from: https://cloud.google.com/sdk/docs/install"
    exit 1
fi

# Check if user is logged in to gcloud
if ! gcloud auth list --filter=status:ACTIVE --format="value(account)" >/dev/null 2>&1; then
    echo -e "${YELLOW}You need to login to Google Cloud first.${NC}"
    gcloud auth login
fi

# Get the project ID
echo -e "${YELLOW}Available projects:${NC}"
gcloud projects list
echo
read -p "Enter the project ID to use (default is 'mypetparlour-nonprod-shared'): " PROJECT_ID

# Set the project
if [ -z "$PROJECT_ID" ]; then
    PROJECT_ID="mypetparlour-nonprod-shared"
    echo -e "\n${YELLOW}No project ID entered. Defaulting to: $PROJECT_ID${NC}"
else
    echo -e "\n${YELLOW}Setting project to: $PROJECT_ID${NC}"
fi
gcloud config set project $PROJECT_ID

# Enable the Route Optimization API
echo -e "\n${YELLOW}Enabling Route Optimization API...${NC}"
gcloud services enable routeoptimization.googleapis.com

# Create service account
SA_NAME="mypetparlorapp-router"
SA_EMAIL="$SA_NAME@$PROJECT_ID.iam.gserviceaccount.com"

echo -e "\n${YELLOW}Creating service account: $SA_NAME${NC}"
gcloud iam service-accounts create $SA_NAME \
    --display-name="MyPetParlor App Route Optimization Service Account" \
    --description="Service account for MyPetParlor App route optimization"

# Grant necessary permissions
echo -e "\n${YELLOW}Granting necessary permissions...${NC}"
gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:$SA_EMAIL" \
    --role="roles/routeoptimization.editor"

# Create and download service account key
KEY_FILE="mypetparlorapp-route-optimization-key.json"
echo -e "\n${YELLOW}Creating service account key: $KEY_FILE${NC}"
gcloud iam service-accounts keys create $KEY_FILE \
    --iam-account=$SA_EMAIL

# Move key file to secure location
KEYS_DIR="./keys"
mkdir -p $KEYS_DIR
mv $KEY_FILE $KEYS_DIR/

# Update .env file
echo -e "\n${YELLOW}Updating .env file with Google Cloud configuration...${NC}"

# Create .env from example if it doesn't exist
if [ ! -f ./.env ]; then
    cp ./.env.example ./.env
fi

# Update Google Cloud settings in .env
if grep -q "GOOGLE_CLOUD_PROJECT=" ./.env; then
    sed -i.bak -e "s/^GOOGLE_CLOUD_PROJECT=.*/GOOGLE_CLOUD_PROJECT=$PROJECT_ID/" ./.env
else
    echo "GOOGLE_CLOUD_PROJECT=$PROJECT_ID" >> ./.env
fi

if grep -q "GOOGLE_APPLICATION_CREDENTIALS=" ./.env; then
    sed -i.bak -e "s|^GOOGLE_APPLICATION_CREDENTIALS=.*|GOOGLE_APPLICATION_CREDENTIALS=keys/$KEY_FILE|" ./.env
else
    echo "GOOGLE_APPLICATION_CREDENTIALS=keys/$KEY_FILE" >> ./.env
fi

# Remove backup file
rm -f ./.env.bak

# Add keys directory to .gitignore if not already present
if ! grep -q "keys/" ./.gitignore 2>/dev/null; then
    echo "" >> ./.gitignore
    echo "# Keys directory (e.g. Google Cloud service account key)" >> ./.gitignore
    echo "keys/" >> ./.gitignore
fi

echo -e "\n${GREEN}Setup complete!${NC}"
echo -e "Google Cloud configuration:"
echo -e "  Project ID: ${YELLOW}$PROJECT_ID${NC}"
echo -e "  Service Account: ${YELLOW}$SA_EMAIL${NC}"
echo -e "  Credentials file: ${YELLOW}keys/$KEY_FILE${NC}"
echo
echo -e "${YELLOW}Important:${NC}"
echo "1. The service account key has been saved to: keys/$KEY_FILE"
echo "2. This directory has been added to .gitignore for security"
echo "3. The .env file has been updated with your Google Cloud settings"
echo
echo -e "${YELLOW}Next steps:${NC}"
echo "1. Review the .env file and ensure all other settings are configured"
echo "2. Run 'make setup' to complete the rest of the application setup"
// Execute this main file to deploy Azure AI Foundry resources in the basic security configuration

// Parameters
@allowed([
  'dev'
  'staging'
  'prod'
])
@description('Environment name (dev, staging, prod)')
param environment string

@description('Azure region used for the deployment of all resources.')
param location string = resourceGroup().location

@description('Friendly name for your Azure AI resource')
param aiHubFriendlyName string

@description('Description of your Azure AI resource displayed in AI Foundry')
param aiHubDescription string

@description('Set of tags to apply to all resources.')
param tags object

@description('Name of the Azure AI Search account')
param aiSearchName string = 'agent-ai-search'

@description('Name for capabilityHost')
param capabilityHostName string = 'caphost1'

@description('AI Service Account kind: either AzureOpenAI or AIServices')
param aiServiceKind string = 'AIServices'

@description('Array of model configurations to deploy')
param models array = [
  {
    name: 'gpt-4'
    deploymentName: 'gpt4'
    version: '1106-Preview'
    format: 'OpenAI'
    capacity: 1
  }
  {
    name: 'gpt-35-turbo'
    deploymentName: 'gpt35'
    version: '1106'
    format: 'OpenAI'
    capacity: 1
  }
]

// Variables
var baseName = toLower('mpp${environment}') // mpp = MyPetParlor
var uniqueSuffix = substring(uniqueString(resourceGroup().id), 0, 4)

// Dependent resources for the Azure Machine Learning workspace
module aiDependencies 'modules/dependent-resources.bicep' = {
  name: 'dependencies-${baseName}-${uniqueSuffix}-deployment'
  params: {
    location: location
    storageName: 'st${baseName}${uniqueSuffix}'
    keyvaultName: 'kv${baseName}${uniqueSuffix}' // Removed hyphen to meet Key Vault naming requirements
    applicationInsightsName: 'appi-${baseName}-${uniqueSuffix}'
    containerRegistryName: 'cr${baseName}${uniqueSuffix}'
    aiServicesName: 'ais-${baseName}-${uniqueSuffix}'
    aiSearchName: '${aiSearchName}-${uniqueSuffix}'
    tags: tags
  }
}

// Create AI Hub first
module aiHub 'modules/ai-hub.bicep' = {
  name: 'aiHub-${uniqueSuffix}-deployment'
  params: {
    aiHubName: 'aih-${baseName}-${uniqueSuffix}'
    aiHubFriendlyName: aiHubFriendlyName
    aiHubDescription: aiHubDescription
    location: location
    tags: tags
    aiServicesId: aiDependencies.outputs.aiservicesID
    aiServicesTarget: aiDependencies.outputs.aiservicesTarget
    aiSearchName: aiDependencies.outputs.aiSearchName
    aiSearchId: aiDependencies.outputs.aiSearchId
    keyVaultId: aiDependencies.outputs.keyvaultId
    storageAccountId: aiDependencies.outputs.storageId
    aiServiceKind: aiServiceKind
  }
}

// Create AI Project workspace
module aiProject 'modules/ai-project.bicep' = {
  name: 'aiProject-${uniqueSuffix}-deployment'
  params: {
    projectName: 'aihp-${baseName}-${uniqueSuffix}'
    projectFriendlyName: '${aiHubFriendlyName} Project'
    projectDescription: 'AI Project for ${aiHubFriendlyName}'
    location: location
    tags: tags
    hubResourceId: aiHub.outputs.aiHubID
  }
}

// Deploy AI Models
module aiModels 'modules/ai-models.bicep' = {
  name: 'aiModels-${uniqueSuffix}-deployment'
  params: {
    aiServicesName: aiDependencies.outputs.aiservicesName
    models: models
    tags: tags
  }
}

// Configure capability host
module capabilityHost 'modules/capability-host.bicep' = {
  name: 'capabilityHost-${uniqueSuffix}-deployment'
  params: {
    aiHubName: aiHub.outputs.aiHubName
    aiProjectName: aiProject.outputs.projectName
    capabilityHostName: '${uniqueSuffix}-${capabilityHostName}'
    acsConnectionName: aiHub.outputs.acsConnectionName
    aoaiConnectionName: aiHub.outputs.aoaiConnectionName
  }
}

// Outputs
output azureAIProjectConnectionString string = aiProject.outputs.projectConnectionString
output azureAIModelDeploymentName string = aiModels.outputs.deploymentNames[0].name
output azureOpenAIEndpoint string = aiDependencies.outputs.aiservicesTarget
output azureOpenAIServiceName string = aiDependencies.outputs.aiservicesName

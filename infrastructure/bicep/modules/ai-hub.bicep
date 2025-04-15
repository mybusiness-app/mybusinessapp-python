@description('Name of the AI Hub')
param aiHubName string

@description('Friendly name for the AI Hub')
param aiHubFriendlyName string

@description('Description of the AI Hub')
param aiHubDescription string

@description('Azure region for resource deployment')
param location string

@description('Tags to apply to all resources')
param tags object

@description('ID of the AI Services account')
param aiServicesId string

@description('Endpoint of the AI Services account')
param aiServicesTarget string

@description('ID of the Key Vault')
param keyVaultId string

@description('ID of the Storage Account')
param storageAccountId string

@description('Name of the AI Search resource')
param aiSearchName string

@description('ID of the AI Search resource')
param aiSearchId string

@description('AI Service Account kind: either OpenAI or AIServices')
param aiServiceKind string

var acsConnectionName = '${aiHubName}-connection-AISearch'
var aoaiConnection = '${aiHubName}-connection-AIServices_aoai'
var kindAIServicesExists = aiServiceKind == 'AIServices'
var aiServiceConnectionName = kindAIServicesExists ? '${aiHubName}-connection-AIServices' : aoaiConnection

// AI Hub
resource aiHub 'Microsoft.MachineLearningServices/workspaces@2024-10-01-preview' = {
  name: aiHubName
  location: location
  tags: tags
  identity: {
    type: 'SystemAssigned'
  }
  properties: {
    friendlyName: aiHubFriendlyName
    description: aiHubDescription
    keyVault: keyVaultId
    storageAccount: storageAccountId
    systemDatastoresAuthMode: 'identity'
  }
  kind: 'Hub'
}

// AI Services Connection
resource aiServicesConnection 'Microsoft.MachineLearningServices/workspaces/connections@2024-07-01-preview' = {
  parent: aiHub
  name: aiServiceConnectionName
  properties: {
    category: aiServiceKind
    target: aiServicesTarget
    authType: 'AAD'
    isSharedToAll: true
    metadata: {
      ApiType: 'Azure'
      ResourceId: aiServicesId
    }
  }
}

// AI Search Connection
resource aiSearchConnection 'Microsoft.MachineLearningServices/workspaces/connections@2024-07-01-preview' = {
  parent: aiHub
  name: acsConnectionName
  properties: {
    category: 'CognitiveSearch'
    target: 'https://${aiSearchName}.search.windows.net'
    authType: 'AAD'
    isSharedToAll: true
    metadata: {
      ApiType: 'Azure'
      ResourceId: aiSearchId
    }
  }
}

// Outputs
output aiHubID string = aiHub.id
output aiHubName string = aiHub.name
output aoaiConnectionName string = aoaiConnection
output acsConnectionName string = acsConnectionName

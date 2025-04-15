@description('The name of the Azure OpenAI service')
param aiServicesName string

@description('Array of model names to deploy')
param models array = [
  'gpt-4o'
]

@description('Tags to apply to all resources')
param tags object = {}

// Model configuration mapping
var modelConfigs = {
  'gpt-4': {
    deploymentName: 'gpt4'
    version: '1106-Preview'
    format: 'OpenAI'
    capacity: 1
  }
  'gpt-35-turbo': {
    deploymentName: 'gpt35'
    version: '1106'
    format: 'OpenAI'
    capacity: 1
  }
  'gpt-4o': {
    deploymentName: 'gpt4o'
    version: '2024-05-13'
    format: 'OpenAI'
    capacity: 1
  }
  'gpt-o3-mini': {
    deploymentName: 'gpto3mini'
    version: '2024-05-13'
    format: 'OpenAI'
    capacity: 1
  }
  'gpt-4.5': {
    deploymentName: 'gpt45'
    version: '2024-05-13'
    format: 'OpenAI'
    capacity: 1
  }
}

// Deploy each model
resource modelDeployments 'Microsoft.CognitiveServices/accounts/deployments@2023-05-01' = [for modelName in models: {
  name: '${aiServicesName}/${modelConfigs[modelName].deploymentName}'
  sku: {
    name: 'Standard'
    capacity: modelConfigs[modelName].capacity
  }
  properties: {
    model: {
      name: modelName
      format: modelConfigs[modelName].format
      version: modelConfigs[modelName].version
    }
    raiPolicyName: 'Microsoft.Default'
    versionUpgradeOption: 'OnceCurrentVersionExpired'
  }
}]

// Output the deployment names for reference
output deploymentNames array = [for modelName in models: {
  name: modelConfigs[modelName].deploymentName
  modelName: modelName
  version: modelConfigs[modelName].version
}] 

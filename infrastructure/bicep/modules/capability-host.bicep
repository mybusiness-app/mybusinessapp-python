@description('AI hub name')
param aiHubName string

@description('AI project name')
param aiProjectName string

@description('Name for ACS connection')
param acsConnectionName string

@description('Name for AOAI connection')
param aoaiConnectionName string

@description('Name for capabilityHost')
param capabilityHostName string

var storageConnections = [
  '${aiProjectName}/workspaceblobstore'
]
var aiSearchConnection = [
  acsConnectionName
]
var aiServiceConnections = [
  aoaiConnectionName
]

// Hub Capability Host
resource hubCapabilityHost 'Microsoft.MachineLearningServices/workspaces/capabilityHosts@2024-10-01-preview' = {
  name: '${aiHubName}/${aiHubName}-${capabilityHostName}'
  properties: {
    capabilityHostKind: 'Agents'
  }
}

// Project Capability Host
resource projectCapabilityHost 'Microsoft.MachineLearningServices/workspaces/capabilityHosts@2024-10-01-preview' = {
  name: '${aiProjectName}/${aiProjectName}-${capabilityHostName}'
  properties: {
    capabilityHostKind: 'Agents'
    aiServicesConnections: aiServiceConnections
    vectorStoreConnections: aiSearchConnection
    storageConnections: storageConnections
  }
  dependsOn: [
    hubCapabilityHost
  ]
} 

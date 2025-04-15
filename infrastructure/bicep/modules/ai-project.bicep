@description('Name of the AI Project workspace')
param projectName string

@description('Friendly name for the AI Project')
param projectFriendlyName string = projectName

@description('Description of the AI Project')
param projectDescription string = ''

@description('Azure region for resource deployment')
param location string

@description('Tags to apply to all resources')
param tags object

@description('ID of the AI Hub workspace')
param hubResourceId string

var subscriptionId = subscription().subscriptionId
var resourceGroupName = resourceGroup().name
var projectConnectionString = '${location}.api.azureml.ms;${subscriptionId};${resourceGroupName};${projectName}'

// AI Project Workspace
resource aiProject 'Microsoft.MachineLearningServices/workspaces@2024-10-01-preview' = {
  name: projectName
  location: location
  tags: union(tags, {
    ProjectConnectionString: projectConnectionString
  })
  identity: {
    type: 'SystemAssigned'
  }
  kind: 'Project'
  properties: {
    friendlyName: projectFriendlyName
    description: projectDescription
    hubResourceId: hubResourceId
  }
}

// Default Datastores
// resource artifactStore 'Microsoft.MachineLearningServices/workspaces/datastores@2025-01-01-preview' = {
//   parent: aiProject
//   name: 'workspaceartifactstore'
//   properties: {
//     datastoreType: 'AzureBlob'
//     accountName: split(storageAccountId, '/')[8]
//     containerName: '${aiProject.name}-azureml'
//     endpoint: 'core.windows.net'
//     protocol: 'https'
//     serviceDataAccessAuthIdentity: 'None'
//   }
// }

// resource blobStore 'Microsoft.MachineLearningServices/workspaces/datastores@2025-01-01-preview' = {
//   parent: aiProject
//   name: 'workspaceblobstore'
//   properties: {
//     datastoreType: 'AzureBlob'
//     accountName: split(storageAccountId, '/')[8]
//     containerName: '${aiProject.name}-azureml-blobstore'
//     endpoint: 'core.windows.net'
//     protocol: 'https'
//     serviceDataAccessAuthIdentity: 'WorkspaceSystemAssignedIdentity'
//   }
// }

// resource workingDirectory 'Microsoft.MachineLearningServices/workspaces/datastores@2025-01-01-preview' = {
//   parent: aiProject
//   name: 'workspaceworkingdirectory'
//   properties: {
//     datastoreType: 'AzureFile'
//     accountName: split(storageAccountId, '/')[8]
//     fileShareName: '${aiProject.name}-code'
//     endpoint: 'core.windows.net'
//     protocol: 'https'
//     serviceDataAccessAuthIdentity: 'None'
//   }
// }

// Outputs
output projectId string = aiProject.id
output projectName string = aiProject.name
output projectConnectionString string = projectConnectionString
output projectPrincipalId string = aiProject.identity.principalId
output projectWorkspaceId string = aiProject.properties.workspaceId

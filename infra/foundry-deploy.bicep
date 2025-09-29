// Main bicep template for AI Apps and Agents infrastructure
@description('Location for all resources')
param location string

@description('Application name prefix')
param appName string = 'aiapps-agents'

// Variables
var resourceGroupName = resourceGroup().name
// Create a suffix using the resource group name and subscription ID, safely handling short names
var resourceGroupSuffix = take(replace(guid('${resourceGroupName}-${subscription().subscriptionId}'), '-', ''), 6)
var resourcePrefix = appName
var logAnalyticsName = '${resourcePrefix}-logs-${resourceGroupSuffix}'
var appInsightsName = '${resourcePrefix}-ai-${resourceGroupSuffix}'
var storageAccountName = replace('${resourcePrefix}st${resourceGroupSuffix}', '-', '')
var keyVaultName = '${resourcePrefix}-kv-${resourceGroupSuffix}'

// AI Foundry and Web app service names
var openAiName = '${resourcePrefix}-ai-foundry-${resourceGroupSuffix}'
var aiServicesName = '${resourcePrefix}-aiservices-${resourceGroupSuffix}'
var aiFoundryProjectName = 'foundryProject'

// OpenAI model configurations
var openAiSettings = {
  name: openAiName
  sku: 'S0'
  maxConversationTokens: '100'
  maxCompletionTokens: '500'
  gptModel: {
    name: 'gpt-4o'
    version: '2024-05-13'
    deployment: {
      name: 'gpt-4o'
    }
    sku: {
      name: 'GlobalStandard'
      capacity: 50
    }
  }
  embeddingsModel: {
    name: 'text-embedding-3-small'
    version: '1'
    deployment: {
      name: 'embeddings'
    }
    sku: {
      name: 'Standard'
      capacity: 50
    }
  }
}



// Log Analytics Workspace (required for Application Insights)
resource logAnalytics 'Microsoft.OperationalInsights/workspaces@2022-10-01' = {
  name: logAnalyticsName
  location: location
  properties: {
    sku: {
      name: 'PerGB2018'
    }
    retentionInDays: 30
    features: {
      enableLogAccessUsingOnlyResourcePermissions: true
    }
  }
}

// Application Insights
resource appInsights 'Microsoft.Insights/components@2020-02-02' = {
  name: appInsightsName
  location: location
  kind: 'web'
  properties: {
    Application_Type: 'web'
    WorkspaceResourceId: logAnalytics.id
  }
}

// Storage Account
resource storageAccount 'Microsoft.Storage/storageAccounts@2023-01-01' = {
  name: storageAccountName
  location: location
  sku: {
    name: 'Standard_LRS'
  }
  kind: 'StorageV2'
  properties: {
    defaultToOAuthAuthentication: false
    allowCrossTenantReplication: true
    minimumTlsVersion: 'TLS1_2'
    allowBlobPublicAccess: false
    allowSharedKeyAccess: true
    networkAcls: {
      bypass: 'AzureServices'
      virtualNetworkRules: []
      ipRules: []
      defaultAction: 'Allow'
    }
    supportsHttpsTrafficOnly: true
    encryption: {
      requireInfrastructureEncryption: false
      services: {
        file: {
          keyType: 'Account'
          enabled: true
        }
        blob: {
          keyType: 'Account'
          enabled: true
        }
      }
      keySource: 'Microsoft.Storage'
    }
    accessTier: 'Hot'
  }
}

// Key Vault
resource keyVault 'Microsoft.KeyVault/vaults@2023-02-01' = {
  name: keyVaultName
  location: location
  properties: {
    sku: {
      family: 'A'
      name: 'standard'
    }
    tenantId: subscription().tenantId
    accessPolicies: []
    enabledForDeployment: false
    enabledForDiskEncryption: false
    enabledForTemplateDeployment: true
    enableSoftDelete: true
    softDeleteRetentionInDays: 90
    enableRbacAuthorization: true
    provisioningState: 'Succeeded'
    publicNetworkAccess: 'Enabled'
  }
}



// -----------------------
// Azure AI Foundry Hub
// -----------------------

// AI Services (Multi-service account)
resource aiServices 'Microsoft.CognitiveServices/accounts@2025-06-01' = {
  name: aiServicesName
  location: location
  sku: {
    name: 'S0'
  }
  kind: 'AIServices'
  identity: {
    type: 'SystemAssigned'
  }
  properties: {
    apiProperties: {}
    networkAcls: {
      defaultAction: 'Allow'
      virtualNetworkRules: []
      ipRules: []
    }
    allowProjectManagement: true
    defaultProject: 'foundryProject'
    associatedProjects: [
      'foundryProject'
    ]
    publicNetworkAccess: 'Enabled'
    customSubDomainName: toLower(aiServicesName)
  }
}

// AI Services Project
resource aiServicesProject 'Microsoft.CognitiveServices/accounts/projects@2025-06-01' = {
  parent: aiServices
  name: aiFoundryProjectName
  location: location
  // kind: 'AIServices'
  identity: {
    type: 'SystemAssigned'
  }
  properties: {
    description: 'AI Foundry Project'
    displayName: 'AI Foundry Project'
  }
}


resource openAiEmbeddingsModelDeployment 'Microsoft.CognitiveServices/accounts/deployments@2023-05-01' = {
  parent: aiServices
  name: openAiSettings.embeddingsModel.deployment.name  
  sku: {
    name: openAiSettings.embeddingsModel.sku.name
    capacity: openAiSettings.embeddingsModel.sku.capacity
  }
  properties: {
    model: {
      format: 'OpenAI'
      name: openAiSettings.embeddingsModel.name
      version: openAiSettings.embeddingsModel.version
    }
  }
}

resource openAiGpt4oModelDeployment 'Microsoft.CognitiveServices/accounts/deployments@2023-05-01' = {
  parent: aiServices
  name: openAiSettings.gptModel.deployment.name
  dependsOn: [
    openAiEmbeddingsModelDeployment
  ]
  sku: {
    name: openAiSettings.gptModel.sku.name
    capacity: openAiSettings.gptModel.sku.capacity
  }
  properties: {
    model: {
      format: 'OpenAI'
      name: openAiSettings.gptModel.name
      version: openAiSettings.gptModel.version
    }    
  }
}




// // AI Services Connection to the Hub
// resource aiServicesConnection 'Microsoft.MachineLearningServices/workspaces/connections@2024-07-01-preview' = {
//   parent: aiFoundryHub
//   name: aiServicesName
//   properties: {
//     authType: 'ApiKey'
//     category: 'AIServices'
//     target: 'https://${aiServicesName}.cognitiveservices.azure.com/'
//     useWorkspaceManagedIdentity: true
//     isSharedToAll: true
//     sharedUserList: []
//     peRequirement: 'NotRequired'
//     peStatus: 'NotApplicable'
//     credentials: {
//       key: aiServices.listKeys().key1
//     }
//     metadata: {
//       ApiType: 'Azure'
//       ResourceId: aiServices.id
//     }
//   }
// }

// // Azure OpenAI Connection to the Hub
// resource aoaiConnection 'Microsoft.MachineLearningServices/workspaces/connections@2024-07-01-preview' = {
//   parent: aiFoundryHub
//   name: '${openAiSettings.name}_aoai'
//   properties: {
//     authType: 'ApiKey'
//     category: 'AzureOpenAI'
//     target: 'https://${openAiSettings.name}.openai.azure.com/'
//     useWorkspaceManagedIdentity: true
//     isSharedToAll: true
//     sharedUserList: []
//     peRequirement: 'NotRequired'
//     peStatus: 'NotApplicable'
//     credentials: {
//       key: openAiAccount.listKeys().key1
//     }
//     metadata: {
//       ApiType: 'Azure'
//       ResourceId: openAiAccount.id
//     }
//   }
// }

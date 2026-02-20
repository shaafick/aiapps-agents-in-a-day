// Main bicep template for AI Apps and Agents infrastructure
@description('Location for all resources')
param location string = 'eastus'

@description('Application name prefix')
param appName string = 'aiapps-agents'

@description('MongoDB administrator username')
param mongoDbUserName string = 'aiaaaadmin'

// Variables
var resourcePrefix = '${appName}-s2'
var logAnalyticsName = '${resourcePrefix}-la'
var appInsightsName = '${resourcePrefix}-ai'
var storageAccountName = replace('${resourcePrefix}st', '-', '')
var keyVaultName = '${resourcePrefix}-kv'
var acrName = replace('${resourcePrefix}acr', '-', '')

var cosmosDbAccountName = '${resourcePrefix}-cosmos'
var searchServiceName = '${resourcePrefix}-search'
var mongoClusterName = '${resourcePrefix}-mongo'

// Auto-generate MongoDB password using unique string based on resource group and subscription
var mongoDbPassword = 'Mongo-${uniqueString(resourceGroup().id, subscription().subscriptionId)}-${substring(newGuid(), 0, 8)}!'

var staticWebAppName = '${resourcePrefix}-swa'

// Web app service names
var aspLinuxName = '${resourcePrefix}-asp'
var appSettingName = '${resourcePrefix}-setting'
var appPlaygroundName = '${resourcePrefix}-playground'
var appChatbotFrontendName = '${resourcePrefix}-chatbot'
var appChatbotBackendName = '${resourcePrefix}-chatbot-api'
var appGameServerName = '${resourcePrefix}-game-server'
var appGameClientName = '${resourcePrefix}-game-client'

var openAiName = '${resourcePrefix}-openai'
var aiFoundryWorkspaceName = '${resourcePrefix}-ai-workspace'
var aiFoundryProjectName = '${resourcePrefix}-ai-project'
var aiServicesName = '${resourcePrefix}-aiservices'


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
      name: 'Standard'
      capacity: 300
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
      capacity: 300
    }
  }
  dalleModel: {
    name: 'dall-e-3'
    version: '3.0'
    deployment: {
      name: 'dalle3'
    }
    sku: {
      name: 'Standard'
      capacity: 1
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

// Store MongoDB password in Key Vault
resource mongoPasswordSecret 'Microsoft.KeyVault/vaults/secrets@2023-02-01' = {
  parent: keyVault
  name: 'mongodb-password'
  properties: {
    value: mongoDbPassword
    contentType: 'text/plain'
    attributes: {
      enabled: true
    }
  }
}

// Store MongoDB username in Key Vault
resource mongoUsernameSecret 'Microsoft.KeyVault/vaults/secrets@2023-02-01' = {
  parent: keyVault
  name: 'mongodb-username'
  properties: {
    value: mongoDbUserName
    contentType: 'text/plain'
    attributes: {
      enabled: true
    }
  }
}

// Store MongoDB connection string in Key Vault
resource mongoConnectionStringSecret 'Microsoft.KeyVault/vaults/secrets@2023-02-01' = {
  parent: keyVault
  name: 'mongodb-connectionstring'
  properties: {
    value: mongoCluster.listConnectionStrings().connectionStrings[0].connectionString
    contentType: 'text/plain'
    attributes: {
      enabled: true
    }
  }
  dependsOn: [
    mongoFirewallRulesAllowAzure
    mongoFirewallRulesAllowAll
  ]
}

// Azure Container Registry
resource containerRegistry 'Microsoft.ContainerRegistry/registries@2023-07-01' = {
  name: acrName
  location: location
  sku: {
    name: 'Basic'
  }
  properties: {
    adminUserEnabled: true
    policies: {
      quarantinePolicy: {
        status: 'disabled'
      }
      trustPolicy: {
        type: 'Notary'
        status: 'disabled'
      }
      retentionPolicy: {
        days: 7
        status: 'disabled'
      }
      exportPolicy: {
        status: 'enabled'
      }

    }
    encryption: {
      status: 'disabled'
    }
    dataEndpointEnabled: false
    publicNetworkAccess: 'Enabled'
    networkRuleBypassOptions: 'AzureServices'
    zoneRedundancy: 'Disabled'

  }
}




// -----------------------
// Databases
// -----------------------

// Cosmos DB Account
resource cosmosDbAccount 'Microsoft.DocumentDB/databaseAccounts@2023-04-15' = {
  name: cosmosDbAccountName
  location: location
  kind: 'GlobalDocumentDB'
  properties: {
    enableFreeTier: false
    databaseAccountOfferType: 'Standard'
    consistencyPolicy: {
      defaultConsistencyLevel: 'Session'
    }
    locations: [
      {
        locationName: location
        failoverPriority: 0
        isZoneRedundant: false
      }
    ]
    capabilities: [
      {
        name: 'EnableServerless'
      }
    ]
    backupPolicy: {
      type: 'Periodic'
      periodicModeProperties: {
        backupIntervalInMinutes: 240
        backupRetentionIntervalInHours: 8
        backupStorageRedundancy: 'Local'
      }
    }
  }
}

// Azure AI Search
resource searchService 'Microsoft.Search/searchServices@2023-11-01' = {
  name: searchServiceName
  location: location
  sku: {
    name: 'basic'
  }
  properties: {
    replicaCount: 1
    partitionCount: 1
    hostingMode: 'default'
    publicNetworkAccess: 'enabled'
    networkRuleSet: {
      ipRules: []
    }
    encryptionWithCmk: {
      enforcement: 'Unspecified'
    }
    disableLocalAuth: false
    authOptions: {
      apiKeyOnly: {}
    }
  }
}

// MongoDB vCore Cluster
resource mongoCluster 'Microsoft.DocumentDB/mongoClusters@2023-03-01-preview' = {
  name: mongoClusterName
  location: location
  properties: {
    administratorLogin: mongoDbUserName
    administratorLoginPassword: mongoDbPassword
    serverVersion: '5.0'
    nodeGroupSpecs: [
      {
        kind: 'Shard'
        sku: 'M30'
        diskSizeGB: 128
        enableHa: false
        nodeCount: 1
      }
    ]
  }
}

resource mongoFirewallRulesAllowAzure 'Microsoft.DocumentDB/mongoClusters/firewallRules@2023-03-01-preview' = {
  parent: mongoCluster
  name: 'allowAzure'
  properties: {
    startIpAddress: '0.0.0.0'
    endIpAddress: '0.0.0.0'
  }
}

resource mongoFirewallRulesAllowAll 'Microsoft.DocumentDB/mongoClusters/firewallRules@2023-03-01-preview' = {
  parent: mongoCluster
  name: 'allowAll'
  properties: {
    startIpAddress: '0.0.0.0'
    endIpAddress: '255.255.255.255'
  }
}



// -----------------------
// AI Apps
// -----------------------

// App Service Plan
resource appServicePlanLinux 'Microsoft.Web/serverfarms@2022-03-01' = {
  name: aspLinuxName
  location: location
  sku: {
    name: 'S2'
  }
  kind: 'linux'
  properties: {
    reserved: true
  }
}


resource appSetting 'Microsoft.Web/sites@2022-03-01' = {
  name: appSettingName
  location: location
  properties: {
    serverFarmId: appServicePlanLinux.id
    httpsOnly: true
    siteConfig: {
      linuxFxVersion: 'DOTNETCORE|8.0'
      appCommandLine: 'dotnet SettingApi.dll'
      alwaysOn: true
    }
  }
}

resource appSettingSettings 'Microsoft.Web/sites/config@2022-03-01' = {
  parent: appSetting
  name: 'appsettings'
  kind: 'string'
  properties: {
    APPINSIGHTS_INSTRUMENTATIONKEY: appInsights.properties.InstrumentationKey
  }
}


resource appPlayground 'Microsoft.Web/sites@2022-03-01' = {
  name: appPlaygroundName
  location: location
  properties: {
    serverFarmId: appServicePlanLinux.id
    httpsOnly: true
    siteConfig: {
      linuxFxVersion: 'NODE|20-lts'
      appCommandLine: 'pm2 serve /home/site/wwwroot/dist --no-daemon --spa'
      alwaysOn: true
    }
  }
}

resource appPlaygroundSettings 'Microsoft.Web/sites/config@2022-03-01' = {
  parent: appPlayground
  name: 'appsettings'
  kind: 'string'
  properties: {
    APPINSIGHTS_INSTRUMENTATIONKEY: appInsights.properties.InstrumentationKey
  }
}

resource appChatbotBackend 'Microsoft.Web/sites@2022-03-01' = {
  name: appChatbotBackendName
  location: location
  properties: {
    serverFarmId: appServicePlanLinux.id
    httpsOnly: true
    siteConfig: {
      linuxFxVersion: 'NODE|20-lts'
      appCommandLine: 'pm2 start app.js --no-daemon'
      alwaysOn: true
    }
  }
}

resource appChatbotBackendSettings 'Microsoft.Web/sites/config@2022-03-01' = {
  parent: appChatbotBackend
  name: 'appsettings'
  kind: 'string'
  properties: {
    APPINSIGHTS_INSTRUMENTATIONKEY: appInsights.properties.InstrumentationKey
  }
}

resource appChatbotFrontend 'Microsoft.Web/sites@2022-03-01' = {
  name: appChatbotFrontendName
  location: location
  properties: {
    serverFarmId: appServicePlanLinux.id
    httpsOnly: true
    siteConfig: {
      linuxFxVersion: 'NODE|20-lts'
      appCommandLine: 'pm2 serve /home/site/wwwroot/dist --no-daemon --spa'
      alwaysOn: true
    }
  }
}

resource appChatbotFrontendSettings 'Microsoft.Web/sites/config@2022-03-01' = {
  parent: appChatbotFrontend
  name: 'appsettings'
  kind: 'string'
  properties: {
    APPINSIGHTS_INSTRUMENTATIONKEY: appInsights.properties.InstrumentationKey
  }
}


resource appGameServer 'Microsoft.Web/sites@2022-03-01' = {
  name: appGameServerName
  location: location
  properties: {
    serverFarmId: appServicePlanLinux.id
    httpsOnly: true
    siteConfig: {
      linuxFxVersion: 'DOTNETCORE|8.0'
      appCommandLine: 'dotnet PsrGameServer.dll'
      alwaysOn: true
    }
  }
}

resource appGameServerSettings 'Microsoft.Web/sites/config@2022-03-01' = {
  parent: appGameServer
  name: 'appsettings'
  kind: 'string'
  properties: {
    APPINSIGHTS_INSTRUMENTATIONKEY: appInsights.properties.InstrumentationKey
  }
}


resource appGameClient 'Microsoft.Web/sites@2022-03-01' = {
  name: appGameClientName
  location: location
  properties: {
    serverFarmId: appServicePlanLinux.id
    httpsOnly: true
    siteConfig: {
      linuxFxVersion: 'NODE|20-lts'
      appCommandLine: 'pm2 start server.js --no-daemon'
      alwaysOn: true
    }
  }
}

resource appGameClientSettings 'Microsoft.Web/sites/config@2022-03-01' = {
  parent: appGameClient
  name: 'appsettings'
  kind: 'string'
  properties: {
    APPINSIGHTS_INSTRUMENTATIONKEY: appInsights.properties.InstrumentationKey
  }
}



// Static Web App
resource staticWebApp 'Microsoft.Web/staticSites@2022-09-01' = {
  name: staticWebAppName
  location: 'EastUS2'
  sku: {
    name: 'Free'
    tier: 'Free'
    size: 'Free'
    family: 'Free'
    capacity: 0
  }
  properties: {
    repositoryUrl: ''
    branch: ''
    buildProperties: {
      appLocation: '/apps-rps/rps-game-client'
      apiLocation: ''
      outputLocation: 'dist'
    }
    stagingEnvironmentPolicy: 'Enabled'
    allowConfigFileUpdates: true
    provider: 'None'
    enterpriseGradeCdnStatus: 'Disabled'
  }
}



// -----------------------
// AI Services
// -----------------------

// AI Services (Multi-service account)
resource aiServices 'Microsoft.CognitiveServices/accounts@2023-05-01' = {
  name: aiServicesName
  location: location
  sku: {
    name: 'S0'
  }
  kind: 'AIServices'
  properties: {
    publicNetworkAccess: 'Enabled'
    customSubDomainName: toLower(aiServicesName)
    apiProperties: {}
  }
}


resource aiServiceGpt4oModelDeployment 'Microsoft.CognitiveServices/accounts/deployments@2023-05-01' = {
  parent: aiServices
  name: openAiSettings.gptModel.deployment.name
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

// Azure OpenAI Service
resource openAiAccount 'Microsoft.CognitiveServices/accounts@2023-05-01' = {
  name: openAiSettings.name
  location: location
  sku: {
    name: openAiSettings.sku    
  }
  kind: 'OpenAI'
  properties: {
    customSubDomainName: openAiSettings.name
    publicNetworkAccess: 'Enabled'
  }
}

resource openAiEmbeddingsModelDeployment 'Microsoft.CognitiveServices/accounts/deployments@2023-05-01' = {
  parent: openAiAccount
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
  parent: openAiAccount
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


resource openAiDalleModelDeployment 'Microsoft.CognitiveServices/accounts/deployments@2023-05-01' = {
  parent: openAiAccount
  name: openAiSettings.dalleModel.deployment.name
  dependsOn: [
    openAiEmbeddingsModelDeployment
    openAiGpt4oModelDeployment
  ]
  sku: {
    name: openAiSettings.dalleModel.sku.name
    capacity: openAiSettings.dalleModel.sku.capacity
  }
  properties: {
    model: {
      format: 'OpenAI'
      name: openAiSettings.dalleModel.name
      version: openAiSettings.dalleModel.version
    }    
  }
}

// Computer Vision Service
resource computerVision 'Microsoft.CognitiveServices/accounts@2023-05-01' = {
  name: '${resourcePrefix}-cv'
  location: location
  kind: 'ComputerVision'
  properties: {
    customSubDomainName: '${resourcePrefix}-cv'
    publicNetworkAccess: 'Enabled'
  }
  sku: {
    name: 'S1'
  }
}

// Speech Service
resource speechService 'Microsoft.CognitiveServices/accounts@2021-04-30' = {
  name: '${resourcePrefix}-speech'
  location: location
  kind: 'SpeechServices'
  sku: {
    name: 'S0'
  }
  properties: {
    apiProperties: {
      qnaRuntimeEndpoint: 'https://${resourcePrefix}-speech.api.cognitive.microsoft.com'
    }
  }
}

// Translator Service
resource translatorService 'Microsoft.CognitiveServices/accounts@2021-04-30' = {
  name: '${resourcePrefix}-translator'
  location: location
  kind: 'TextTranslation'
  sku: {
    name: 'S1'
  }
  properties: {
    apiProperties: {
      qnaRuntimeEndpoint: 'https://${resourcePrefix}-translator.api.cognitive.microsoft.com'
    }
  }
}


// -----------------------
// Microsoft Foundry Hub
// -----------------------

// Microsoft Foundry Hub Workspace
resource aiFoundryHub 'Microsoft.MachineLearningServices/workspaces@2024-04-01-preview' = {
  name: aiFoundryWorkspaceName
  location: location
  kind: 'Hub'
  identity: {
    type: 'SystemAssigned'
  }
  properties: {
    friendlyName: aiFoundryWorkspaceName
    storageAccount: storageAccount.id
    keyVault: keyVault.id
    publicNetworkAccess: 'Enabled'
    managedNetwork: {
      isolationMode: 'Disabled'
    }
    workspaceHubConfig: {
      defaultWorkspaceResourceGroup: resourceGroup().id
    }
  }
  dependsOn: [
    aiServices
  ]
}

// AI Services Connection to the Hub
resource aiServicesConnection 'Microsoft.MachineLearningServices/workspaces/connections@2024-07-01-preview' = {
  parent: aiFoundryHub
  name: aiServicesName
  properties: {
    authType: 'ApiKey'
    category: 'AIServices'
    target: 'https://${aiServicesName}.cognitiveservices.azure.com/'
    useWorkspaceManagedIdentity: true
    isSharedToAll: true
    sharedUserList: []
    peRequirement: 'NotRequired'
    peStatus: 'NotApplicable'
    credentials: {
      key: aiServices.listKeys().key1
    }
    metadata: {
      ApiType: 'Azure'
      ResourceId: aiServices.id
    }
  }
}

// Azure OpenAI Connection to the Hub
resource aoaiConnection 'Microsoft.MachineLearningServices/workspaces/connections@2024-07-01-preview' = {
  parent: aiFoundryHub
  name: '${openAiSettings.name}_aoai'
  properties: {
    authType: 'ApiKey'
    category: 'AzureOpenAI'
    target: 'https://${openAiSettings.name}.openai.azure.com/'
    useWorkspaceManagedIdentity: true
    isSharedToAll: true
    sharedUserList: []
    peRequirement: 'NotRequired'
    peStatus: 'NotApplicable'
    credentials: {
      key: openAiAccount.listKeys().key1
    }
    metadata: {
      ApiType: 'Azure'
      ResourceId: openAiAccount.id
    }
  }
}

// Microsoft Foundry Project Workspace
resource aiFoundryProject 'Microsoft.MachineLearningServices/workspaces@2024-04-01-preview' = {
  name: aiFoundryProjectName
  location: location
  kind: 'Project'
  identity: {
    type: 'SystemAssigned'
  }
  properties: {
    friendlyName: aiFoundryProjectName
    hubResourceId: aiFoundryHub.id
    publicNetworkAccess: 'Enabled'
  }
}

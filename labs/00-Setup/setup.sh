#!/bin/bash
# chmod +x setup.sh
# ./setup.sh

# Define the search and replace pairs
declare -A replacements=(
    ["<DEV_Name>"]="lab2user325@aiapps.top"
    ["<MONGODB_CONNECTION_STRING>"]="mongodb+srv://aiaaaadmin:Pswd6202@aiaaa-s2-mongo.global.mongocluster.cosmos.azure.com/?tls=true&authMechanism=SCRAM-SHA-256&retrywrites=false&maxIdleTimeMS=120000"
    ["<AZURE_OPENAI_API_INSTANCE_NAME>"]="aiaaa-s2-openai"
    ["<AZURE_OPENAI_API_ENDPOINT>"]="https://aiaaa-s2-openai.openai.azure.com/"
    ["<AZURE_OPENAI_API_KEY>"]="8d91f222533647a488602ebc75e7a180"
    ["<AZURE_OPENAI_API_DEPLOYMENT_NAME>"]="gpt-4.1"
    ["<AZURE_OPENAI_API_EMBEDDINGS_DEPLOYMENT_NAME>"]="embeddings"
    ["<AZURE_OPENAI_API_VERSION>"]="2024-10-21"
    ["<AI_PROXY_PLAYGROUND_URL>"]="https://aiaaa-s2-playground.azurewebsites.net"
    ["<COMPUTER_VISION_ENDPOINT>"]="https://aiaaa-s2-cv.cognitiveservices.azure.com/"
    ["<COMPUTER_VISION_API_KEY>"]="33e6501c20c94efb95d23a0c8c2072d2"
    ["<TRANSLATOR_SERVICE_ENDPOINT>"]="https://api.cognitive.microsofttranslator.com/translate?api-version=3.0"
    ["<TRANSLATOR_SERVICE_API_KEY>"]="adfa2a6b11884e499f369a8f44f58b29"
    ["<SPEECH_SERVICE_ENDPOINT>"]="https://eastus.api.cognitive.microsoft.com/"
    ["<SPEECH_SERVICE_API_KEY>"]="c8f3837d26bd42ef81838019c9528de4"
    ["<AZURE_FOUNDRY_PROJECT_ENDPOINT>"]="https://aiaaa-s2-aiservices.services.ai.azure.com/api/projects/foundryProject"
    ["<APPLICATIONINSIGHTS_CONNECTION_STRING>"]="InstrumentationKey=27f9b8f3-6c54-4ee4-8f06-c3e0060a772f;IngestionEndpoint=https://eastus-8.in.applicationinsights.azure.com/;LiveEndpoint=https://eastus.livediagnostics.monitor.azure.com/;ApplicationId=ea69b9cd-9c73-408c-863f-e24d50672647"
)

# Check if parent directory exists
if [ ! -d "../" ]; then
    echo "Parent directory not found!"
    exit 1
fi

echo "Searching for .env and .js files..."

# Find .env and .js files in parent directory 
#  -o -name "*.js"
find ../../ -type f \( -name "*.env" -o -name "*-openai-sdk*" \) -not -path "*/node_modules/*" | while read -r file; do
    echo "Processing: $file"
    for search in "${!replacements[@]}"; do
        # replace="${replacements[$search]}"
        replace=$(echo "${replacements[$search]}" | sed 's/&/\\&/g')
        sed -i "s|${search}|${replace}|g" "$file"
    done
done

echo "Replacements complete!"
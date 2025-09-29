#!/bin/bash
# chmod +x setup.sh
# ./setup.sh

# Define the search and replace pairs
declare -A replacements=(
    ["<DEV_Name>"]="add_value"
    ["<MONGODB_CONNECTION_STRING>"]="add_value"
    ["<AZURE_OPENAI_API_INSTANCE_NAME>"]="aiaaa-s2-openai"
    ["<AZURE_OPENAI_API_KEY>"]="add_value"
    # see examples below
    # ["<DEV_Name>"]="dev_daniel_66"
    # ["<MONGODB_CONNECTION_STRING>"]="mongodb+srv://aiaaaadmin:aiaaapassword123@arg-syd-aiaaa-mongo.global.mongocluster.cosmos.azure.com/?tls=true&authMechanism=SCRAM-SHA-256&retrywrites=false&maxIdleTimeMS=120000"
    # ["<AZURE_OPENAI_API_INSTANCE_NAME>"]="aiaaa-s2-openai"
    # ["<AZURE_OPENAI_API_KEY>"]=""
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
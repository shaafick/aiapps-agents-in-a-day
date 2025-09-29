
CONFIG_URL="https://aiaaa-s2-setting.azurewebsites.net/api/configuration/all"

 # please edit below to your assigned user name
DEV_Name="lab1user310"
# DEV_Name="lab1user310"

echo "Fetching configuration from $CONFIG_URL..."
config_json=$(curl -s "$CONFIG_URL")

if [ -z "$config_json" ]; then
    echo "Failed to fetch configuration."
    exit 1
fi

# Save fetched data to config.json
# echo "Saving configuration to config.json..."
# echo "$config_json" > config.json
# echo "Configuration saved to config.json"

# Extract all key-value pairs from the JSON
declare -A replacements

# Parse JSON manually - extract configurations array content
configs=$(echo "$config_json" | sed -n 's/.*"configurations":\s*\[\(.*\)\].*/\1/p' | sed 's/},\s*{/}\n{/g')

# Process each configuration object
while IFS= read -r config; do
    if [[ -n "$config" ]]; then
        # Extract key and value using sed
        key=$(echo "$config" | sed -n 's/.*"key":\s*"\([^"]*\)".*/\1/p')
        value=$(echo "$config" | sed -n 's/.*"value":\s*"\([^"]*\)".*/\1/p')
        
        if [[ -n "$key" && -n "$value" ]]; then
            replacements["<$key>"]="$value"
        fi
    fi
done <<< "$configs"

replacements["<DEV_Name>"]="${DEV_Name}"

# Print all items in replacements array
# echo "Found ${#replacements[@]} configuration items:"
# for key in "${!replacements[@]}"; do
#     echo "  $key = ${replacements[$key]}"
# done
# echo ""

echo "Searching for .env files..."

find ../../ -type f \( -name "*.env" -o -name "*-openai-sdk*" \) -not -path "*/node_modules/*" | while read -r file; do
    echo "Processing: $file"
    for search in "${!replacements[@]}"; do
        replace=$(echo "${replacements[$search]}" | sed 's/&/\\&/g')
        # echo "${search}->${replace}"
        sed -i "s|${search}|${replace}|g" "$file"
    done
done

echo "Replacements complete!"



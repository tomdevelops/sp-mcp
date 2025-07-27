#!/bin/bash

# Get the directory of this script and project root
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# Read manifest to get plugin name and version
MANIFEST_FILE="$PROJECT_ROOT/manifest.json"

if [ ! -f "$MANIFEST_FILE" ]; then
    echo "Error: manifest.json not found in $PROJECT_ROOT"
    exit 1
fi

# Extract id and version from manifest.json using jq (or sed as fallback)
if command -v jq &> /dev/null; then
    PLUGIN_ID=$(jq -r '.id' "$MANIFEST_FILE")
    PLUGIN_VERSION=$(jq -r '.version' "$MANIFEST_FILE")
else
    # Fallback using sed (less robust but works without jq)
    PLUGIN_ID=$(sed -n 's/.*"id"[[:space:]]*:[[:space:]]*"\([^"]*\)".*/\1/p' "$MANIFEST_FILE")
    PLUGIN_VERSION=$(sed -n 's/.*"version"[[:space:]]*:[[:space:]]*"\([^"]*\)".*/\1/p' "$MANIFEST_FILE")
fi

if [ -z "$PLUGIN_ID" ] || [ -z "$PLUGIN_VERSION" ]; then
    echo "Error: Could not extract id or version from manifest.json"
    exit 1
fi

OUTPUT_FILE="$PROJECT_ROOT/${PLUGIN_ID}-v${PLUGIN_VERSION}.zip"

# Remove existing zip file if it exists
[ -f "$OUTPUT_FILE" ] && rm "$OUTPUT_FILE"

# Files to include in the plugin package
FILES_TO_PACKAGE=(
    "icon.svg"
    "plugin.js"
    "README.md"
    "index.html"
    "manifest.json"
)

# Check if all required files exist
for file in "${FILES_TO_PACKAGE[@]}"; do
    if [ ! -f "$PROJECT_ROOT/$file" ]; then
        echo "Error: Required file $file not found in $PROJECT_ROOT"
        exit 1
    fi
done

# Create the zip file with maximum compression
cd "$PROJECT_ROOT"
zip -9 "$OUTPUT_FILE" "${FILES_TO_PACKAGE[@]}"

# Get file size and display results
if [ -f "$OUTPUT_FILE" ]; then
    FILE_SIZE=$(stat -c%s "$OUTPUT_FILE")
    SIZE_KB=$(echo "scale=2; $FILE_SIZE / 1024" | bc -l 2>/dev/null || echo "$((FILE_SIZE / 1024))")

    echo "Plugin packaged successfully: $(basename "$OUTPUT_FILE")"
    echo "Total size: ${SIZE_KB} KB"
else
    echo "Error: Failed to create zip file"
    exit 1
fi
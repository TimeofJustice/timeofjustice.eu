import json

# Read the JSON file with the appropriate encoding
with open('data.json', 'r', encoding='utf-16') as file:
    data = json.load(file)

# Write the data back to a new JSON file with UTF-8 encoding
with open('data_utf8.json', 'w', encoding='utf-8') as file:
    json.dump(data, file, ensure_ascii=False)


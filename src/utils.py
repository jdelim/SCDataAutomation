import json

def create_mapping(json_column_name: str) -> dict:
    mappings = {}
    with open('mappings/key_ids.json', 'r') as f:
        data = json.load(f)
        
    jsonData = data[json_column_name.lower()]
    
    keys = jsonData.keys()
    values = jsonData.values()
    
    mappings = dict(zip(keys, values))
    
    return mappings
        
        
def main():
    print(create_mapping('organization'))

if __name__ == "__main__":
    main()
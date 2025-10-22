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
        
def load_column_synonyms(json_file_path: str = 'mappings/column_synonyms.json') -> dict[str, list[str]]:
    with open(json_file_path, 'r', encoding='utf-8') as f:
        return json.load(f)
        
def normalize(val: str) -> str:
    val = val.lower().strip()
    val = val.replace("and/or", "or")
    val = val.replace("-", " ")
    return " ".join(val.split())  # collapse extra spaces

def main():
    #print(create_mapping('organization'))
    pass
if __name__ == "__main__":
    main()
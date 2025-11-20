import json
from connection import *
import pandas as pd

def export_mappings(conn, file_path='mappings/key_ids.json'): # TODO add error handling
    mappings = {}
    query_map = {
        "ethnicity_id": "SELECT ETHNICITY_NAME, ETHNICITY_ID FROM ETHNICITY;",
        "gender_id": "SELECT GENDER_TAG, GENDER_ID FROM GENDER;",
        "org_id": "SELECT ORG_NAME, ORG_ID FROM ORGANIZATION;"
    }
    cur = conn.cursor()

    # retrieve values
    for key, query in query_map.items():
        cur.execute(query)
        rows = cur.fetchall()
        # convert tuples (rows) to dict and store w/ its key
        mappings[key] = {}
        for name, id in rows:
            mappings[key][name] = id
    
    # save mappings to json
    with open(file_path, "w") as f:
        json.dump(mappings, f, indent=2)

def main():
    conn = make_connection(find_env_variables())
    export_mappings(conn)

if __name__ == "__main__":
    main()
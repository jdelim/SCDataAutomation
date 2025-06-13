from snowflake.core import Root
import snowflake.connector
import os
from dotenv import find_dotenv, load_dotenv

dotenv_path = find_dotenv()
# load up entries as env variables
load_dotenv(dotenv_path)
user = os.getenv("user")
account = os.getenv("account")
private_key_path = os.getenv("private_key_path")

# read private key
with open(private_key_path, "rb") as key_file:
    private_key_bytes = key_file.read()

# use this for now bc TOML file not being identified
conn = snowflake.connector.connect(
    user=user,
    account=account,
    private_key=private_key_bytes,
    warehouse='COMPUTE_WH',
    database='STEAMCODERS',
    schema='STEAM_DATA_STAGING'
    )
root = Root(conn)

def InsertEvent(file_name, event_id, start_date, end_date):
    """
    Inserts a row into the EVENT table in Snowflake.
    """
    try:
        cursor = conn.cursor()

        insert_query = """
            INSERT INTO STG_EVENT (EVENT_ID, EVENT_NAME, EVENT_START_DATE, EVENT_END_DATE)
            VALUES (%s, %s, %s, %s)
        """
        cursor.execute(insert_query, (event_id, file_name, start_date, end_date))
        print(f"Inserted event '{file_name}' with ID {event_id} successfully.")
    except Exception as e:
        print(f"Failed to insert event: {e}")
    finally:
        cursor.close()

print("Connection successful!")
print("Account: ", conn.account)
print("User: ", conn.user)
print("Warehouse: ", conn.warehouse)
print("Database: ", conn.database)
print("Schema: ", conn.schema)

InsertEvent("Caltech Y Robotics 2024 Summer Session", 3500, "2024-07-01", "2024-07-19")

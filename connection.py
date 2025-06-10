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

print("Connection successful!")
print("Account: ", conn.account)
print("User: ", conn.user)
print("Warehouse: ", conn.warehouse)
print("Database: ", conn.database)
print("Schema: ", conn.schema)

<<<<<<< HEAD
from snowflake import Root
from snowflake.snowspark import Session
=======
from snowflake.core import Root
import snowflake.connector
import os
from dotenv import find_dotenv, load_dotenv
>>>>>>> 3d7b89ba6ff0eec08cf9244749ebc54bc69598a4

dotenv_path = find_dotenv()
# load up entries as env variables
load_dotenv(dotenv_path)
user = os.getenv("user")
password = os.getenv("password")
account = os.getenv("account")

# use this for now bc TOML file not being identified
conn = snowflake.connector.connect(
    user=user,
    password=password,
    account=account,
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

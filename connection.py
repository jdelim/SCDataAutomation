from snowflake.core import Root
import snowflake.connector
import os
from dotenv import find_dotenv, load_dotenv

USER, ACCOUNT, PRIVATE_KEY_PATH = 'user', 'account', 'private_key_path'
WAREHOUSE, DATABASE, SCHEMA = 'COMPUTE_WH', 'STEAMCODERS', 'STEAM_DATA_STAGING'

    
def find_env_variables() -> list[str]: # user, account, privateKeyBytes
    try:
        env_variables = []
        dotenv_path = find_dotenv()
        if not dotenv_path:
            raise FileNotFoundError(".env file not found!")
        
        load_dotenv(dotenv_path)
        
        user = os.getenv(USER)
        account = os.getenv(ACCOUNT)
        private_key_path = os.getenv(PRIVATE_KEY_PATH)
        
        if not user or not account or not private_key_path:
            raise ValueError("Missing one or more env variables!")
        
        if not os.path.exists(private_key_path):
            raise FileNotFoundError(f"Private key not found at: {private_key_path}!")
        
        # parse privateKeyPath as bytes
        with open(private_key_path, "rb") as key_file:
            private_key_bytes = key_file.read()
        
        env_variables.extend([user, account, private_key_bytes, WAREHOUSE, DATABASE, SCHEMA])

        return env_variables
    
    except (FileNotFoundError, ValueError) as e:
        print(f"Configuration error: {e}")
        raise
    except OSError as e:
        print(f"File access error: {e}")
        raise
    except Exception as e:
        print(f"Unexpected error: {e}")
        raise
    
    

def make_connection(env_variables: list[str]):
    try:
        # check for length and empty strings
        if len(env_variables) < 6:
            raise ValueError(
                f"Expected 6 connection parameters, got {len(env_variables)}"
            )
    
        user, account, private_key, warehouse, database, schema = env_variables
        
        if not all([user, account, warehouse, database, schema]) or private_key is None:
            raise ValueError("One or more connection parameters is missing!")
        
        conn = snowflake.connector.connect(
        user=user,
        account=account,
        private_key=private_key,
        warehouse=warehouse,
        database=database,
        schema=schema
        )
        
        return conn
    
    except ValueError as e:
        print(f"Configuration error: {e}")
        raise
    except snowflake.connector.errors.Error as e:
        print(f"Snowflake connection error: {e}")
        raise ConnectionError("Failed to connect to Snowflake") from e
    except Exception as e:
        print(f"Unexpected error: {e}")
        raise


def main():
    my_variables = find_env_variables()
    conn = make_connection(my_variables)
    print("Account: ", conn.account)
    print("User: ", conn.user)
    print("Warehouse: ", conn.warehouse)
    print("Database: ", conn.database)
    print("Schema: ", conn.schema)
    
if __name__ == "__main__":
    main()

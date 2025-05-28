from snowflake.core import Root
from snowflake.snowspark import Session

session = Session.builder.config("connection_test", "myconnection").create()
root = Root(session)
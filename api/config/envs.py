import os
from dotenv import load_dotenv


if os.path.exists(".env"):
    load_dotenv(".env")

CLIENT_ID = os.getenv("AzureWebJobsStorage__clientId") or None

INTERNAL_SECRET = os.getenv("INTERNAL_SECRET") or ""
if not INTERNAL_SECRET:
    raise Exception("No INTERNAL_SECRET")

STORAGE_CONTAINER_NAME: str = os.getenv("STORAGE_CONTAINER_NAME") or ""
if not STORAGE_CONTAINER_NAME:
    raise Exception("No STORAGE_CONTAINER_NAME")

CONFIG_BLOB_NAME: str = os.getenv("CONFIG_BLOB_NAME") or ""
if not CONFIG_BLOB_NAME:
    raise Exception("No CONFIG_BLOB_NAME")

QUERY_BLOB_NAME: str = os.getenv("QUERY_BLOB_NAME") or ""
if not QUERY_BLOB_NAME:
    raise Exception("No QUERY_BLOB_NAME")

DATABASE_CONNECTION_STRING: str = os.getenv("DATABASE_CONNECTION_STRING") or ""
if not DATABASE_CONNECTION_STRING:
    raise Exception("No DATABASE_CONNECTION_STRING")

account_name: str = os.getenv("AzureWebJobsStorage__accountName") or ""
if not account_name:
    raise Exception("No STORAGE_CONNECTION_STRING")
STORAGE_ACCOUNT_URI = f"https://{account_name}.blob.core.windows.net"

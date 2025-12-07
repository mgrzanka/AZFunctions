import os
from dotenv import load_dotenv


if os.path.exists(".env"):
    load_dotenv(".env")

CLIENT_ID = os.getenv("AzureWebJobsStorage__clientId") or None
ACCOUNT_NAME: str = os.getenv("AzureWebJobsStorage__accountName") or ""
if not ACCOUNT_NAME:
    raise Exception("No STORAGE_CONNECTION_STRING")

STORAGE_CONTAINER_NAME: str = os.getenv("STORAGE_CONTAINER_NAME") or ""
if not STORAGE_CONTAINER_NAME:
    raise Exception("No STORAGE_CONTAINER_NAME")

CONFIG_BLOB_NAME: str = os.getenv("CONFIG_BLOB_NAME") or ""
if not CONFIG_BLOB_NAME:
    raise Exception("No CONFIG_BLOB_NAME")

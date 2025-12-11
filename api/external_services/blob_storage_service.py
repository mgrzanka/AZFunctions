from azure.storage.blob import BlobServiceClient, ContainerClient, StorageStreamDownloader
from azure.identity import DefaultAzureCredential
from azure.core.exceptions import ResourceNotFoundError

from api.config.envs import STORAGE_ACCOUNT_URI, CLIENT_ID, STORAGE_CONTAINER_NAME


def create_blob_service() -> 'BlobService':
    return BlobService(STORAGE_ACCOUNT_URI, STORAGE_CONTAINER_NAME, CLIENT_ID)


class BlobService:
    def __init__(self, storage_account_uri: str, container_name: str, client_id: str | None = None) -> None:
        if client_id:
            credential = DefaultAzureCredential(managed_identity_client_id=client_id)
        else:
            credential = DefaultAzureCredential()

        self.blob_service_client: BlobServiceClient = \
            BlobServiceClient(storage_account_uri, credential=credential)
        self.container_client: ContainerClient = \
            self.blob_service_client.get_container_client(container_name)

    def download_blob(self, blob_name: str) -> bytes:
        try:
            blob_stream: StorageStreamDownloader = self.container_client.download_blob(blob_name)
            blob_data: bytes = blob_stream.readall()
            return blob_data
        except ResourceNotFoundError as e:
            print("Non-existing blob file")
            raise e

    def close(self):
        self.blob_service_client.close()

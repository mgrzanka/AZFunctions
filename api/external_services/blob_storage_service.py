from azure.storage.blob import BlobServiceClient, ContainerClient, StorageStreamDownloader
from azure.identity import DefaultAzureCredential
from azure.core.exceptions import ResourceNotFoundError


class BlobService:
    def __init__(self, account_name: str, container_name: str, client_id: str | None = None) -> None:
        account_url = f"https://{account_name}.blob.core.windows.net"
        if client_id:
            credential = DefaultAzureCredential(managed_identity_client_id=client_id)
        else:
            credential = DefaultAzureCredential()

        self.blob_service_client: BlobServiceClient = \
            BlobServiceClient(account_url, credential=credential)
        self.container_client: ContainerClient = \
            self.blob_service_client.get_container_client(container_name)

    def download_blob(self, blob_name: str) -> bytes:
        try:
            print("Dowloading config file...")
            blob_stream: StorageStreamDownloader = self.container_client.download_blob(blob_name)
            blob_data: bytes = blob_stream.readall()
            print("Config file dowloaded...")
            return blob_data
        except ResourceNotFoundError as e:
            print("Non-existing blob file")
            raise e

    def close(self):
        self.blob_service_client.close()

from typing import cast
from typing_extensions import Self


class BlobHolderService:
    _instance: 'BlobHolderService | None' = None

    def __new__(cls, *args, **kwargs) -> Self:
        if not cls._instance:
            cls._instance = super().__new__(cls, *args, **kwargs)
            cls._instance._blob_cache = {}
        return cast(Self, cls._instance)

    def update_blob_content(self, blobname: str, content: str):
        self._blob_cache[blobname] = content

    def get_blob_content(self, blobname: str):
        return self._blob_cache.get(blobname)

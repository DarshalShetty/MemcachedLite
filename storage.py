import os
from abc import ABC, abstractmethod

from server_config import SERVER_STORAGE_DIR
from response_parse import RetrievalResponse, ResponseValue, StorageResponse, DeleteResponse


class AbstractStorage(ABC):
    @abstractmethod
    def get(self, keys: [str]) -> bytes:
        raise NotImplementedError()

    @abstractmethod
    def set(self, key: str, value: bytes, value_size_bytes: int) -> bytes:
        raise NotImplementedError()


class FileStorage(AbstractStorage):
    def __init__(self):
        try:
            os.mkdir(SERVER_STORAGE_DIR)
        except FileExistsError as e:
            pass

    def get(self, keys: [str]) -> RetrievalResponse:
        values = []
        for key in keys:
            file_name = f"{SERVER_STORAGE_DIR}/{key}"
            if os.path.exists(file_name):
                with open(file_name, 'rb') as fh:
                    value = fh.read(-1)
                    val_size_bytes = len(value)
                    values.append(ResponseValue(key, val_size_bytes, value))
        return RetrievalResponse(values)

    def set(self, key: str, value: bytes, value_size_bytes: int) -> StorageResponse:
        with open(f"{SERVER_STORAGE_DIR}/{key}", 'wb') as fh:
            fh.write(value)
            return StorageResponse("STORED")

    def delete(self, key:str) -> DeleteResponse:
        file_name = f"{SERVER_STORAGE_DIR}/{key}"
        if os.path.exists(file_name):
            os.unlink(file_name)
            return DeleteResponse('DELETED')
        return DeleteResponse('NOT_FOUND')

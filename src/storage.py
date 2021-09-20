import os
from abc import ABC, abstractmethod

from server_config import SERVER_STORAGE_DIR
from src.response_parse import RetrievalResponse, ResponseValue, StorageResponse


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
        dummy_value = b"this is a value"
        return RetrievalResponse(
            [ResponseValue(key, len(dummy_value), dummy_value) for key in keys])

    def set(self, key: str, value: bytes, value_size_bytes: int):
        return StorageResponse("STORED")

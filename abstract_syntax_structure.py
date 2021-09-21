from abc import ABC, abstractmethod
from typing import BinaryIO


class AbstractSyntaxStructure(ABC):
    name: str

    @abstractmethod
    def to_concrete_syntax(self) -> bytes:
        return NotImplemented

    @classmethod
    @abstractmethod
    def parse(cls, current_buffer: bytes, concrete_syntax_stream: BinaryIO) -> 'AbstractSyntaxStructure':
        return NotImplemented

import re
from dataclasses import dataclass
from typing import BinaryIO, Union, Literal
from abstract_syntax_structure import AbstractSyntaxStructure


@dataclass
class ResponseValue:
    name = 'VALUE'
    key: str
    value_size_bytes: int
    value: bytes

    def to_concrete_syntax(self) -> bytes:
        return f"{self.name} {self.key} {self.value_size_bytes}\r\n".encode('utf-8') + \
               self.value + b'\r\n'


@dataclass
class RetrievalResponse(AbstractSyntaxStructure):
    name = 'VALUE'
    values: [ResponseValue]

    parsing_regex = re.compile(r"^VALUE\s+(?P<key>\S+)\s+(?P<value_size_bytes>\d+)$")

    def to_concrete_syntax(self) -> bytes:
        return b''.join([value.to_concrete_syntax() for value in self.values]) + b'END\r\n'

    @classmethod
    def parse(cls, current_buffer, concrete_syntax_stream) -> 'RetrievalResponse':
        values = []
        response_str = current_buffer.decode('utf-8').strip()
        while response_str != "END":
            response_match = cls.parsing_regex.search(response_str)
            if not response_match:
                raise ResponseParseException(f"Invalid MCLite retrieval command response value: {response_str}")

            value_size_bytes = int(response_match.group("value_size_bytes"))
            value = concrete_syntax_stream.read(value_size_bytes)

            if concrete_syntax_stream.read(2) != b"\r\n":
                raise ResponseParseException(
                    "Either incorrect value size specified or value data block doesn't end with CRLF")

            values.append(ResponseValue(response_match.group('key'), value_size_bytes, value))
            response_str = concrete_syntax_stream.readline().decode('utf-8').strip()

        return RetrievalResponse(values)


@dataclass
class StorageResponse(AbstractSyntaxStructure):
    name: str

    possible_values = "STORED", "NOT_STORED"

    def to_concrete_syntax(self) -> bytes:
        return f"{self.name}\r\n".encode('utf-8')

    @classmethod
    def parse(cls, current_buffer: bytes, concrete_syntax_stream: BinaryIO) -> 'StorageResponse':
        response_str = current_buffer.decode('utf-8').strip()

        if response_str not in cls.possible_values:
            raise ResponseParseException(f"Invalid MCLite storage command response: {response_str}")

        return StorageResponse(response_str)


@dataclass
class ErrorResponse(AbstractSyntaxStructure):
    name: str
    message: Union[str, None]

    parsing_regex = re.compile(r"^(?P<name>SERVER_ERROR|CLIENT_ERROR)\s+(?P<message>.+)$")

    def to_concrete_syntax(self) -> bytes:
        return f"{self.name}{' ' + self.message if self.message else ''}\r\n".encode('utf-8')

    @classmethod
    def parse(cls, current_buffer: bytes, concrete_syntax_stream: BinaryIO) -> 'ErrorResponse':
        response_str = current_buffer.decode('utf-8').strip()
        response_match = cls.parsing_regex.search(response_str)

        if not response_match:
            if response_str == 'ERROR':
                name = "ERROR"
                message = None
            else:
                raise ResponseParseException(f"Invalid MCLite error response: {response_str}")
        else:
            name = response_match.group('name')
            message = response_match.group('message')

        return ErrorResponse(name, message)


class ResponseParseException(Exception):
    pass

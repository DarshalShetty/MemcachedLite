import re
from dataclasses import dataclass
from typing import Literal, Union, BinaryIO

from abstract_syntax_structure import AbstractSyntaxStructure
from server_config import SERVER_MAX_VALUE_SIZE, SERVER_KEY_MAX_LENGTH

StorageCommandName = Literal["set"]
RetrievalCommandName = Literal["get"]

protocol_line_end = "\r\n"


@dataclass
class QuitCommand(AbstractSyntaxStructure):
    name = "quit"

    def to_concrete_syntax(self) -> bytes:
        return self.name.encode('utf-8') + b"\r\n"

    @classmethod
    def parse(cls, current_buffer: bytes, concrete_syntax_stream: BinaryIO) -> 'QuitCommand':
        command_str = current_buffer.decode('utf-8').strip()
        if command_str != "quit":
            raise CommandParseException(f"Invalid quit command: {command_str}")
        return QuitCommand()


@dataclass
class DeleteCommand(AbstractSyntaxStructure):
    name = "delete"
    key: str

    parsing_regex = re.compile(r"^delete\s+(?P<key>[^\s]+)\s*$")

    def to_concrete_syntax(self) -> bytes:
        return self.name.encode('utf-8') + b" " + self.key.encode('utf-8') + b"\r\n"

    @classmethod
    def parse(cls, current_buffer: bytes, concrete_syntax_stream: BinaryIO) -> 'DeleteCommand':
        command_str = current_buffer.decode('utf-8').strip()
        command_match = cls.parsing_regex.search(command_str)
        if not command_match:
            raise CommandParseException(f"Invalid MCLite delete command: {command_str}")

        key = command_match.group('key')

        return DeleteCommand(key)


@dataclass
class StorageCommand(AbstractSyntaxStructure):
    name: StorageCommandName
    key: str
    value_size_bytes: int
    value: bytes

    parsing_regex = re.compile(
        r"^set\s+(?P<key>\S{1," +
        str(SERVER_KEY_MAX_LENGTH) +
        r"})\s+(?P<value_size_bytes>\d+)(\s+(?P<noreply>noreply))?$")

    def to_concrete_syntax(self) -> bytes:
        return f"{self.name} {self.key} {self.value_size_bytes}{protocol_line_end}".encode('utf-8') + \
               self.value + protocol_line_end.encode('utf-8')

    @classmethod
    def parse(cls, current_buffer, concrete_syntax_stream) -> 'StorageCommand':
        command_str = current_buffer.decode('utf-8').strip()
        command_match = cls.parsing_regex.search(command_str)

        value_size_bytes = int(command_match.group("value_size_bytes"))

        if not command_match:
            concrete_syntax_stream.read(value_size_bytes)
            concrete_syntax_stream.readline()  # Read the CRLF trailing after the value data block
            raise CommandParseException(f"Invalid MCLite storage command: {command_str}")

        if value_size_bytes > SERVER_MAX_VALUE_SIZE:
            concrete_syntax_stream.read(value_size_bytes)
            concrete_syntax_stream.readline()  # Read the CRLF trailing after the value data block
            raise CommandParseException(f"Value size bytes greater than SERVER_MAX_VALUE_SIZE: "
                                        f"{value_size_bytes} > {SERVER_MAX_VALUE_SIZE}")

        value = concrete_syntax_stream.read(value_size_bytes)

        if concrete_syntax_stream.read(2) != b"\r\n":
            raise CommandParseException(
                "Either incorrect value size specified or value data block doesn't end with CRLF")

        return StorageCommand("set", command_match.group('key'), value_size_bytes, value)


@dataclass
class RetrievalCommand(AbstractSyntaxStructure):
    name: RetrievalCommandName
    keys: [str]

    parsing_regex = re.compile(r"^get(?P<keys>(?:\s+\S{1," + str(SERVER_KEY_MAX_LENGTH) + r"})+)$")

    def to_concrete_syntax(self) -> bytes:
        return f"{self.name} {' '.join(self.keys)}{protocol_line_end}".encode('utf-8')

    @classmethod
    def parse(cls, current_buffer, concrete_syntax_stream) -> 'RetrievalCommand':
        command_str = current_buffer.decode('utf-8').strip()
        command_match = cls.parsing_regex.search(command_str)
        if not command_match:
            raise CommandParseException(f"Invalid MCLite retrieval command: {command_str}")

        keys = command_match.group('keys').split()

        return RetrievalCommand("get", keys)


AbstractCommand = Union[RetrievalCommand, StorageCommand, QuitCommand, DeleteCommand]


@dataclass
class MCLiteCommand(AbstractSyntaxStructure):
    command: AbstractCommand

    def to_concrete_syntax(self) -> bytes:
        return self.command.to_concrete_syntax()

    @classmethod
    def parse(cls, current_buffer, concrete_syntax_stream) -> 'MCLiteCommand':
        if current_buffer.startswith(b"get"):
            return MCLiteCommand(RetrievalCommand.parse(current_buffer, concrete_syntax_stream))
        elif current_buffer.startswith(b"set"):
            return MCLiteCommand(StorageCommand.parse(current_buffer, concrete_syntax_stream))
        elif current_buffer.startswith(b"quit"):
            return MCLiteCommand(QuitCommand.parse(current_buffer, concrete_syntax_stream))
        elif current_buffer.startswith(b"delete"):
            return MCLiteCommand(DeleteCommand.parse(current_buffer, concrete_syntax_stream))
        else:
            raise NonExistentCommandException(f"Command doesn't exist: {current_buffer}")


class NonExistentCommandException(Exception):
    pass


class CommandParseException(Exception):
    pass

import signal
import socket
import sys
from io import BufferedReader
from typing import Union, Dict

from command_parse import MCLiteCommand, StorageCommand, RetrievalCommand, QuitCommand
from response_parse import RetrievalResponse, ResponseValue, StorageResponse, ResponseParseException, ErrorResponse


class ClientSDK:

    def __init__(self, host: str, port: int) -> None:
        self.sock_conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.host = host
        self.port = port

    def __enter__(self):
        signal.signal(signal.SIGINT, self._handle_interrupt)
        signal.signal(signal.SIGTERM, self._handle_interrupt)

        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        # if self.sock_conn.fileno() >= 0:
        self.sock_conn.sendall(MCLiteCommand(QuitCommand()).to_concrete_syntax())
        self.close()

    def _handle_interrupt(self, *args):
        print(f"Interrupt received. Args: {args}")
        sys.exit()  # will trigger a exception, causing __exit__ to be called

    def connect(self):
        self.sock_conn.connect((self.host, self.port))

    def close(self):
        self.sock_conn.close()

    def set(self, key: str, val: bytes) -> Union[StorageResponse, ErrorResponse]:
        comm_abs_syn = MCLiteCommand(StorageCommand("set", key, len(val), val))
        self.sock_conn.sendall(comm_abs_syn.to_concrete_syntax())
        sock_stream = self.sock_conn.makefile('r', -1, newline="\r\n")
        current_buffer = sock_stream.readline().strip()

        tokens = current_buffer.split()
        if len(tokens) > 0 and tokens[0] in StorageResponse.possible_names:
            received = StorageResponse.parse(current_buffer.encode('utf-8'), sock_stream)
            return received
        else:
            response = ErrorResponse.parse(current_buffer.encode('utf-8'), sock_stream)
            return response

    def set_str(self, key: str, val: str) -> str:
        return self.set(key, val.encode('utf-8')).name

    def get(self, keys: [str]) -> Union[RetrievalResponse, ErrorResponse]:

        comm_abs_syn = MCLiteCommand(RetrievalCommand("get", set(keys)))
        self.sock_conn.sendall(comm_abs_syn.to_concrete_syntax())
        sock_stream: BufferedReader = self.sock_conn.makefile('rb')
        current_buffer: bytes = sock_stream.readline().strip()

        tokens = current_buffer.decode('utf-8').split()
        if len(tokens) > 0 and tokens[0] in RetrievalResponse.possible_names:
            received = RetrievalResponse.parse(current_buffer, sock_stream)
            return received
        else:
            response = ErrorResponse.parse(current_buffer, sock_stream)
            return response

    def get_str(self, keys: [str]) -> Dict[str, str]:
        return {val.key: val.value.decode('utf-8') for val in self.get(keys).values}

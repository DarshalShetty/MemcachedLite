import socketserver
from logging import Logger

from command_parse import MCLiteCommand, NonExistentCommandException, CommandParseException, QuitCommand, \
    StorageCommand, RetrievalCommand, DeleteCommand
from server_logging import init_logger, ConnectionLogAdapter
from response_parse import ErrorResponse
from server_config import SERVER_HOST, SERVER_PORT
from storage import FileStorage


class MCLiteTCPHandler(socketserver.StreamRequestHandler):
    storage = FileStorage()

    @classmethod
    def set_logger(cls, logger: Logger):
        cls.logger = logger

    def handle(self):
        log_adapter = ConnectionLogAdapter(self.logger, {
            "client_host": self.client_address[0],
            "client_port": self.client_address[1],
        })
        log_adapter.info("New client connected.")
        try:
            while True:
                text_line = self.rfile.readline()

                try:
                    comm_abs_synt = MCLiteCommand.parse(text_line, self.rfile)
                    request_repr = str(comm_abs_synt)
                    log_adapter.info(f"Request: {request_repr}")

                    command = comm_abs_synt.command
                    response = b""
                    if isinstance(command, QuitCommand):
                        break
                    elif isinstance(command, StorageCommand):
                        response = self.storage.set(command.key, command.value, command.value_size_bytes)
                    elif isinstance(command, RetrievalCommand):
                        response = self.storage.get(command.keys)
                    elif isinstance(command, DeleteCommand):
                        response = self.storage.delete(command.key)
                    log_adapter.info(f"Response: {response}")
                    self.wfile.write(response.to_concrete_syntax())
                except NonExistentCommandException as e:
                    log_adapter.info(str(e))
                    response = ErrorResponse("ERROR", None)
                    self.wfile.write(response.to_concrete_syntax())
                except CommandParseException as e:
                    log_adapter.info(str(e))
                    response = ErrorResponse("CLIENT_ERROR", str(e))
                    self.wfile.write(response.to_concrete_syntax())
        except BrokenPipeError as e:
            log_adapter.warning("Broken pipe error. Disconnecting now...")
        except Exception as e:
            log_adapter.error("Unexpected error. Disconnecting now...")
        finally:
            log_adapter.info("Client disconnected")


if __name__ == "__main__":
    logger = init_logger()

    # Create the server, binding to HOST on PORT
    with socketserver.ForkingTCPServer((SERVER_HOST, SERVER_PORT), MCLiteTCPHandler) as server:
        MCLiteTCPHandler.set_logger(logger)
        logger.info(f"Begin listening on {SERVER_HOST}:{SERVER_PORT}...")
        server.serve_forever()
        logger.info("Shutting down.")

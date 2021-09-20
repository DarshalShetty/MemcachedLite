#! /usr/bin/env python3

from client_sdk import ClientSDK
from src.response_parse import ErrorResponse

HOST, PORT = "localhost", 9889

if __name__ == "__main__":
    # Create a socket (SOCK_STREAM means a TCP socket)
    with ClientSDK(HOST, PORT) as conn:
        while True:
            try:
                line = input(f"[{HOST}:{PORT}]> ")
            except EOFError:
                break

            try:
                tokens = line.strip().split()
                if len(tokens) < 1:
                    resp = ErrorResponse("ERROR", None)
                elif tokens[0] == "get":
                    resp = conn.get_str(tokens[1:])
                elif tokens[0] == "set":
                    resp = conn.set_str(tokens[1], tokens[2])
                elif tokens[0] == "quit":
                    break
                else:
                    resp = ErrorResponse("ERROR", None)
                print(resp)
            except Exception as e:
                print(f"Unknown exception {e}")

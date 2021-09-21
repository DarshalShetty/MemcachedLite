#! /usr/bin/env python3

from client_sdk import ClientSDK
from server_config import SERVER_HOST, SERVER_PORT

if __name__ == "__main__":
    # Create a socket (SOCK_STREAM means a TCP socket)
    with ClientSDK(SERVER_HOST, SERVER_PORT) as conn:
        while True:
            try:
                line = input(f"[{SERVER_HOST}:{SERVER_PORT}]> ")
            except EOFError:
                break

            try:
                tokens = line.strip().split()
                if len(tokens) < 1:
                    resp = "ERROR\r\n"
                elif tokens[0] == "get":
                    resp = conn.get_str(tokens[1:])
                elif tokens[0] == "set":
                    resp = conn.set_str(tokens[1], tokens[2])
                elif tokens[0] == "quit":
                    break
                else:
                    resp = "ERROR\r\n"
                print(resp)
            except Exception as e:
                print(f"Unknown exception {e}")

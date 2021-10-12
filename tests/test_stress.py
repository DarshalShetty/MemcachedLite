import sys
import datetime
import random

sys.path.extend("..")
from client_sdk import ClientSDK
from server_config import SERVER_HOST, SERVER_PORT


def random_code():
    return random.randint(0, 1000000)


if __name__ == "__main__":
    server_host = SERVER_HOST if len(sys.argv) < 2 else sys.argv[1]
    server_port = SERVER_PORT if len(sys.argv) < 3 else int(sys.argv[2])
    connection_count = 10 if len(sys.argv) < 4 else int(sys.argv[3])
    batch_operations_count = 10
    batch_count = 100

    print(f"connection_count: {connection_count}")
    print(f"batch_operations_count: {batch_operations_count}")
    print(f"batch_count: {batch_count}")
    connections = [(ClientSDK(server_host, server_port)).__enter__() for _ in range(connection_count)]
    try:
        writes_start = datetime.datetime.now()
        for _ in range(batch_count):
            for conn in connections:
                for _ in range(batch_operations_count):
                    res = conn.set_str(f"key_{random_code()}",
                                       f"value_{random_code()}_{random_code()}_{random_code()}_{random_code()}")
        print(f"writes_time: {(datetime.datetime.now() - writes_start).total_seconds()} seconds")

        reads_start = datetime.datetime.now()
        for _ in range(batch_count):
            for conn in connections:
                res = conn.get_str([f"key_{random_code()}" for _ in range(batch_operations_count)])
        print(f"reads_time: {(datetime.datetime.now() - reads_start).total_seconds()} seconds")
    except Exception as e:
        print(e)
        exit(1)
    finally:
        for conn in connections:
            conn.__exit__(None, None, None)

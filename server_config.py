SERVER_HOST = "0.0.0.0"
SERVER_PORT = 9889
SERVER_MAX_VALUE_SIZE = 2 ** 20  # 1mb value size which is also the default in Oracle's and GCP's implementation
SERVER_KEY_MAX_LENGTH = 250  # This follows the memcached protocol
SERVER_STORAGE_DIR = "data"

import sys

sys.path.extend("..")
from client_sdk import ClientSDK
from server_config import SERVER_HOST, SERVER_PORT, SERVER_STORAGE_DIR

if __name__ == "__main__":
    server_host = SERVER_HOST if len(sys.argv) < 2 else sys.argv[1]
    server_port = SERVER_PORT if len(sys.argv) < 3 else int(sys.argv[2])
    with ClientSDK(server_host, server_port) as conn:
        conn.delete_str('k1')
        conn.delete_str('k2')

        res = conn.set_str("k1", "abc")
        print("Storing a key should return with a STORED response")
        assert res == "STORED"

        res = conn.get_str(["k1", "k2"])
        print("Fetching multiple keys should return values for only those"
              " keys that have been stored already.")
        assert res == {"k1": "abc"}

        res = conn.set_str("k2", "xyz")
        print("Storing another key should return with a STORED response again")
        assert res == "STORED"

        res = conn.get_str(["k1", "k2"])
        print("Once both keys have been set, getting multiple keys should "
              "fetch all stored values.")
        assert res == {"k1": "abc", "k2": "xyz"}

        res = conn.delete_str("k1")
        print("Deleting an existing key should return DELETED")
        assert res == "DELETED"

        res = conn.delete_str("k1")
        print("Deleting a non-existing key should return NOT_FOUND")
        assert res == "NOT_FOUND"

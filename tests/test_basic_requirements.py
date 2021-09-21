import os
import sys
import glob

sys.path.extend("..")
from client_sdk import ClientSDK
from server_config import SERVER_HOST, SERVER_PORT, SERVER_STORAGE_DIR

if __name__ == "__main__":
    with ClientSDK(SERVER_HOST, SERVER_PORT) as conn:
        print("Truncating data store for tests")
        files = glob.glob(f'{SERVER_STORAGE_DIR}/*')
        for f in files:
            os.remove(f)

        res = conn.get_str(["k1", "k2"])
        assert res == {}
        print("Empty store should fetch no keys for get commands")

        res = conn.set_str("k1", "abc")
        assert res == "STORED"
        print("Storing a key should return with a STORED response")

        res = conn.get_str(["k1", "k2"])
        assert res == {"k1": "abc"}
        print("Fetching multiple keys should return values for only those"
              " keys that have been stored already.")

        res = conn.set_str("k2", "xyz")
        assert res == "STORED"

        res = conn.get_str(["k1", "k2"])
        assert res == {"k1": "abc", "k2": "xyz"}
        print("Once both keys have been set, getting multiple keys should "
              "fetch all stored values.")

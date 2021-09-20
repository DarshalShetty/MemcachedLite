import os
import sys
import glob

from src.client_sdk import ClientSDK
from src.server_config import SERVER_HOST, SERVER_PORT, SERVER_STORAGE_DIR

sys.path.extend("../src")
files = glob.glob(f'{SERVER_STORAGE_DIR}/*')
for f in files:
    os.remove(f)

if __name__ == "__main__":
    with ClientSDK(SERVER_HOST, SERVER_PORT) as conn:
        res = conn.get_str(["k1", "k2"])
        assert res == {}

        res = conn.set_str("k1", "abc")
        assert res == "STORED"

        res = conn.get_str(["k1", "k2"])
        assert res == {"k1": "abc"}

        res = conn.set_str("k2", "xyz")
        assert res == "STORED"

        res = conn.get_str(["k1", "k2"])
        assert res == {"k1": "abc", "k2": "xyz"}

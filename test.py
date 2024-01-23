from ecc_cryptografy import *
import json

path_pem = os.path.join(os.path.dirname(__name__), r"db_local\pk.json")

if __name__ == "__main__":
    private_key, public_key = generate_key_pair()
    public_key_path = serialize_public_key(public_key) 
    private_key_path = serialize_private_key(private_key)

    obj_json = {"public_key":public_key_path.decode()}
    ola = "kaskals"
    with open(path_pem, "w") as f:
        f.write(json.dumps(obj_json))

    with open(path_pem, "r") as f:
        db = json.load(f)
        print(db["public_key"])

    print(public_key_path == db["public_key"].encode())

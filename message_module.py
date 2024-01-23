from functions_auth import *

def send_message(sio,  message): 
    connect_socket(sio)
    pk=''
    with open(path_pem, 'rb') as _pk:
        pk = _pk.read()
    
    private_key = serialization.load_pem_private_key(pk,
                                                     password=None,backend=default_backend())
    
    public_key = get_receiver_public_key()
    public_key = serialization.load_pem_public_key(public_key.encode(),
                                                     backend=default_backend())
    shared_key_sender = derive_shared_key(private_key, public_key)
    salt = os.urandom(16)
    derive_key = derive_symmetric_key(shared_key_sender, salt)
    iv = os.urandom(16)
    ciphertext = encrypt_message(derive_key, iv, message.encode())
    print('hey')
    sio.emit("message", {"message":ciphertext, "receiver": get_receiver_id(), "sender":get_user_id(), "sender_name":get_user_username(), "salt":salt.hex(), "iv":iv.hex()})

def receive_message(message, salt, iv):
    pk=''
    with open(path_pem, 'rb') as _pk:
        pk = _pk.read()
    
    private_key = serialization.load_pem_private_key(pk,
                                                     password=None,backend=default_backend())
    
    public_key = get_receiver_public_key()
    public_key = serialization.load_pem_public_key(public_key.encode(),
                                                     backend=default_backend())
    shared_key_sender = derive_shared_key(private_key, public_key)
    derive_key = derive_symmetric_key(shared_key_sender, bytes.fromhex(salt))
    new_message = decrypt_message(derive_key, bytes.fromhex(iv), message.encode())
    return new_message
    

def add_message(message):
    with open(path_db_local, 'r') as file:
        db = json.load(file)

    id_searched = get_user_id() + get_receiver_id()
    for row in db:
        if row == id_searched:
            db[id_searched].append(message)
            with open(path_db_local, 'w') as file:
                json.dump(db, file, indent=2)
            return


def message_handler(msg):
    print(msg)
    new_message = receive_message(msg["message"].decode(), msg["salt"], msg["iv"])
    message = {"username":msg["sender_name"],"message":new_message.decode()}
    print(new_message.decode())
    add_message(message)
    st.rerun()
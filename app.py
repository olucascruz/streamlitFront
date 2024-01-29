# from message_module import *
from functions_auth import *
import socketio


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
        sio.emit("message_test", {"message":ciphertext, "receiver": get_receiver_id(), "sender":get_user_id(), "sender_name":get_user_username(), "salt":salt, "iv":iv})
        print("aqui")
        
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
    derive_key = derive_symmetric_key(shared_key_sender, salt)
    new_message = decrypt_message(derive_key, iv, message)
    return new_message

def message_handler(msg):
    print("msg:",msg)
    print("msg['message']:",msg["message"])

    new_message = receive_message(msg["message"], msg["salt"], msg["iv"])
    print("new_message:",new_message)
    print("new_message_decoded:", new_message.decode())

def main():
    sio = socketio.Client()
    message = "ola mundo"
    print(message)
    send_message(sio, message)
    while True:
        sio.on("teste", message_handler)
    

if __name__ == "__main__":
     main()
        
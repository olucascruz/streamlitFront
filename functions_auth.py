from ecc_cryptografy import *
from service import API_CHAT
import streamlit as st
import json

path_db_local = os.path.join(os.path.dirname(__name__), r"db_local\db_messages.json")
path_db_auth = os.path.join(os.path.dirname(__name__), r"db_local\db_auth.json")
path_db_receiver = os.path.join(os.path.dirname(__name__), r"db_local\db_receiver.json")
path_pem = os.path.join(os.path.dirname(__name__), r"db_local\pk.pem")

def connect_socket(sio):
    if not sio.connected:
        sio.connect('http://127.0.0.1:5000')

def login_submitted(api:API_CHAT, username, password, sio):
    private_key, public_key = generate_key_pair()
    public_key_path = serialize_public_key(public_key) 
    private_key_path = serialize_private_key(private_key)
    with open(path_pem, "wb") as f:
        f.write(private_key_path)
    
    data = {
        "username":username,
        "password": password,
        "public_key":public_key_path.decode()
        }
    try:
        response, code_response = api.login(data)
    except Exception as err:
        code_response = 400
        st.session_state.error_login = "error login"

    if code_response == 200:
        auth = {"token": response["token"],
                "id":response["id"]} 
        st.session_state.auth = auth
        key_pair = {
            "private_key": private_key,
            "public_key": public_key,
            "id":response["id"]
            }
        define_auth(response["id"], username, private_key_path.decode())
        st.session_state.key_pair = key_pair
        st.session_state.username = username
        connect_socket(sio)
        st.session_state.state = "users"

def register_submmited(api:API_CHAT,username, password):
    private_key, public_key = generate_key_pair()
    public_key_path = serialize_public_key(public_key)
    private_key_path = serialize_private_key(private_key)
    with open(path_pem, "wb") as f:
        f.write(private_key_path)
    public_key_path = serialize_public_key(public_key) 
    data = {
        "username":username,
        "password": password,
        "public_key":public_key_path.decode()
        }
    response, code_response = api.register(data)
    
    if code_response == 200:
        st.toast('Conta criada!')
        st.session_state.state = "login"

def define_receiver(user, username, public_key):
    with open(path_db_receiver, 'w') as file:
        json.dump({}, file, indent=2)
    
    with open(path_db_receiver, 'r') as file:
        db = json.load(file)

    db[user] = {"username":username, "public_key":public_key}

    with open(path_db_receiver, 'w') as file:
        json.dump(db, file, indent=2)


def define_auth(user_id, username, private_key):
    with open(path_db_auth, 'r') as file:
        db = json.load(file)
    
    db["auth"] = {"user_id":user_id, "username":username, "private_key":private_key}

    with open(path_db_auth, 'w') as file:
        json.dump(db, file, indent=2)

def get_receiver_id():
    with open(path_db_receiver, 'r') as file:
        db = json.load(file)

    for receiver in db:
        return receiver
    
def get_user_id():
    with open(path_db_auth, 'r') as file:
        db = json.load(file)

    print(db)
    return db["auth"]["user_id"]


def get_user_username():
    with open(path_db_auth, 'r') as file:
        db = json.load(file)

    print(db)
    return db["auth"]["username"]

def get_user_private_key():
    with open(path_db_auth, 'r') as file:
        db = json.load(file)

    print(db)
    return db["auth"]["private_key"]

def create_db_message(receiver_id):
    id_message = get_user_id() + receiver_id
    with open(path_db_local, 'r') as file:
        db = json.load(file)
    
    for row in db:
        if row == id_message: return 

    db[id_message] = []

    with open(path_db_local, 'w') as file:
        json.dump(db, file, indent=2)


def get_receiver_public_key():
    with open(path_db_receiver, 'r') as file:
        db = json.load(file)

    for receiver in db:
        return db[receiver]["public_key"]
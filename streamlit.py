import streamlit as st
from service import API_CHAT
from ecc_cryptografy import *
import threading
import socketio
import json
import os

def selected_user(user, username_receiver, public_key):
    create_db_message(user)
    st.session_state.receiver = user
    st.session_state.state = "chat"
    st.session_state.username_receiver = username_receiver
    define_receiver(user, username_receiver, public_key)
sio = socketio.Client()
path_db_local = os.path.join(os.path.dirname(__name__), r"db_local\db_messages.json")


path_db_auth = os.path.join(os.path.dirname(__name__), r"db_local\db_auth.json")

path_db_receiver = os.path.join(os.path.dirname(__name__), r"db_local\db_receiver.json")


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

def connect_socket(sio):
    if not sio.connected:
        sio.connect('http://127.0.0.1:5000')

def send_message(sio,  message): 
    connect_socket(sio)
    sio.emit("message", {"message":message, "receiver": get_receiver_id(), "sender":get_user_id(), "sender_name":get_user_username()})

def login_submitted(api:API_CHAT, username, password):
    private_key, public_key = generate_key_pair()
    public_key_path = serialize_public_key(public_key) 
    data = {
        "username":username,
        "password": password,
        "public_key":str(public_key_path)
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
        define_auth(response["id"], username, str(private_key))
        st.session_state.key_pair = key_pair
        st.session_state.username = username
        global sio
        connect_socket(sio)
        st.session_state.state = "users"

def register_submmited(api:API_CHAT,username, password):
    private_key, public_key = generate_key_pair()
    public_key_path = serialize_public_key(public_key)

    data = {
        "username":username,
        "password": password,
        "public_key":str(public_key_path)
        }
    response, code_response = api.register(data)
    
    if code_response == 200:
        st.toast('Conta criada!')
        st.session_state.state = "login"

def login_component(api:API_CHAT):
    with st.form("login"):
        st.write("login")
        username = st.text_input('username')
        password = st.text_input('password')
       
        st.write(st.session_state.error_login)
        # Every form must have a submit button.
        submitted = st.form_submit_button("Submit")
        
        if submitted:
            global sio
            connect_socket(sio)
            login_submitted(api, username, password)
    if st.button("go to register"):
        st.session_state.state="register"

def register_component(api:API_CHAT):
    with st.form("register"):
        st.write("register")
        username = st.text_input('username')
        password = st.text_input('password')

        # Every form must have a submit button.
        submitted = st.form_submit_button("Submit")
        if submitted:
            register_submmited(api, username, password)
            
    if st.button("go to login"):
        st.session_state.state="login"
        
def list_users_component(api:API_CHAT):
    users = False
    try:
        users = api.get_users(st.session_state.auth["token"])
    except Exception as err:
        print(err)

    if users:
        for user in users:
            if user != st.session_state.auth["id"]:
                st.write(f"{users[user]['username']}:{users[user]['is_online']}")
                st.button("acessar",on_click=selected_user(user=user, username_receiver=users[user]['username'], public_key=users[user]['public_key']), key=user)



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

def chat_component():
    global sio, msgs
    

    with open(path_db_local, 'r') as file:
        db = json.load(file)
    
    id_searched = get_user_id() + get_receiver_id()
    if id_searched in db:
        for message in db[id_searched]: 
            st.write(f"{message['username']} : {message['message']} \n")
    
    # Every form must have a submit button.
    submitted = st.chat_input("your message")
    if submitted:
        message = {"username":st.session_state.username,"message":submitted}
        add_message(message)
        send_message(sio, submitted)
    sio.on(f"message-{get_user_id()}", message_handler)

def message_handler(msg):
    
    message = {"username":msg["sender_name"],"message":msg["message"]}
    if msg["sender"] != get_user_id():
        add_message(message)


def init_session():
    if 'users' not in st.session_state:
        st.session_state['users'] = []
    
    if 'auth' not in st.session_state:
        st.session_state['auth'] = {"token":"",
                                    "id":""}    
    if 'username' not in st.session_state:
        st.session_state['username'] = ""
        
    if 'messages' not in st.session_state:
        st.session_state['messages'] = []
    
    if 'state' not in st.session_state:
        st.session_state['state'] = "login"

    if 'receiver' not in st.session_state:
        st.session_state['receiver'] = ''

    if 'username_receiver' not in st.session_state:
        st.session_state['username_receiver'] = ''
    if 'key_pair' not in st.session_state:
        st.session_state['key_pair'] = {
                                        "id":"",
                                        "private_key":"",
                                        "public_key":""}
    


def erros():
    if 'error_login' not in st.session_state:
        st.session_state['error_login'] = ""

def interface(api:API_CHAT):
    if st.session_state.state == "login":
        login_component(api)
    elif st.session_state.state == "register":
        register_component(api)
    elif st.session_state.state == "users" and st.session_state.auth["token"] != "":
        list_users_component(api)
    elif st.session_state.state == "chat" and st.session_state.auth["token"] != "":
        chat_component()
    
        
        
if __name__ == "__main__":
    api = API_CHAT()
    init_session()
    erros()
    interface(api)
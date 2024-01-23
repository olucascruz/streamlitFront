import streamlit as st
from service import API_CHAT
from functions_auth import *
from ecc_cryptografy import *
import socketio
import json
from message_module import *


#Global
sio = socketio.Client()

def selected_user(user, username_receiver, public_key):
    create_db_message(user)
    st.session_state.receiver = user
    st.session_state.state = "chat"
    st.session_state.username_receiver = username_receiver
    define_receiver(user, username_receiver, public_key)

def login_component(api:API_CHAT):
    with st.form("login"):
        st.write("login")
        username = st.text_input('username')
        password = st.text_input('password')
       
        st.write(st.session_state.error_login)
        # Every form must have a submit button.
        submitted = st.form_submit_button("Submit")
        
        if submitted:
            connect_socket(sio)
            login_submitted(api, username, password, sio)
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
            register_submmited(api, username, password, sio)
            
    if st.button("go to login"):
        st.session_state.state="login"
        
def list_users_component(api:API_CHAT):
    users = False
    try:
        users = api.get_users(st.session_state.auth["token"])
    except Exception as err:
        (err)

    if users:
        for user in users:
            if user != st.session_state.auth["id"]:
                st.write(f"{users[user]['username']}:{users[user]['is_online']}")
                st.button("acessar",on_click=selected_user(user=user, username_receiver=users[user]['username'], public_key=users[user]['public_key']), key=user)

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
        send_message(sio, submitted)
        add_message(message)
    sio.on(f"message-{get_user_id()}", message_handler)



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
    elif st.session_state.state == "users":
        list_users_component(api)
    elif st.session_state.state == "chat":
        chat_component()
    
        
        
if __name__ == "__main__":
    api = API_CHAT()
    init_session()
    erros()
    interface(api)
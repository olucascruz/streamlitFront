import requests

class API_CHAT:
    def __init__(self) -> None:
        self.url = "http://127.0.0.1:5000"

    def register(self, data):
        """expected format: {
        username: ""
        password: ""
        }, public_key """

        url_register = f"{self.url}/register"
        
        print(data)
        response = requests.post(url_register, json=data)
        print(response.text)
        return (response, response.status_code)
        

    def login(self, data):
        """expected format: {
        username: ""
        password: ""
        }, public_key"""

        url_login = f"{self.url}/login"
        
        response = requests.post(url_login, json=data)
        return (response.json(), response.status_code)
    
    def get_users(self, auth):
        url_users = f"{self.url}/users"
        headers = {"Authorization": auth}
        return requests.get(url_users, headers=headers).json()
    
    def logout(self, id):
        url_users = f"{self.url}/logout"
        return requests.post(url_users, json={"id":id}).json()
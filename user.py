from app import app

class user():
    def __init__(self, birthdate, name, email, administrator=False):
        self.birthdate = birthdate
        self.name = name
        self.email = email
        self.administrator = administrator
        self.password = "j"
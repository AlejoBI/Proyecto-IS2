from typing import List
from firebase import firebase
from core import ports
from core import models
import app.configurations as configurations

class FirebaseUserAdapter(ports.UserRepositoryPort):  # Cambia el puerto a uno relacionado con usuarios
    def __init__(self, url: str) -> None:
        self.firebase = firebase.FirebaseApplication(url, None)

    def register_user(self, user: models.User) -> None:
        print(f"Guardando usuario: {user}")
        self.firebase.post(f"/users/{user.id}", data={"id": user.id, "name": user.name, "email": user.email, "password": user.password, "role": user.role})

    def login_user(self, email: str, password: str) -> models.User | None:
        users = self.firebase.get("/users", None)
        if not users:
            return None

        for user_id, user_data in users.items():
            if user_data['email'] == email and user_data['password'] == password:
                return models.User(id=user_id, name=user_data['name'], email=user_data['email'])
        return None

    def get_users(self, query: str = None) -> List[models.User]:
        users = self.firebase.get("/users", None)  # Obtiene todos los usuarios
        if not users:
            return []

        user_list = []
        for user_id, user_data in users.items():
            if not query or query.lower() in user_data['name'].lower():  # Filtra por nombre si se pasa un query
                user_list.append(models.User(id=user_id, name=user_data['name'], email=user_data['email']))
        return user_list

    def get_user_by_id(self, user_id: str) -> models.User | None:
        user_data = self.firebase.get(f"/users/{user_id}", None)
        if user_data:
            return models.User(id=user_id, name=user_data['name'], email=user_data['email'])
        return None
    
    def update_user_by_id(self, user: models.User) -> None:
        self.firebase.put(f"/users/{user.id}", data={"id": user.id, "name": user.name, "email": user.email, "password": user.password, "role": user.role})

    def delete_user(self, user_id: str) -> None:
        self.firebase.delete(f"/users/{user_id}", None)

firebase_adapter = FirebaseUserAdapter(configurations.Settings.FIREBASE_URI)

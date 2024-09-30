from typing import List
from server.core import ports
from server.core import models
from google.cloud import firestore
import firebase_admin
from server.app import configurations
from firebase_admin import credentials, auth


class FirebaseUserAdapter(ports.UserRepositoryPort):
    def __init__(self) -> None:
        cred = credentials.Certificate(configurations.settings.FIREBASE_CONFIG)
        firebase_admin.initialize_app(cred)
        self.db = firestore.Client()

    def register_user(self, user: models.User) -> None:
        try:
            print(f"Guardando usuario: {user}")
            auth_user = auth.create_user(email=user.email, password=user.password)
            self.db.collection("users").document(auth_user.uid).set({
                "id": auth_user.uid,
                "name": user.name,
                "email": user.email,
                "role": user.role
            })
        except firebase_admin.exceptions.FirebaseError as e:
            print(f"Error al registrar usuario: {e}")
            raise

    def login_user(self, email: str, password: str) -> models.User | None:
        try:
            auth_user = auth.get_user_by_email(email)
            user_data = self.db.collection("users").document(auth_user.uid).get()
            if user_data.exists:
                user_data = user_data.to_dict()
                return models.User(id=auth_user.uid, name=user_data['name'], email=user_data['email'])
            else:
                print("Usuario no encontrado en Firestore")
                return None
        except firebase_admin.exceptions.FirebaseError as e:
            print(f"Error al iniciar sesión: {e}")
            return None

    def get_users(self, query: str = None) -> List[models.User]:
        users_ref = self.db.collection("users")
        if query:
            users_ref = users_ref.where("name", ">=", query).where("name", "<=", query + "\uf8ff")
        users = users_ref.stream()
        return [models.User(id=user.id, **user.to_dict()) for user in users]

    def get_user_by_id(self, user_id: str) -> models.User | None:
        user_data = self.db.collection("users").document(user_id).get()
        if user_data.exists:
            return models.User(id=user_id, **user_data.to_dict())
        return None

    def update_user_by_id(self, user: models.User) -> None:
        self.db.collection("users").document(user.id).update({
            "name": user.name,
            "email": user.email,
            "password": user.password,
            "role": user.role
        })

    def delete_user(self, user_id: str) -> None:
        self.db.collection("users").document(user_id).delete()


firebase_adapter = FirebaseUserAdapter()
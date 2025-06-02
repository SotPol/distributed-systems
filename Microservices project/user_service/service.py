# user_service/service.py
from repository import UserRepository
from passlib.hash import bcrypt

class UserService:
    @staticmethod
    def create_user(data: dict):
        # Перевірка, що є email і пароль
        if 'email' not in data or 'password' not in data:
            return {"error": "email and password required"}, 400

        # Хешування пароля
        data['password'] = bcrypt.hash(data['password'])

        # Запис до бази
        return UserRepository.add_user(data)

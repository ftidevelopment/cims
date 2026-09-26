from werkzeug.security import (
    check_password_hash,
    generate_password_hash,
)

from app.repositories.user_repository import UserRepository
from app.services.base_service import BaseService
from app.core.transaction_manager import TransactionManager


class AuthService(BaseService):

    MAX_FAILED_LOGIN = 5

    def __init__(self):
        super().__init__()
        self.user_repository = UserRepository()

    def authenticate(self, username, password):

        try:

            user = self.find_user(username)

            if user is None:
                return self.failed(
                    "Username tidak ditemukan."
                )

            if self.is_locked(user):
                return self.failed(
                    "Akun telah dikunci."
                )

            if not self.verify_password(user, password):

                self.login_failed(user)

                return self.failed(
                    "Password salah."
                )

            self.login_success(user)

            return self.success(
                "Login berhasil.",
                user,
            )
        except Exception as ex:
            return self.handle_exception(ex)
    
    
    def find_user(self, username):
        return self.user_repository.get_by_username(username)

    def verify_password(self, user, password):
        return check_password_hash(
            user.password_hash,
            password,
        )

    def is_locked(self, user):
        return user.is_locked

    def login_success(self, user):
        with TransactionManager():
            user.update_last_login()
            user.reset_failed_login()

    def login_failed(self, user):
        with TransactionManager():
            user.increase_failed_login()

            if user.failed_login_count >= self.MAX_FAILED_LOGIN:
                user.is_locked = True

    def change_password(
        self,
        user,
        current_password,
        new_password,
    ):
        try:

            # ==========================================
            # Verify current password
            # ==========================================

            if not check_password_hash(
                user.password_hash,
                current_password,
            ):
                return self.failed(
                    "Current password is incorrect."
                )

            # ==========================================
            # Prevent same password
            # ==========================================

            if check_password_hash(
                user.password_hash,
                new_password,
            ):
                return self.failed(
                    "New password must be different from current password."
                )

            # ==========================================
            # Generate new password hash
            # ==========================================

            new_password_hash = generate_password_hash(
                new_password
            )

            # ==========================================
            # Update password
            # ==========================================

            with TransactionManager():

                user.change_password(
                    new_password_hash
                )

            return self.success(
                "Password changed successfully."
            )

        except Exception as ex:

            return self.handle_exception(ex)
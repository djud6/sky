from api_auth.Auth_User.User import User
from api_auth.Auth_User.UserModelHistory import UserModelHistory
import logging

class Logger():
    @staticmethod
    def getLogger():
        return logging.getLogger(__name__)


class UserHistory:

    @staticmethod
    def create_user_record(user_id):
        try:
            user = User.objects.using("auth_db").get(id=user_id)
            user_history_entry = UserHistory.generate_userhistory_entry(user)
            user_history_entry.save()
            return True
        except Exception as e:
            print(e)
            Logger.getLogger().error(e)
            return False

    @staticmethod
    def generate_userhistory_entry(user):
        return UserModelHistory(
            user=user,
            email=user.email,
            db_access=user.db_access,
            password=user.password,
            first_name=user.first_name,
            last_name=user.last_name,
            is_superuser=user.is_superuser,
            is_staff=user.is_staff,
            is_active=user.is_active,
            username=user.username
        )
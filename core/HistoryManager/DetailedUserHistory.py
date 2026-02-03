from api.Models.DetailedUser import DetailedUser
from api.Models.DetailedUserModelHistory import DetailedUserModelHistory
import logging

class Logger():
    @staticmethod
    def getLogger():
        return logging.getLogger(__name__)


class DetailedUserHistory:

    @staticmethod
    def create_detailed_user_record(detailed_user_id, db_name):
        try:
            user = DetailedUser.objects.using(db_name).get(detailed_user_id=detailed_user_id)
            detailed_user_history_entry = DetailedUserHistory.generate_userhistory_entry(user)
            detailed_user_history_entry.save()
            return True
        except Exception as e:
            Logger.getLogger().error(e)
            return False

    @staticmethod
    def generate_userhistory_entry(user):
        return DetailedUserModelHistory(
            user=user,
            company=user.company,
            email=user.email,
            business_unit=user.business_unit,
            cost_allowance=user.cost_allowance,
            role_permissions=user.role_permissions,
            image_url=user.image_url
        )
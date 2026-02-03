from ..Auth_User.db_constants import Constants
from ..Auth_User.User import User
from django.core.exceptions import ObjectDoesNotExist

class DBMethods():

    @staticmethod
    def GetDBName(_user_id):
        user = User.objects.using(Constants.AUTH_DB).get(pk=_user_id)
        if(not user is None):
            return user.db_access
        else:
            return None

    # -----------------------------------------------------------------------

    @staticmethod
    def GetDbNameFromUserID(_user_id):
        user = User.objects.using(Constants.AUTH_DB).get(pk=_user_id)
        if(user):
            db_name = DBMethods.GetDBName(user.id)
            return db_name
        return None

    # -----------------------------------------------------------------------

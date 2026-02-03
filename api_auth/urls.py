from api_auth.Auth_Pusher import PusherView
from django.urls import path, include
from rest_framework.urlpatterns import format_suffix_patterns
from .Auth_User import AuthView
from .Auth_User import AuthRefresh
from .Auth_User import UserView

app_name = 'api_auth'

urlpatterns = [
    path('Login', AuthView.CustomAuthToken.as_view()),
    path('Refresh', AuthRefresh.RefreshAuthToken.as_view()),
    path('User/Get/All', UserView.GetAllUsers.as_view()),
    path('User/Create/Account', UserView.CreateUser.as_view()),
    path('User/Edit/Account', UserView.EditUserAccount.as_view()),
    path('User/Edit/AnyAccount', UserView.EditAnyUserInfoSuperUser.as_view()), 
    path('User/Info', UserView.GetUserInformation.as_view()),
    path('User/GetAllActions', UserView.GetUserActions.as_view()),
    path('User/Any-Info', UserView.GetAnyUserInfoSuperUser.as_view()), 
    path('User/Update/Image', UserView.UpdateUserImage.as_view()),
    path('User/Update/Password', UserView.UpdateUserPassword.as_view()),
    path('User/Create/Password', UserView.CreateUserPasswordSuperuser.as_view()), 
    path('User/Update/User-Permission', UserView.UserPermissionSuperUser.as_view()),
    path('User/Update/Agreement', UserView.UpdateAgreement.as_view()),
    path('User/Update/Configuration', UserView.UpdateUserConfiguration.as_view()),
    path('User/Update/Tablefilter', UserView.UpdateUserTableFilter.as_view()),
    path('User/Delete/Tablefilter', UserView.DeleteUserTableFilter.as_view()),
    path('User/Forgot/Password', UserView.ForgotPassword.as_view()),  
    path('reset-password/<uidb64>/<token>/', UserView.PasswordTokenCheck.as_view(), name='password_reset_confirm'), 
    path('User/password-reset-complete/', UserView.ForgotPasswordGenerate.as_view(), name='password-reset-complete'), 
    path('pusher/auth', PusherView.PusherAuth.as_view()),
    path('RolePermission/Get/All', UserView.GetAllRolePermissions.as_view()),
    path('User/Initial-Data', UserView.GetInitialUserData.as_view()),
]

urlpatterns = format_suffix_patterns(urlpatterns)


from rest_framework import serializers
from django.contrib.auth import authenticate
from django.utils.translation import gettext_lazy as _
from api.Models.DetailedUser import DetailedUser
from api.Models.user_configuration import UserConfiguration
from api.Models.RolePermissions import RolePermissions
from ..Auth_User.User import User
import json

class DetailedUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = DetailedUser
        fields = ["detailed_user_id", "email", "cost_allowance", "company", "image_url", "business_unit", "location", "role_permissions", "agreement_accepted", "first_time_login", "cost_centre"]
        depth = 1

class LinkedUserModelSerializer(serializers.ModelSerializer):
    details = DetailedUserSerializer(read_only=True)
    class Meta:
        model = User
        fields = ["username", "email", "first_name", "last_name", "is_superuser", "is_staff", "is_active", "details", "date_joined", "last_login"]

class UserModelSerializer(serializers.ModelSerializer):
    company_name = serializers.SlugRelatedField(read_only=True, source='company', slug_field='company_name')
    class Meta:
        model = User
        fields = "__all__"

class DetailedSuperUserSerializer(DetailedUserSerializer):
    pass

class LinkedSuperUserModelSerializer(serializers.ModelSerializer):
    details = DetailedUserSerializer(read_only=True)
    class Meta:
        model = User
        fields = ["id", "username", "email", "first_name", "last_name", "is_superuser", "is_staff", "is_active", "details"]

class UserConfigurationSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserConfiguration
        fields = "__all__"

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        table_filter = rep.get('table_filter')
        if table_filter:
            # Replacing single quotes with double quotes to make it a valid JSON string
            table_filter = table_filter.replace("'", '"')
            # Replacing "None" with null
            table_filter = table_filter.replace('None', 'null')
            # Converting the JSON string to a Python dictionary
            table_filter_dict = json.loads(table_filter)
            # Updating the rep dictionary with the new dictionary
            rep['table_filter'] = table_filter_dict

        return rep

class RolePermissionsSerializer(serializers.ModelSerializer):
    class Meta:
        model = RolePermissions
        fields = "__all__"

# This is the LoginSerializer
class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField(
        label=_("Email"),
        write_only=True
    )
    password = serializers.CharField(
        label=_("Password"),
        style={'input_type': 'password'},
        trim_whitespace=False,
        write_only=True
    )

    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')

        if email and password:
            user = authenticate(request=self.context.get('request'),
                                email=email, password=password)

            if not user:
                msg = _('Unable to log in with provided credentials.')
                raise serializers.ValidationError(msg, code='authorization')
        else:
            msg = _('Must include "email" and "password".')
            raise serializers.ValidationError(msg, code='authorization')

        attrs['user'] = user
        return attrs

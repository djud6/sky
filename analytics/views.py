from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from api_auth.Auth_User.AuthTokenCheckHandler import auth_token_check
from django.db.models import Count, F
from django.db.models.functions import Trunc

from core.AnalyticsManager.AnalyticsHandler import AnalyticsHandler
from api.Models.asset_model import AssetModel
from api.Models.accident_report import AccidentModel
from GSE_Backend.errors.ErrorDictionary import CustomError

import logging

class Logger():
    @staticmethod
    def getLogger():
        return logging.getLogger(__name__)



# Utility functions
def countAssetsByField(field, queryset=None, **kwargs):

    if 'fieldname' in kwargs:
        name = kwargs['fieldname']
        if queryset is None:
            return AssetModel.objects.annotate(**{name:F(field)}).values(name).annotate(count=Count(field)).order_by('-count')
        else:
            
            return queryset.annotate(**{name:F(field)}).values(name).annotate(count=Count(field)).order_by('-count')
    else:
        if queryset is None:
            return AssetModel.objects.values(field).annotate(count=Count(field)).order_by('-count')
        else:
            return queryset.values(field).annotate(count=Count(field)).order_by('-count')

# Create your views here.

class ActiveVehicles(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    def get(self, request):
        if auth_token_check(request.user):
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.IT_0))
            return Response(CustomError.get_full_error_json(CustomError.IT_0), status=status.HTTP_400_BAD_REQUEST)

        if request.query_params.get('Location', None) is None:
            #counts = AssetModel.objects.values('Status').annotate(count=Count('Status'))
            counts = countAssetsByField('last_process')
            return Response(counts)
        else:
            #counts = AssetModel.objects.filter(Location_IATA=request.query_params.get('Location_IATA')).values('Status').annotate(count=Count('Status'))
            counts = countAssetsByField('last_process', AssetModel.objects.filter(current_location=request.query_params.get('current_location')))
            return Response(counts)

class Locations(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    def get(self, request):
        if auth_token_check(request.user):
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.IT_0))
            return Response(CustomError.get_full_error_json(CustomError.IT_0), status=status.HTTP_400_BAD_REQUEST)

        #counts = AssetModel.objects.values('Location_IATA').annotate(count=Count('Location_IATA'))
        counts = countAssetsByField('current_location__location_name', fieldname='location_name')
        return Response(counts)

class BusinessUnits(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    def get(self, request):
        if auth_token_check(request.user):
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.IT_0))
            return Response(CustomError.get_full_error_json(CustomError.IT_0), status=status.HTTP_400_BAD_REQUEST)

        counts = countAssetsByField('department__name',fieldname='department_name')
        return Response(counts)


# Takes query_params: start, end, scale {day,week,month)
class Accidents(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    def get(self, request):
        if auth_token_check(request.user):
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.IT_0))
            return Response(CustomError.get_full_error_json(CustomError.IT_0), status=status.HTTP_400_BAD_REQUEST)

        scale = request.query_params.get('scale','month')
        start = request.query_params.get('start','1900-01-01')
        end = request.query_params.get('end', '2100-01-01')
        queryset = AccidentModel.objects.filter(date_created__gte=start, date_created__lte=end)
        if scale == 'month':
            counts = queryset.annotate(month=Trunc('date_created','month')).values('month').annotate(count=Count('month')).order_by('month')
            return Response(counts)
        elif scale == 'week':
            counts = queryset.annotate(week=Trunc('date_created','week')).values('week').annotate(count=Count('week')).order_by('week')
            return Response(counts)
        else:
            counts = queryset.values('date_created').annotate(count=Count('date_created')).order_by('date_created')
            return Response(counts)

class MaxUsersAndAssetsForDaterange(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    def get(self, request, start_date, end_date):
        if auth_token_check(request.user):
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.IT_0))
            return Response(CustomError.get_full_error_json(CustomError.IT_0), status=status.HTTP_400_BAD_REQUEST)

        return AnalyticsHandler.handle_max_users_and_assets_for_daterange(start_date, end_date, request.user.db_access)

class AllMaxUsersAndAssetsForMonth(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    def get(self, request):
        if auth_token_check(request.user):
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.IT_0))
            return Response(CustomError.get_full_error_json(CustomError.IT_0), status=status.HTTP_400_BAD_REQUEST)

        return AnalyticsHandler.handle_all_max_users_and_assets_for_month()

class DataPerAssetForDaterange(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    def get(self, request, start_date, end_date):
        if auth_token_check(request.user):
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.IT_0))
            return Response(CustomError.get_full_error_json(CustomError.IT_0), status=status.HTTP_400_BAD_REQUEST)

        return AnalyticsHandler.handle_data_per_asset_for_daterange(start_date, end_date, request.user.db_access)

class AllDataPerAssetForMonth(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    def get(self, request):
        if auth_token_check(request.user):
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.IT_0))
            return Response(CustomError.get_full_error_json(CustomError.IT_0), status=status.HTTP_400_BAD_REQUEST)

        return AnalyticsHandler.handle_all_data_per_asset_for_month()
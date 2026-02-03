from django.urls import path
from analytics import views
from .dynamic_fleetguru import DynamicFleetGuruView

urlpatterns = [
    path('ActiveVehicles', views.ActiveVehicles.as_view()),
    path('Locations', views.Locations.as_view()),
    path('BusinessUnits', views.BusinessUnits.as_view()),
    path('Accidents', views.Accidents.as_view()),
    path('Daterange/Max/Users/Assets/<str:start_date>/<str:end_date>', views.MaxUsersAndAssetsForDaterange.as_view()),
    path('All/Monthly/Max/Users/Assets', views.AllMaxUsersAndAssetsForMonth.as_view()),
    path('Daterange/Data/Per/Asset/<str:start_date>/<str:end_date>', views.DataPerAssetForDaterange.as_view()),
    path('All/Monthly/Data/Per/Asset', views.AllDataPerAssetForMonth.as_view()),
    path('DynamicFleetGuru/Underused/Assets', DynamicFleetGuruView.UnderusedAssets.as_view()),
]
from django.urls import path
from .Views.Test import TestView
from .Views.Scope1.Scope1View import *
from .Views.Scope2 import Scope2View
from django.http import JsonResponse
from .Views.Scope3 import Scope3View
from .Views import GHGCalculateRouter
from .Views.Scope4 import Scope4View

urlpatterns = [
    path("TestConnectionToClientServer", TestView.TestConnectionToClientServer.as_view()),
    path("TestRoutingToClientServer/<str:client_name>", TestView.TestRoutingToClientServer.as_view()),
    path("Scope1/Marine/CO2", CalculateUniformMarineCO2Emissions.as_view()),

    path("Scope1/Uniform/Marine", CalculateUniformMarineCO2Emissions.as_view()),
    path("Scope1/Uniform/Aviation", CalculateUniformAviationCO2Emissions.as_view()),
    path("Scope1/Uniform/Railway", CalculateUniformRailwaysCO2Emissions.as_view()),
    path("Scope1/Uniform/Road", CalculateUniformRoadCO2Emissions.as_view()),

    path("Scope1/NA/Marine", CalculateNorthAmericanMarineCO2Emissions.as_view()),
    path("Scope1/NA/Aviation", CalculateNorthAmericanAviationCO2Emissions.as_view()),
    path("Scope1/NA/Railway", CalculateNorthAmericanRailwaysCO2Emissions.as_view()),

    path("Scope1/EU/Marine", CalculateEuropeanMarineCO2Emissions.as_view()),
    path("Scope1/EU/Aviation", CalculateEuropeanAviationCO2Emissions.as_view()),
    path("Scope1/EU/Railway", CalculateEuropeanRailwaysCO2Emissions.as_view()),
    path("Scope1/EU/Road", CalculateEuropeanRoadCO2Emissions.as_view()),

    path("Scope1/CH/Marine", CalculateChinaMarineCO2Emissions.as_view()),
    path("Scope1/CH/Aviation", CalculateChinaAviationCO2Emissions.as_view()),
    path("Scope1/CH/Railway", CalculateChinaRailwaysCO2Emissions.as_view()),
    path("Scope1/CH/Road", CalculateChinaRoadCO2Emissions.as_view()),

    path("Scope1/AF/Marine", CalculateAfricanMarineCO2Emissions.as_view()),
    path("Scope1/AF/Aviation", CalculateAfricanAviationCO2Emissions.as_view()),
    path("Scope1/AF/Railway", CalculateAfricanRailwaysCO2Emissions.as_view()),
    path("Scope1/AF/Road", CalculateAfricanRoadCO2Emissions.as_view()),

    path("Scope2/ES", Scope2View.CalculateEnergySource.as_view()),
    path("Scope2/NA", Scope2View.CalculateNAScope2Emissions.as_view()),
    path("Scope2/EU", Scope2View.CalculateEUScope2Emissions.as_view()),
    path("Scope2/Uniform", Scope2View.CalculateUniformedScope2Equations.as_view()),
    path("Scope2/Asia", Scope2View.CalculateAsiaScope2Emissions.as_view()),

    path("Scope3/SupplierSpecific", Scope3View.CalculateSupplierSpecificScope3Emissions.as_view()),
    path("Scope3/Hybrid", Scope3View.CalculateHybridScope3Emissions.as_view()),
    path("Scope3/AverageData", Scope3View.CalculateAverageDataScope3Emissions.as_view()),
    path("Scope3/SpendBased", Scope3View.CalculateSpendBasedScope3Emissions.as_view()),

    path("Scope4/GreenHydrogen", Scope4View.CalculateGreenHydrogenReplacingFossilFuels.as_view()),
    path("Scope4/WorkFromHome", Scope4View.CalculateWorkFromHomeAvoidedEmissions.as_view()),
    path("Scope4/CO2Capture", Scope4View.CalculateCO2CaptureAndSequestration.as_view()),

    path("calculate", GHGCalculateRouter.as_view()),

]


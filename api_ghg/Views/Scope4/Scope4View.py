from rest_framework.views import APIView
from django.conf import settings
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from api_ghg.Auth.AuthHelper import AuthHelper
from api.Models.Company import Company
from django.http import JsonResponse

from GSE_Backend.errors.ErrorDictionary import CustomError
import logging


'''
Scope 4 Equations for the GHG Module
Sources for equations can be found here: https://drive.google.com/drive/u/6/folders/1ZTQOT4uwMOWWhxDncuk8ywpTzuDcjJ4O
'''

# Global helper for missing parameter check
def check_missing_keys(data, required_keys):
    missing = [k for k in required_keys if data.get(k) is None]
    if missing:
        return JsonResponse({"error": f"Missing required fields: {', '.join(missing)}"}, status=400)
    return None



# -------------------- Fuel and transport ------------------------------

# 1) Electric Vehicles (EVs) replacing gasoline/diesel cars
"""
Avoided Emissions = (E_fuel - E_EV) x D_travelled

Where:
- E_fuel: CO₂ emissions per km for fossil fuel cars (kg CO2e/km)
- E_EV: CO₂ emissions per km for EVs (grid-mix based) (kg CO2e/km)
- D_travelled: Distance travelled by EVs (km)

Required:
- E_fuel (float), E_EV (float), D_travelled (float)

Returns:
- Result: avoided emissions (kg CO2e)
"""
class CalculateEVsReplacingDieselCars(APIView):
    def post(self, request):
        data = request.data
        required = ["E_fuel", "E_EV", "D_travelled"]
        resp = check_missing_keys(data, required)
        if resp: return resp

        E_fuel = data["E_fuel"]
        E_EV = data["E_EV"]
        D_travelled = data["D_travelled"]

        avoided = (E_fuel - E_EV) * D_travelled
        return JsonResponse({"Result": avoided, "Units": "kg CO2e"})
    permission_classes = [AllowAny]


# 2) Sustainable Aviation Fuel (SAF) replacing jet fuel
"""
Avoided Emissions = V_SAF x (E_jetfuel - E_SAF)

Where:
- V_SAF: Volume of SAF used (liters)
- E_jetfuel: Emission factor for conventional jet fuel (kg CO2e/liter)
- E_SAF: Emission factor for SAF (kg CO2e/liter)

Required:
- V_SAF (float), E_jetfuel (float), E_SAF (float)

Returns:
- Result: avoided emissions (kg CO2e)
"""
class CalculateSAFReplacingJetFuel(APIView):
    def post(self, request):
        data = request.data
        required = ["V_SAF", "E_jetfuel", "E_SAF"]
        resp = check_missing_keys(data, required)
        if resp: return resp

        V_SAF = data["V_SAF"]
        E_jetfuel = data["E_jetfuel"]
        E_SAF = data["E_SAF"]

        avoided = V_SAF * (E_jetfuel - E_SAF)
        return JsonResponse({"Result": avoided, "Units": "kg CO2e"})
    permission_classes = [AllowAny]


# 3) High-Speed Rail & Public Transit reducing car travel
"""
Avoided Emissions = (E_car - E_rail) x P_shifted

Where:
- E_car: Emissions per passenger-km for cars (kg CO2e/passenger-km)
- E_rail: Emissions per passenger-km for rail (kg CO2e/passenger-km)
- P_shifted: Number of passengers shifting from cars to rail

Notes:
- If your team tracks distance per shifted passenger, include optional D_passenger_km
  and compute: (E_car - E_rail) x P_shifted x D_passenger_km

Required (minimum):
- E_car (float), E_rail (float), P_shifted (float or int)

Optional:
- D_passenger_km (float)  # average passenger-km travelled per shifted passenger

Returns:
- Result: avoided emissions (kg CO2e)
"""
class CalculateRailTransitShiftAvoidedEmissions(APIView):
    def post(self, request):
        data = request.data
        required = ["E_car", "E_rail", "P_shifted"]
        resp = check_missing_keys(data, required)
        if resp: return resp

        E_car = data["E_car"]
        E_rail = data["E_rail"]
        P_shifted = data["P_shifted"]
        D_passenger_km = data.get("D_passenger_km")  # optional

        diff = (E_car - E_rail)
        avoided = diff * P_shifted * D_passenger_km if D_passenger_km is not None else diff * P_shifted

        return JsonResponse({"Result": avoided, "Units": "kg CO2e"})
    permission_classes = [AllowAny]


# -------------------- Energy Sector -----------------------------------



# -------------------- Industrial Processes ----------------------------



# -------------------- Circular Economy --------------------------------



# -------------------- Digitalization and Remote Work ------------------



# -------------------- Carbon Capture and Storage ----------------------


# -------------------- Green Hydrogen Replacing Fossil Fuels --------------------
"""
    Calculate avoided emissions from using green hydrogen to replace fossil fuels.

    Equation:
    Avoided Emissions=(Efossil−EH2)×Hused

    Where:
    Efossil - Emission factor for the fossil fuel replaced (kg CO₂ per kg fuel or MJ)
    EH2 - Emission factor for the hydrogen (kg CO₂ per kg H₂), depends on production method
    Hused - Total amount of hydrogen consumed (kg or MJ)

    Required Parameters:
    - Efossil: Emission factor for the fossil fuel replaced (float)
    - EH2: Emission factor for the hydrogen (float)
    - Hused: Total amount of hydrogen consumed (float)
"""
class CalculateGreenHydrogenReplacingFossilFuels(APIView):
    def post(self, request):
        data = request.data
        required = ["Efossil", "EH2", "Hused"]
        resp = check_missing_keys(data, required)
        if resp: return resp
        efossil = data["Efossil"]
        eh2 = data["EH2"]
        hused = data["Hused"]
        emissions = (efossil - eh2) * hused
        return JsonResponse({"Result": emissions, "Units": "kg CO2e"})
    permission_classes = [AllowAny]

# -------------------- Work‐From‐Home (Reducing Commuting Emissions) --------------------
"""
    Calculate avoided emissions from working from home.
    Equation:
    Avoided Emissions=Nemployees​×E(commute)×D(remote)

    Where:
    Nemployees​ - Number of employees working remotely
    E(commute) - CO₂ emissions per employee commute (could be kg CO₂ per km or per day)
    D(remote) - Number of remote workdays per year
    
    Required Parameters:
    - N_employees: Number of employees working remotely (int)
    - E_commute: CO₂ emissions per employee commute (float)
    - D_remote: Number of remote workdays per year (int)
"""
class CalculateWorkFromHomeAvoidedEmissions(APIView):
    def post(self, request):
        data = request.data
        required = ["N_employees", "E_commute", "D_remote"]
        resp = check_missing_keys(data, required)
        if resp: return resp
        N_employees = data["N_employees"]
        E_commute = data["E_commute"]
        D_remote = data["D_remote"]
        emissions = N_employees * E_commute * D_remote
        return JsonResponse({"Result": emissions, "Units": "kg CO2e"})
    permission_classes = [AllowAny]

# -------------------- CO2 Capture and Sequestration --------------------
"""
    Calculate avoided emissions from CO2 capture and sequestration.
    
    Equation:
    Avoided Emissions=Ccaptured​×Sefficiency​	
    
    Where:
    C_captured​ - Total CO₂ captured (tonnes per year)
    S_efficiency​ - Storage efficiency factor (fraction of CO₂ that remains sequestered)

    Required Parameters:
    - _captured​: Total CO₂ captured (tonnes per year) (float)
    - _efficiency​: Storage efficiency factor (fraction of CO₂ that remains sequestered) (float)
"""
class CalculateCO2CaptureAndSequestration(APIView):
    def post(self, request):
        data = request.data
        required = ["C_captured", "S_efficiency"]
        resp = check_missing_keys(data, required)
        if resp: return resp
        C_captured = data["C_captured"]
        S_efficiency = data["S_efficiency"]
        emissions = C_captured * S_efficiency
        return JsonResponse({"Result": emissions, "Units": "kg CO2e"})
    permission_classes = [AllowAny]
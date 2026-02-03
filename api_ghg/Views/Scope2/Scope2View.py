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

def check_missing_keys(data, required_keys):
    missing = [key for key in required_keys if key not in data]
    if missing:
        return JsonResponse({"error": f"Missing required fields: {', '.join(missing)}"}, status=400)
    return None

'''
Scope 2 Equations for the GHG Module
Sources for equations can be found here: https://drive.google.com/drive/u/6/folders/1ZTQOT4uwMOWWhxDncuk8ywpTzuDcjJ4O

Split into 6 categories: EU, NA, Asia, Uniformed equations (Uni), Energy resource (ES)
Following the same naming conventions as scope 1
'''

# -----------------------------------------------------------------------------------------------------------------
# EU
# -----------------------------------------------------------------------------------------------------------------
"""
Equations:
Equation used for electricity consumption: Total MWh = (Square Footage x kWh/Sq ft)/1000a
Location-based: Scope 2 Emissions(Location-Based)=Electricity Consumption×Grid Average Emission Factor
𝐺𝑒𝑛𝑒𝑟𝑎𝑡𝑖𝑜𝑛𝐸𝑛𝑒𝑟𝑔𝑦 𝑆𝑜𝑢𝑟𝑐𝑒𝑥 − 𝐼𝑠𝑠𝑢𝑒𝑑 𝐴𝑡𝑡𝑟𝑖𝑏𝑢𝑡𝑒𝑠𝐸𝑛𝑒𝑟𝑔𝑦 𝑆𝑜𝑢𝑟𝑐𝑒𝑥 + 𝐸𝑥𝑝𝑖𝑟𝑒𝑑 𝐴𝑡𝑡𝑟𝑖𝑏𝑢𝑡𝑒𝑠𝐸𝑛𝑒𝑟𝑔𝑦 𝑆𝑜𝑢𝑟𝑐𝑒𝑥 = 𝐷𝑜𝑚𝑒𝑠𝑡𝑖𝑐 𝑅𝑒𝑠𝑖𝑑𝑢𝑎𝑙 𝑀𝑖𝑥𝐸𝑛𝑒𝑟𝑔𝑦 𝑆𝑜𝑢𝑟𝑐𝑒𝑥 
(Market-Based)=∑(Electricity Consumption×Emission Factor for the Specific Source)
Volume of a Domestic Residual Mix: For each of Domestic RM_Energy_Source = Domestic Residual Mix
Share of Energy Source x in the Domestic Residual Mix: % in the Domestic RM_Energy_Sorce_X= Domestic Resicual Mix_Energy_Source_X/Domestic Residual Mix
Emissions = Electricity x EF 
Where: Emissions = Mass of CO2, CH4, or N2O emitted 
Electricity = Quantity of electricity purchased 
EF = CO2, CH4, or N2O emission factor

"""

class CalculateEUScope2Emissions(APIView):
    permission_classes = [AllowAny]
    def post(self, request):
        method = request.data.get("method")
        if not method:
            return JsonResponse({"error": "Method parameter required (e.g., 'ES_eq_1')"}, status=400)
        try:
            return getattr(self, method)(request)
        except AttributeError:
            return JsonResponse({"error": f"Method {method} not found"}, status=400)
    
    
    """
    Location-based: Scope 2 Emissions(Location-Based)=Electricity Consumption×Grid Average Emission Factor
    """
    def EU_eq_1(self, request):
        data = request.data
        required = ["EC", "GAEF"]
        resp = check_missing_keys(data, required)
        if resp: return resp
        EC = data.get("EC")
        GAEF = data.get("GAEF")
        EM = EC * GAEF
        return JsonResponse({"Result": EM})


    """
    Equation used for electricity consumption: Total MWh = (Square Footage x kWh/Sq ft)/1000a
    """
    def EU_eq_2(self, request):
        data = request.data
        required = ["SF", "kWh", "Sq_ft"]
        resp = check_missing_keys(data, required)
        if resp: return resp
        SF = data.get("SF")
        kWh = data.get("kWh") 
        Sq_ft = data.get("Sq_ft")
        MWh = (SF * (kWh/Sq_ft))/1000
        return JsonResponse({"Result": MWh})

    """
    (Market-Based)=∑(Electricity Consumption×Emission Factor for the Specific Source)
    """
    def EU_eq_3(self, request):
        data = request.data
        required = ["A_set", "EF", "EC"]
        resp = check_missing_keys(data, required)
        if resp: return resp
        A_set = data.get("A_set")
        EF = data.get("EF")
        EC = data.get("EC")
        EM=sum(EF(a)*EC(a) for a in A_set)
        return JsonResponse({"Result": EM})


    """
    𝐺𝑒𝑛𝑒𝑟𝑎𝑡𝑖𝑜𝑛𝐸𝑛𝑒𝑟𝑔𝑦 𝑆𝑜𝑢𝑟𝑐𝑒𝑥 − 𝐼𝑠𝑠𝑢𝑒𝑑 𝐴𝑡𝑡𝑟𝑖𝑏𝑢𝑡𝑒𝑠𝐸𝑛𝑒𝑟𝑔𝑦 𝑆𝑜𝑢𝑟𝑐𝑒𝑥 + 𝐸𝑥𝑝𝑖𝑟𝑒𝑑 𝐴𝑡𝑡𝑟𝑖𝑏𝑢𝑡𝑒𝑠𝐸𝑛𝑒𝑟𝑔𝑦 𝑆𝑜𝑢𝑟𝑐𝑒𝑥 = 𝐷𝑜𝑚𝑒𝑠𝑡𝑖𝑐 𝑅𝑒𝑠𝑖𝑑𝑢𝑎𝑙 𝑀𝑖𝑥𝐸𝑛𝑒𝑟𝑔𝑦 𝑆𝑜𝑢𝑟𝑐𝑒𝑥 
    """
    def EU_eq_4(self, request):
        data = request.data
        required = ["GES", "IAES", "EAES"]
        resp = check_missing_keys(data, required)
        if resp: return resp
        GES = data.get("GES")
        IAES = data.get("IAES")
        EAES = data.get("EAES")
        DRMES = GES - IAES + EAES
        return JsonResponse({"Result": DRMES})
        

    """
    Volume of a Domestic Residual Mix: For each of Domestic RM_Energy_Source = Domestic Residual Mix
    """
    def EU_eq_5(self, request):
        data = request.data
        required = ["DRMES", "A_set"]
        resp = check_missing_keys(data, required)
        if resp: return resp
        DRMES = data.get("DRMES")
        A_set = data.get("A_set")
        DRM = sum(DRMES(a) for a in A_set)

    """
    Share of Energy Source x in the Domestic Residual Mix: % in the Domestic RM_Energy_Sorce_X= 
    Domestic Resicual Mix_Energy_Source_X/Domestic Residual Mix
    """
    def EU_eq_6(self, request):
        data = request.data
        required = ["DRM", "DRME_x"]
        resp = check_missing_keys(data, required)
        if resp: return resp
        DRME_x = data.get("DRME_x")
        DRM = data.get("DRM")
        DRMEP = DRME_x/DRM
        return JsonResponse({"Result": DRMEP})

    """
    Emissions = Electricity x EF 
    Where: Emissions = Mass of CO2, CH4, or N2O emitted 
    Electricity = Quantity of electricity purchased 
    EF = CO2, CH4, or N2O emission factor
    """
    def EU_eq_7(self, request):
        data = request.data
        required = ["Elec", "EF"]
        resp = check_missing_keys(data, required)
        if resp: return resp
        Elec = data.get("Elec")
        EF = data.get("EF")
        EM= Elec * EF
        return JsonResponse({"Result": EM})




# -----------------------------------------------------------------------------------------------------------------
# NA
# -----------------------------------------------------------------------------------------------------------------
class CalculateNAScope2Emissions(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        method = request.data.get("method")
        if not method:
            return JsonResponse({"error": "Method parameter required (e.g., 'NA_eq_1')"}, status=400)
        try:
            return getattr(self, method)(request)
        except AttributeError:
            return JsonResponse({"error": f"Method {method} not found"}, status=400)

    """
    Equation: Emissions = Electricity x EF
    

    Expected Input:
    electricity: Quantity of electricity purchased during the reporting year (in MWh or kWh)
    EF : Emission factors for each pollutant (e.g., {"CO2": 500, "CH4": 0.05, "N2O": 0.01}) in lb/MWh or kg/kWh

    Expected Output:
    Emissions: Dictionary with pollutant as key and total emissions (in lb or kg) as value
    """
    def NA_eq_1(self, request):
        data = request.data
        required = ["electricity", "EF"]
        resp = check_missing_keys(data, required)
        if resp: return resp

        electricity = data["electricity"]
        EF = data["EF"]

        emissions = {pollutant: round(electricity * factor, 4) for pollutant, factor in EF.items()}
        return JsonResponse({"Result": emissions})
    

    """
    NA_eq_2 - eGRID-Based Emissions Calculation

    Equation:
    Emissions = eGRID output emission rate (lbs/MWh) x Electricity usage (MWh)

    Expected Input:
    electricity_usage: Electricity consumed in MWh
    EF: Emission factor from eGRID in lbs/MWh (can be pollutant-specific, e.g., CO2, NOx, SO2)

    Expected Output:
    emissions: Total indirect emissions (in lbs) for the specified pollutant
    """
    def NA_eq_2(self, request):
        data = request.data
        required = ["electricity_usage", "EF"]
        resp = check_missing_keys(data, required)
        if resp: return resp

        electricity_usage = data["electricity_usage"]
        EF = data["EF"]

        emissions = electricity_usage * EF
        return JsonResponse({"Result": round(emissions, 2)})


# -----------------------------------------------------------------------------------------------------------------
# Asia
# -----------------------------------------------------------------------------------------------------------------
class CalculateAsiaScope2Emissions(APIView):
    permission_classes = [AllowAny]
    
    def post(self, request):
        method = request.data.get("method")
        if not method:
            return JsonResponse({"error": "Method parameter required (e.g., 'Asia_eq_1')"}, status=400)
        try:
            return getattr(self, method)(request)
        except AttributeError:
            return JsonResponse({"error": f"Method {method} not found"}, status=400)

    """
    Market Based Equation for Asia:
    Emissions = kWh of electricity used × Contract source emissions factor
    """
    def Asia_eq_1(self, request):
        data = request.data
        required = ["kWh", "contract_source_EF"]
        resp = check_missing_keys(data, required)
        if resp: return resp
        
        kWh = data.get("kWh")
        contract_source_EF = data.get("contract_source_EF")
        
        emissions = kWh * contract_source_EF
        return JsonResponse({"Result": emissions})

    """
    Location Based Equation for Asia:
    Emissions = kWh of electricity used × Local Grid Emissions Factor
    """
    def Asia_eq_2(self, request):
        data = request.data
        required = ["kWh", "local_grid_EF"]
        resp = check_missing_keys(data, required)
        if resp: return resp
        
        kWh = data.get("kWh")
        local_grid_EF = data.get("local_grid_EF")
        
        emissions = kWh * local_grid_EF
        return JsonResponse({"Result": emissions})


# -----------------------------------------------------------------------------------------------------------------
#Uniformed equations
# -----------------------------------------------------------------------------------------------------------------
class CalculateUniformedScope2Equations(APIView):
    permission_classes = [AllowAny]
    
    def post(self, request):
        method = request.data.get("method")
        if not method:
            return JsonResponse({"error": "Method parameter required (e.g., 'Uni_eq_1')"}, status=400)
        try:
            return getattr(self, method)(request)
        except AttributeError:
            return JsonResponse({"error": f"Method {method} not found"}, status=400)

    """
    Square Footage calculation:
    Square Footage = 150 sqft × number of employees
    """
    def Uni_eq_1(self, request):
        data = request.data
        required = ["number_of_employees"]
        resp = check_missing_keys(data, required)
        if resp: return resp
        
        number_of_employees = data.get("number_of_employees")
        square_footage = 150 * number_of_employees
        return JsonResponse({"Result": square_footage})

    """
    Allocated Consumption:
    Allocated Consumption = Building's total Electricity × Sqft occupancy ratio
    """
    def Uni_eq_2(self, request):
        data = request.data
        required = ["building_total_electricity", "sqft_occupancy_ratio"]
        resp = check_missing_keys(data, required)
        if resp: return resp
        
        building_total_electricity = data.get("building_total_electricity")
        sqft_occupancy_ratio = data.get("sqft_occupancy_ratio")
        
        allocated_consumption = building_total_electricity * sqft_occupancy_ratio
        return JsonResponse({"Result": allocated_consumption})

    """
    Total Consumption:
    Total Consumption = Location based data - Total mWhs of REC's Purchased
    """
    def Uni_eq_3(self, request):
        data = request.data
        required = ["location_based_data", "total_mWhs_RECs_purchased"]
        resp = check_missing_keys(data, required)
        if resp: return resp
        
        location_based_data = data.get("location_based_data")
        total_mWhs_RECs_purchased = data.get("total_mWhs_RECs_purchased")
        
        total_consumption = location_based_data - total_mWhs_RECs_purchased
        return JsonResponse({"Result": total_consumption})

    """
    Scope 2 Consumption:
    Scope 2 Consumption = Scope 1 (energy generator company)
    """
    def Uni_eq_4(self, request):
        data = request.data
        required = ["scope_1_energy_generator"]
        resp = check_missing_keys(data, required)
        if resp: return resp
        
        scope_1_energy_generator = data.get("scope_1_energy_generator")
        scope_2_consumption = scope_1_energy_generator
        return JsonResponse({"Result": scope_2_consumption})

    """
    Total Energy Consumption:
    Total Energy Consumption = Self Generated (scope 1) + Energy Purchased from the grid
    """
    def Uni_eq_5(self, request):
        data = request.data
        required = ["self_generated_scope1", "energy_purchased_from_grid"]
        resp = check_missing_keys(data, required)
        if resp: return resp
        
        self_generated_scope1 = data.get("self_generated_scope1")
        energy_purchased_from_grid = data.get("energy_purchased_from_grid")
        
        total_energy_consumption = self_generated_scope1 + energy_purchased_from_grid
        return JsonResponse({"Result": total_energy_consumption})

    """
    SA mWh calculation:
    mWh = (Square Footage × kWh per Square foot) / 1000
    """
    def Uni_eq_6(self, request):
        data = request.data
        required = ["square_footage", "kWh_per_sqft"]
        resp = check_missing_keys(data, required)
        if resp: return resp
        
        square_footage = data.get("square_footage")
        kWh_per_sqft = data.get("kWh_per_sqft")
        
        mWh = (square_footage * kWh_per_sqft) / 1000
        return JsonResponse({"Result": mWh})

    """
    Domestic Residual Mix (Alternative formula):
    Domestic Residual mix = Generation + Physical new import - Physical Export + expired attributes - Issued Attributes
    """
    def Uni_eq_7(self, request):
        data = request.data
        required = ["generation", "physical_new_import", "physical_export", "expired_attributes", "issued_attributes"]
        resp = check_missing_keys(data, required)
        if resp: return resp
        
        generation = data.get("generation")
        physical_new_import = data.get("physical_new_import")
        physical_export = data.get("physical_export")
        expired_attributes = data.get("expired_attributes")
        issued_attributes = data.get("issued_attributes")
        
        domestic_residual_mix = generation + physical_new_import - physical_export + expired_attributes - issued_attributes
        return JsonResponse({"Result": domestic_residual_mix})

    """
    Residual mix calculation (general):
    Residual mix = Generation + Physical new import - Physical Export + expired attributes - Issued Attributes
    """
    def Uni_eq_8(self, request):
        data = request.data
        required = ["generation", "physical_new_import", "physical_export", "expired_attributes", "issued_attributes"]
        resp = check_missing_keys(data, required)
        if resp: return resp
        
        generation = data.get("generation")
        physical_new_import = data.get("physical_new_import")
        physical_export = data.get("physical_export")
        expired_attributes = data.get("expired_attributes")
        issued_attributes = data.get("issued_attributes")
        
        residual_mix = generation + physical_new_import - physical_export + expired_attributes - issued_attributes
        return JsonResponse({"Result": residual_mix})

    """
    Generation calculation:
    Generation = ((Voltage(V) x Current(A))/1,000) x Time (hours)
    """
    def Uni_eq_9(self, request):
        data = request.data
        required = ["voltage", "current", "time_hours"]
        resp = check_missing_keys(data, required)
        if resp: return resp
        
        voltage = data.get("voltage")
        current = data.get("current")
        time_hours = data.get("time_hours")
        
        generation = ((voltage * current) / 1000) * time_hours
        return JsonResponse({"Result": generation})

    """
    Alternative Domestic Residual Mix calculation:
    Domestic Residual Mix = Generation + Imported Attributes - Exported Attribute - Cancelled Attributes
    """
    def Uni_eq_10(self, request):
        data = request.data
        required = ["generation", "imported_attributes", "exported_attributes", "cancelled_attributes"]
        resp = check_missing_keys(data, required)
        if resp: return resp
        
        generation = data.get("generation")
        imported_attributes = data.get("imported_attributes")
        exported_attributes = data.get("exported_attributes")
        cancelled_attributes = data.get("cancelled_attributes")
        
        domestic_residual_mix = generation + imported_attributes - exported_attributes - cancelled_attributes
        return JsonResponse({"Result": domestic_residual_mix})




# -----------------------------------------------------------------------------------------------------------------
# Enery source
# -----------------------------------------------------------------------------------------------------------------



class CalculateEnergySource(APIView):
    permission_classes = [AllowAny]
    """
    Calculate energy output for renewable sources such as hydropower and wind.
    """

    def post(self, request):
        method = request.data.get("method")
        if not method:
            return JsonResponse({"error": "Method parameter required (e.g., 'ES_eq_1')"}, status=400)
        try:
            return getattr(self, method)(request)
        except AttributeError:
            return JsonResponse({"error": f"Method {method} not found"}, status=400)

    """
    Hydropower Output Formula
    P = η * p * g * h * Q, where Q = A * v

    Expected inputs:
    η: Turbine efficiency (n)
    p: Water density (p)
    g: Gravitational acceleration
    h: Head height
    Q: Discharge (flow rate)

    Expected output:
    P: Power output in watts
    """
    def ES_eq_1(self, request):
        data = request.data
        required = ["n", "p", "g", "h", "Q"]
        resp = check_missing_keys(data, required)
        if resp: return resp

        n = data["n"]
        p = data["p"]
        g = data["g"]
        h = data["h"]
        Q = data["Q"]

        P = n * p * g * h * Q
        return JsonResponse({"Result": P})

    """
    Windpower Output Formula
    P = 1/2 * p * A * v³

    Expected inputs:
    p: Air density (p)
    A: Cross-sectional area
    v: Wind velocity

    Expected output:
    P: Power output in watts
    """
    def ES_eq_2(self, request):
        data = request.data
        required = ["p", "A", "v"]
        resp = check_missing_keys(data, required)
        if resp: return resp

        p = data["p"]
        A = data["A"]
        v = data["v"]

        P = 0.5 * p * A * (v ** 3)
        return JsonResponse({"Result": P})


from rest_framework.views import APIView
from django.conf import settings
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from api_ghg.Auth.AuthHelper import AuthHelper
from api.Models.Company import Company
from django.http import JsonResponse
'''
Scope 1 Equations for the GHG Module
Sources for equations can be found here: https://drive.google.com/drive/u/6/folders/1ZTQOT4uwMOWWhxDncuk8ywpTzuDcjJ4O

Split into 4 categories: Aviation, Marine, Railways, Road

'''

# Global helper for missing parameter check
def check_missing_keys(data, required_keys):
    missing = [k for k in required_keys if data.get(k) is None]
    if missing:
        return JsonResponse({"error": f"Missing required fields: {', '.join(missing)}"}, status=400)
    return None
from GSE_Backend.errors.ErrorDictionary import CustomError
import logging


# -----------------------------------------------------------------------------------------------------------------
# REGION - NORTH AMERICA (NA)
# -----------------------------------------------------------------------------------------------------------------

# -------------------- AVIATION --------------------
class CalculateNorthAmericanAviationCO2Emissions(APIView):
    def post(self, request):
        method = request.data.get("method")
        if not method:
            return JsonResponse({"error": "Method parameter required (e.g., 'NA_eq_1')"}, status=400)
        try:
            return getattr(self, method)(request)
        except AttributeError:
            return JsonResponse({"error": f"Method {method} not found"}, status=400)
    permission_classes = [AllowAny]
    """
    Calculate CO2 emissions for North America for Aviation based on various parameters.
    """

    def NA_eq_1(self, request):
        """
        NA Basic equation: Emissions = Fuel Use × Emission Factor
        """
        data = request.data
        required = ["fuel_use", "emission_factor"]
        resp = check_missing_keys(data, required)
        if resp: return resp
        fuel_use = data["fuel_use"]
        emission_factor = data["emission_factor"]
        emissions = fuel_use * emission_factor
        return JsonResponse({"Result": emissions})

# -------------------- MARINE --------------------
class CalculateNorthAmericanMarineCO2Emissions(APIView):
    def post(self, request):
        method = request.data.get("method")
        if not method:
            return JsonResponse({"error": "Method parameter required (e.g., 'USA_eq_1')"}, status=400)
        try:
            return getattr(self, method)(request)
        except AttributeError:
            return JsonResponse({"error": f"Method {method} not found"}, status=400)
    permission_classes = [AllowAny]
    """
    Calculate CO2 emissions for North America for Marine based on various parameters.
    """

    # USA EQUATIONS
    """
    Equation: E = P × A × EF × LLAF
    Expected Input:
    - P: Engine operating power (in kW)
    - A: Engine operating activity (in hours)
    - EF: Emission factor (in g/kWh)
    - LLAF: Low load adjustment factor (unitless)

    Expected Output:
    - E: Per vessel emissions (in grams)
    """
    def USA_eq_1(self, request):
        data = request.data
        required = ["P", "A", "EF"]
        resp = check_missing_keys(data, required)
        if resp: return resp
        P = data["P"]
        A = data["A"]
        EF = data["EF"]
        LLAF = data.get("LLAF", 1)
        E = P * A * EF * LLAF
        return JsonResponse({"Result": round(E, 2)})

    """
    Equation: EFPM10 = PMbase + (Sact × BSFC × FSC × MWR)
    Expected Input:
    - PMbase: Base PM emission factor (in g/kWh)
    - Sact: Actual fuel sulfur level (weight ratio, unitless)
    - BSFC: Brake-specific fuel consumption (in g/kWh)
    - FSC: Fraction of sulfur in fuel that is converted to sulfate (unitless)
    - MWR: Molecular weight ratio of sulfate (unitless)

    Expected Output:
    - EFPM10: Adjusted PM10 emission factor (in g/kWh)
    """
    def USA_eq_2(self, request):
        data = request.data
        required = ["PM_base", "S_act", "BSFC", "FSC", "MWR"]
        resp = check_missing_keys(data, required)
        if resp: return resp
        PM_base = data["PM_base"]
        S_act = data["S_act"]
        BSFC = data["BSFC"]
        FSC = data["FSC"]
        MWR = data["MWR"]
        EF_PM10 = PM_base + (S_act * BSFC * FSC * MWR)
        return JsonResponse({"Result": round(EF_PM10, 2)})

    
    """
    Equation: Ep = Pp × A × EF × LLAF
    Expected Input:
    - Pp: Propulsion engine operating power for each AIS record (in kW)
    - A: Time interval between consecutive AIS records (in hours)
    - EF: Emission factor (in g/kWh)
    - LLAF: Low load adjustment factor per AIS record (unitless)

    Expected Output:
    - Ep: Propulsion engine emissions per AIS record (in grams)
    """
    def USA_eq_3(self, request):
        data = request.data
        required = ["P_p", "A", "EF"]
        resp = check_missing_keys(data, required)
        if resp: return resp
        P_p = data["P_p"]
        A = data["A"]
        EF = data["EF"]
        LLAF = data.get("LLAF", 1)
        E_p = P_p * A * EF * LLAF
        return JsonResponse({"Result": round(E_p, 2)})
    """
    Equation: Ep,i = Pp,i × Ai × EF × LLAFi
    Expected Input:
    - Pp_i: Propulsion engine operating power for operating mode i (in kW)
    - Ai: Time spent in operating mode i (in hours)
    - EF: Emission factor (in g/kWh)
    - LLAFi: Low load adjustment factor for mode i (unitless)

    Expected Output:
    - Ep_i: Propulsion emissions for mode i (in grams)
    """
    def USA_eq_4(self, request):
        data = request.data
        required = ["P_p_i", "A_i", "EF", "LLAF_i"]
        resp = check_missing_keys(data, required)
        if resp: return resp
        P_p_i = data["P_p_i"]
        A_i = data["A_i"]
        EF = data["EF"]
        LLAF_i = data["LLAF_i"]
        E_p_i = sum(P_p_i[i] * A_i[i] * EF * LLAF_i[i] for i in P_p_i)
        return JsonResponse({"Result": round(E_p_i, 4)})

    """
    Equation: Ei = Ep,i + Ea,i + Eb,i
    Expected Input:
    - Ep_i: Propulsion engine emissions for mode i (in grams)
    - Ea_i: Auxiliary engine emissions for mode i (in grams)
    - Eb_i: Boiler emissions for mode i (in grams)
    Expected Output:
    - Ei: Total vessel emissions for operating mode i (in grams)
    """
    def USA_eq_5(self, request):
        data = request.data
        required = ["E_p", "E_a", "E_b"]
        resp = check_missing_keys(data, required)
        if resp: return resp
        E_p = data["E_p"]
        E_a = data["E_a"]
        E_b = data["E_b"]
        E_i = E_p + E_a + E_b
        return JsonResponse({"Result": round(E_i, 2)})

    """
    Equation: E = P × LF × A × EF
    Expected Input:
    - P: Engine power (in kW)
    - LF: Load factor (unitless)
    - A: Engine operating activity (in hours)
    - EF: Emission factor (in g/kWh)

    Expected Output:
    - E: Total vessel emissions (in grams)
    """
    def USA_eq_6(self, request):
        data = request.data
        required = ["P", "LF", "A", "EF"]
        resp = check_missing_keys(data, required)
        if resp: return resp
        P = data["P"]
        LF = data["LF"]
        A = data["A"]
        EF = data["EF"]
        E = P * LF * A * EF
        return JsonResponse({"Result": round(E, 4)})

    # MEXICO EQUATIONS 

    """
    Equation: E_ip = (Qr_i × EF_rp) + (Qd_i × EF_dp)

    Expected Input:
    - Qr_i: Quantity of residual oil consumed in area i (in tons)
    - Qd_i: Quantity of distillate oil consumed in area i (in tons)
    - EF_rp: Emission factor for pollutant p for residual oil (in g/ton)
    - EF_dp: Emission factor for pollutant p for distillate oil (in g/ton)

    Expected Output:
    - E_ip: Total emissions of pollutant p produced annually by vessels operating within area i (in grams)
    """

    def MEX_eq_1(self, request):
        data = request.data
        required = ["Q_ri", "EF_rp", "Q_di", "EF_dp"]
        resp = check_missing_keys(data, required)
        if resp: return resp
        Q_ri = data["Q_ri"]
        EF_rp = data["EF_rp"]
        Q_di = data["Q_di"]
        EF_dp = data["EF_dp"]
        E_ip = (Q_ri * EF_rp) + (Q_di * EF_dp)
        return JsonResponse({"Result": round(E_ip, 2)})

# -------------------- RAILROAD --------------------
class CalculateNorthAmericanRailwaysCO2Emissions(APIView):
    def post(self, request):
        method = request.data.get("method")
        if not method:
            return JsonResponse({"error": "Method parameter required (e.g., 'NA_eq_1')"}, status=400)
        try:
            return getattr(self, method)(request)
        except AttributeError:
            return JsonResponse({"error": f"Method {method} not found"}, status=400)
    permission_classes = [AllowAny]
    
    """
    Calculate CO2 emissions for North America for Railroad based on various parameters.
    """

    """
    NA_eq_1 – Railroad fuel consumption allocation by track length:
    F_ci = F_cn x (TL_i / TL_n)

    Expected input:
    - F_cn: national railroad fuel consumption (in liters)
    - TL_i: track length for inventory area i (in km)
    - TL_n: national railroad track length (in km)

    Expected output:
    - F_ci: estimated railroad fuel consumption for inventory area i (in liters)
    """
    def NA_eq_1(self, request):
        data = request.data
        required = ["F_cn", "TL_i", "TL_n"]
        resp = check_missing_keys(data, required)
        if resp: return resp
        F_cn = data["F_cn"]
        TL_i = data["TL_i"]
        TL_n = data["TL_n"]
        F_ci = F_cn * (TL_i / TL_n)
        return JsonResponse({"Result": F_ci})

    """
    NA_eq_2 – Emissions from allocated fuel consumption:
    EL_pi = F_ci x EF_lp

    Expected input:
    - F_ci: railroad fuel consumption for inventory area i (in liters/year)
    - EF_lp: emission factor for pollutant p (in kg/liter)

    Expected output:
    - EL_pi: estimated annual emissions (in kg) for pollutant p in inventory area i
    """
    def NA_eq_2(self, request):
        data = request.data
        required = ["F_ci", "EF_lp"]
        resp = check_missing_keys(data, required)
        if resp: return resp
        F_ci = data["F_ci"]
        EF_lp = data["EF_lp"]
        EL_pi = F_ci * EF_lp
        return JsonResponse({"Result": EL_pi})

# -------------------- ROAD --------------------
''' No Road equations provided in the original code snippet.'''


# -----------------------------------------------------------------------------------------------------------------
# REGION - EUROPE (EU)
# -----------------------------------------------------------------------------------------------------------------

# ------------------------------ AVIATION ------------------------------
class CalculateEuropeanAviationCO2Emissions(APIView):
        def post(self, request):
            method = request.data.get("method")
            if not method:
                return JsonResponse({"error": "Method parameter required (e.g., 'EU_eq_1')"}, status=400)
            try:
                return getattr(self, method)(request)
            except AttributeError:
                return JsonResponse({"error": f"Method {method} not found"}, status=400)
        permission_classes = [AllowAny]
        """
        Calculate CO2 emissions for Europe for Aviation based on various parameters.
        """

        """
        Simplified EU equation: Em = AD * EF
        Where:
        - Em = Emissions [t CO₂]
        - AD = Activity data (fuel consumed) [t]
        - EF = Emission factor [t CO₂/t fuel]
        """
        def EU_eq_1(self, request): 
            data = request.data
            required = ["AD", "EF"]
            resp = check_missing_keys(data, required)
            if resp: return resp
            AD = data["AD"]
            EF = data["EF"]
            Em = AD * EF
            return JsonResponse({"Result": Em})
        
        """
        EU Method A: F_N,A = T_N - T_N+1 + U_N+1
        Where:
        - F_N,A = Fuel consumed for the flight [t]
        - T_N = Fuel in tanks after uplift for flight [t]
        - T_N+1 = Fuel in tanks after uplift for next flight [t]
        - U_N+1 = Fuel uplift for next flight [t]
        """
        def EU_eq_2(self, request): 
            data = request.data
            required = ["T_N", "T_N_1", "U_N_1"]
            resp = check_missing_keys(data, required)
            if resp: return resp
            T_N = data["T_N"]
            T_N_1 = data["T_N_1"]
            U_N_1 = data["U_N_1"]
            F_NA = T_N - T_N_1 + U_N_1
            return JsonResponse({"Result": F_NA})

        """
        EU Method B: F_N,B = R_N-1 - R_N + U_N
        (Same as Uniform equation 1)
        """
        def EU_eq_3(self, request):
            return self.Uni_eq_1(request)

# ---------------------------------- MARINE ------------------------------
class CalculateEuropeanMarineCO2Emissions(APIView):
    def post(self, request):
        method = request.data.get("method")
        if not method:
            return JsonResponse({"error": "Method parameter required (e.g., 'EU_eq_1')"}, status=400)
        try:
            return getattr(self, method)(request)
        except AttributeError:
            return JsonResponse({"error": f"Method {method} not found"}, status=400)
    permission_classes = [AllowAny]
    """ 
    Calculate CO2 emissions for Europe for Marine based on various parameters.
    """

    '''
    Total CO2 emissions : CO2_MRV = sum((M_i - M_iNC) * EF_CO2_i)

    Expected input:
    - M_i: dict of total fuel mass by type (e.g. {"diesel": 100})
    - M_iNC: dict of non-combusted fuel by type
    - EF_CO2: dict of CO2 emission factors (kg CO2/ton)

    Expected output:
    - Result: total CO2 emissions (kg CO2)
    '''
    def EU_eq_1(self, request):
       
        data = request.data
        required = ["M_i", "M_iNC", "EF_CO2"]
        resp = check_missing_keys(data, required)
        if resp: return resp
        M_i = data.get("M_i", {})
        M_iNC = data.get("M_iNC", {})
        EF_CO2 = data.get("EF_CO2", {})

        CO2 = sum((M_i[fuel] - M_iNC.get(fuel, 0)) * EF_CO2.get(fuel, 0) for fuel in M_i)
        return JsonResponse({"Result": round(CO2, 4)})

    '''
    CH4 emissions : CH4_MRV = sum((M_i - M_iNC) * EF_CH4_i) + CH4_s
    Expected input:
    - M_i: dict of total fuel mass by type
    - M_iNC: dict of non-combusted fuel mass
    - EF_CH4: dict of CH4 emission factors (kg CH4/ton)
    - CH4_s: supplementary CH4 emissions (optional, default = 0)

    Expected output:
    - Result: total CH4 emissions (kg CH4)
    '''
    def EU_eq_2(self, request):

        data = request.data
        required = ["M_i", "M_iNC", "EF_CH4", "CH4_s"]
        resp = check_missing_keys(data, required)
        if resp: return resp
        M_i = data.get("M_i", {})
        M_iNC = data.get("M_iNC", {})
        EF_CH4 = data.get("EF_CH4", {})
        CH4_s = data.get("CH4_s", 0)

        CH4 = sum((M_i[fuel] - M_iNC.get(fuel, 0)) * EF_CH4.get(fuel, 0) for fuel in M_i) + CH4_s
        return JsonResponse({"Result": round(CH4, 4)})

    '''
    M_iNC (slippage-adjusted uncombusted fuel mass) M_iNC[fuel] = sum(M_ij * C_ij / 100)

    Expected input:
    - M_ij: dict with keys as (fuel, engine) and values as fuel mass
    - C_ij: dict with keys as (fuel, engine) and values as % slippage (uncombusted fraction)

    Expected output:
    - Result: dict of M_iNC for each fuel type
    '''
    def EU_eq_3(self, request):
        data = request.data
        required = ["M_i","M_iNC", "EF_N2O"]
        resp = check_missing_keys(data, required)
        if resp: return resp
        M_i = data.get("M_i", {})
        M_iNC = data.get("M_iNC", {})
        EF_N2O = data.get("EF_N2O", {})

        N2O = sum((M_i[fuel] - M_iNC.get(fuel, 0)) * EF_N2O.get(fuel, 0) for fuel in M_i)
        return JsonResponse({"Result": round(N2O, 4)})

    '''
    M_iNC (slippage-adjusted uncombusted fuel mass) M_iNC[fuel] = sum(M_ij * C_ij / 100)

    Expected input:
    - M_ij: dict with keys as (fuel, engine) and values as fuel mass
    - C_ij: dict with keys as (fuel, engine) and values as % slippage (uncombusted fraction)

    Expected output:
    - Result: dict of M_iNC for each fuel type
    '''
    def EU_eq_4(self, request):
        
        data = request.data
        required = ["M_ij", "C_ij"]
        resp = check_missing_keys(data, required)
        if resp: return resp
        M_ij = data.get("M_ij", {})  # { (i,j): value }
        C_ij = data.get("C_ij", {})  

        result = {}
        for (fuel, engine), m_val in M_ij.items():
            slip = C_ij.get((fuel, engine), 0)
            result[fuel] = result.get(fuel, 0) + (m_val * slip / 100)

        return JsonResponse({"Result": result})

    '''
    CH4_s = (M_iNC)
    Expected input:
    - M_iNC: dict of non-combusted fuel quantities (tons)

    Expected output:
    - Result: total CH4 slippage (tons)
    '''
    def EU_eq_5(self, request):
        data = request.data
        required = ["M_iNC"]
        resp = check_missing_keys(data, required)
        if resp: return resp
        M_iNC = data.get("M_iNC", {})
        return JsonResponse({"Result": M_iNC})

    
    '''
    Total GHG_MRV = CO2 + CH4 * GWP_CH4 + N2O * GWP_N2O
    
    Expected input:
    - CO2_MRV: CO2 emissions (kg)
    - CH4_MRV: CH4 emissions (kg)
    - N2O_MRV: N2O emissions (kg)
    - GWP_CH4: global warming potential of CH4 (default = 28)
    - GWP_N2O: global warming potential of N2O (default = 265)

    Expected output:
    - Result: GHG emissions in CO2-equivalent (kg)
    '''
    def EU_eq_6(self, request):
        data = request.data
        required = ["CO2", "CH4", "N2O", "GWP_CH4", "GWP_N2O"]
        resp = check_missing_keys(data, required)
        if resp: return resp
        CO2 = data.get("CO2", 0)
        CH4 = data.get("CH4", 0)
        N2O = data.get("N2O", 0)
        GWP_CH4 = data.get("GWP_CH4", 28)
        GWP_N2O = data.get("GWP_N2O", 265)

        GHG = CO2 + CH4 * GWP_CH4 + N2O * GWP_N2O
        return JsonResponse({"Result": round(GHG, 4)})

# ------------------------------ RAILROAD ------------------------------
class CalculateEuropeanRailwaysCO2Emissions(APIView):
    def post(self, request):
        method = request.data.get("method")
        if not method:
            return JsonResponse({"error": "Method parameter required (e.g., 'EU_eq_1')"}, status=400)
        try:
            return getattr(self, method)(request)
        except AttributeError:
            return JsonResponse({"error": f"Method {method} not found"}, status=400)
    permission_classes = [AllowAny]
    """
    Calculate CO2 emissions for Europe for Railroad based on various parameters.
    """

    """
    Fuel base methodology:
    Ei = Sum(FC_m * EF_i_m)
    Expcected input:
    FC : diactionarry of fuel consumption for each fuel type m for the period and area considered
    EF_i : emission factor of pollutant i for each unit of fuel type m used
    m_set: set of fuel types
    Expected output:
    E_i: emissions of pollutant i for the period concerned in the inventory (kg or g)
    """
    def EU_eq_1(self, request):
        data = request.data
        required = ["FC", "EF_i", "m_set"]
        resp = check_missing_keys(data, required)
        if resp: return resp
        FC = data["FC"]
        EF_i = data["EF_i"]
        m_set = data["m_set"]
        result = sum(FC[m] * EF_i[m] for m in m_set)
        return JsonResponse({"Result": result})

    def EU_eq_2(self, request):
        raise NotImplementedError
    
    """
    Fuel used by types of locomotive methodology:
    Ei = Sum over m and j of (FC_j_m * EF_i_j_m)

    Expected input:
    - FC : dictionary mapping (locomotive_category, fuel_type) to the fuel consumption for the period and area considered (in tonnes)

    - EF_i : dictionary mapping ( locomotive_category, fuel_type) to the emission factor (in kg/tonne)

    - j_set : set of locomotive categories 

    - m_set : set of fuel types

    Expected output:
    - E_i : emissions of pollutant i for the period concerned in the inventory (in kg or g)
    """

    def EU_eq_3(self, request):
        data = request.data
        required = ["FC", "EF_i", "j_set", "m_set"]
        resp = check_missing_keys(data, required)
        if resp: return resp
        FC = data.get("FC")
        EF_i = data.get("EF_i")
        j_set = data.get("j_set")
        m_set = data.get("m_set")

        result = sum(sum(FC[(j, m)] * EF_i[(j, m)]for j in j_set )for m in m_set)
        return JsonResponse({"Result": result})

    """
    Locomotive usage methodology:
    Ei = Sum over m and j of (N_j_m x H_j_m x P_j_m x LF_j_m x EF_i_j_m)

    Expected input:
    - N : dictionary mapping (locomotive_category, fuel_type) to the number of locomotives

    - H : dictionary mapping (locomotive_category, fuel_type) to average operating hours (in hours)

    - P : dictionary mapping (locomotive_category, fuel_type) to average nominal power output (in kW)

    - LF : dictionary mapping (locomotive_category, fuel_type) to load factor (unitless, between 0 and 1)

    - EF_i : dictionary mapping (locomotive_category, fuel_type) to the emission factor for pollutant i (in kg/kWh or g/kWh)

    - j_set : set of locomotive categories

    - m_set : set of fuel types

    Expected output:
    - E_i : emissions of pollutant i for the period concerned in the inventory (in kg or g)
    """
    def EU_eq_4(self, request):
        data = request.data
        required = ["N", "H", "P", "LF", "EF_i", "j_set", "m_set"]
        resp = check_missing_keys(data, required)
        if resp: return resp

        N = data.get("N")
        H = data.get("H")
        P = data.get("P")
        LF = data.get("LF")
        EF_i = data.get("EF_i")
        j_set = data.get("j_set")
        m_set = data.get("m_set")

        result = sum(
            sum(
                N.get((j, m), 0) *
                H.get((j, m), 0) *
                P.get((j, m), 0) *
                LF.get((j, m), 0) *
                EF_i.get((j, m), 0)
                for j in j_set
            )
            for m in m_set
        )

        return JsonResponse({"Result": result})

# ------------------------------ ROAD ------------------------------
class CalculateEuropeanRoadCO2Emissions(APIView):
    def post(self, request):
        method = request.data.get("method")
        if not method:
            return JsonResponse({"error": "Method parameter required (e.g., 'EU_eq')"}, status=400)
        try:
            return getattr(self, method)(request)
        except AttributeError:
            return JsonResponse({"error": f"Method {method} not found"}, status=400)
    permission_classes = [AllowAny]
    """
    Calculate CO2 emissions for Europe for Road based on various parameters.
    """

    """
    EU inputs and formulas
    CO2 Emissions 
    CO2 = FC * EF
    Where: 
    CO2: Carbon emissions (g CO2/km)
    *FC: Fuel consumption(1/100 km)
    EF: Emission factor (g)

    *To calculate fuel consumption
    FC = (Fuel_Total/D_Total) * 100

    Where:
    FC: Fuel consumption (1/100 km)
    Fuel_Total: Total amount of fuel consumed
    D_Total: Total distance traveled (km)

    Expected inputs: 
    EF: Emission Factor
    Fuel_Total: Total amount fuel consumed
    D_Total: Total distance Traveled

    Expected output:
    CO: Carbon emissions
    """

    def Eu_eq_1(self, request):
        data = request.data
        required = ["EF", "Fuel_Total", "D_Total"]
        resp = check_missing_keys(data, required)
        if resp: return resp
        EF = data["EF"]
        Fuel_Total = data["Fuel_Total"]
        D_Total = data["D_Total"]
        FC = (Fuel_Total/D_Total) * 100
        CO = EF * FC
        return JsonResponse({"Result": CO})

# -----------------------------------------------------------------------------------------------------------------
# REGION - ASIA
# -----------------------------------------------------------------------------------------------------------------

# ------------------------------ AVIATION ------------------------------
class CalculateChinaAviationCO2Emissions(APIView):
    def post(self, request):
        method = request.data.get("method")
        if not method:
            return JsonResponse({"error": "Method parameter required (e.g., 'China_eq_1')"}, status=400)
        try:
            return getattr(self, method)(request)
        except AttributeError:
            return JsonResponse({"error": f"Method {method} not found"}, status=400)
    permission_classes = [AllowAny]
    """
    Calculate CO2 emissions for China for Aviation based on various parameters.
    """
    
    """
    China's aviation calculation (from image):
    Emissions = Fuel Consumption × Emission Factor
    """
    def China_eq_1(self, request):
        data = request.data
        required = ["fuel_consumption", "emission_factor"]
        resp = check_missing_keys(data, required)
        if resp: return resp
        fuel_consumption = data.get("fuel_consumption")
        emission_factor = data.get("emission_factor")

        emissions = fuel_consumption * emission_factor
        return JsonResponse({"Result": emissions})
# ------------------------------ MARINE ------------------------------
class CalculateChinaMarineCO2Emissions(APIView):
    def post(self, request):
        method = request.data.get("method")
        if not method:
            return JsonResponse({"error": "Method parameter required (e.g., 'CHINA_eq_1')"}, status=400)
        try:
            return getattr(self, method)(request)
        except AttributeError:
            return JsonResponse({"error": f"Method {method} not found"}, status=400)
    permission_classes = [AllowAny]
    """ 
    Calculate CO2 emissions for China for Marine based on various parameters.
    """
    
    '''
    Equation: Emissions_trip = F * EF

    Expected Input:
    - F: Fuel consumption for a single trip (in liters or MJ)
    - EF: Emission factor for the fuel used (in kg CO₂/liter or kg CO₂/MJ)

    Expected Output:
    - Emissions_trip: CO₂ emissions for a single trip (in kg CO₂)
    ''' 
    def CHINA_eq_1(self, request):      
        data = request.data
        required = ["F", "EF"]
        resp = check_missing_keys(data, required)
        if resp: return resp
        F = data.get("F")  
        EF = data.get("EF")  

        Emissions_trip = F * EF
        return JsonResponse({"Result": round(Emissions_trip, 4)})

    '''
    for multiple trips,
    Equation: Emissions = sum(F * EF)

    Expected Input:
    - F: A dictionary or list of fuel consumptions across multiple trips (in liters or MJ)
    - EF: Corresponding emission factors for each fuel entry (in kg CO₂/liter or kg CO₂/MJ)

    Expected Output:
    - Emissions: Total aggregated CO2 emissions for all trips (in kg CO₂)
    '''
    def CHINA_eq_2(self, request):

        data = request.data
        required = ["F_list", "EF_list"]
        resp = check_missing_keys(data, required)
        if resp: return resp
        F_list = data.get("F_list")  
        EF_list = data.get("EF_list")  
       
        Emissions = sum(f * ef for f, ef in zip(F_list, EF_list))
        return JsonResponse({"Result": round(Emissions, 4)})

# ------------------------------ RAILROAD ------------------------------
class CalculateChinaRailwaysCO2Emissions(APIView):
    def post(self, request):
        method = request.data.get("method")
        if not method:
            return JsonResponse({"error": "Method parameter required (e.g., 'China_eq_1')"}, status=400)
        try:
            return getattr(self, method)(request)
        except AttributeError:
            return JsonResponse({"error": f"Method {method} not found"}, status=400)
    permission_classes = [AllowAny]
    """
    Calculate CO2 emissions for China for Railroad based on various parameters.
    """

    """
    Emissions = Sum over all segments of (N x H x P x LF x EF)

    Expected input:
    - N: dictionary mapping segment identifiers to the number of trains
    - H: dictionary mapping segment identifiers to hours of operation per train
    - P: dictionary mapping segment identifiers to passenger or cargo capacity per train
    - LF: dictionary mapping segment identifiers to load factor (as a decimal, e.g. 0.75 for 75%)
    - EF: dictionary mapping segment identifiers to emission factor (e.g., kg CO₂ per MJ or per unit of fuel)
    - segments: a list or set of all segment identifiers (e.g. region codes or route IDs)

    Expected output:
    - Emissions: total estimated emissions for all segments combined (in kg or g)
    """

    #It wasn't mentionned what does the equation iterate on, left it as segment
    def China_eq_1(self, request):
        data = request.data
        required = ["N", "H", "P", "LF", "EF", "segments"]
        resp = check_missing_keys(data, required)
        if resp: return resp

        N = data.get("N")
        H = data.get("H")
        P = data.get("P")
        LF = data.get("LF")
        EF = data.get("EF")
        segments = data.get("segments")

        result = sum(
            N.get(seg, 0) * H.get(seg, 0) * P.get(seg, 0) * LF.get(seg, 0) * EF.get(seg, 0)
            for seg in segments
        )

        return JsonResponse({"Result": result})
# ------------------------------ ROAD ------------------------------
class CalculateChinaRoadCO2Emissions(APIView):
    def post(self, request):
        method = request.data.get("method")
        if not method:
            return JsonResponse({"error": "Method parameter required (e.g., 'ch_eq_pm')"}, status=400)
        try:
            return getattr(self, method)(request)
        except AttributeError:
            return JsonResponse({"error": f"Method {method} not found"}, status=400)
    permission_classes = [AllowAny]
    """
    Calculate CO2 emissions for China for Road based on various parameters.
    """

    """
    China Equations
    Preservation method
    Emissions = P * F_E * VKT * EF
    Where:
    P: Number of Vehicles
    F_E: Fuel efficiency of the vehicles (e.g., liters of fuel per kilometer)
    VKT: Velocity Kilometers traveled
    EF: Emission factor (e.g. kg CO2 per liter of fuel)

    Expected intputs:
    P: Number of Vehicles
    F_E: Fuel efficiency of the vehicles (e.g., liters of fuel per kilometer)
    VKT: Velocity Kilometers traveled
    EF: Emission factor (e.g. kg CO2 per liter of fuel)

    Expected outputs
    Emissions: Total emissions
    """

    def China_eq_1(self, request):
        data = request.data
        required = ["P", "F_E", "VKT", "EF"]
        resp = check_missing_keys(data, required)
        if resp: return resp

        P = data.get("P")
        F_E = data.get("F_E")
        VKT = data.get("VKT")
        EF = data.get("EF")

        Emissions = P * F_E * VKT * EF

        JsonResponse({"Result": Emissions})

    """
    Cycle conversion method
    Passenger: Emission_CO2 = (PKM * FE_PKM * EF)
    Freight: Emissions_CO2 (TKM * FE_TKM * EF)
    Where:
    PKM: Passenger kilometers (Total distance traveled by passengers)
    TKM: Ton kilometers (Total distance goods are transported)
    FE_PKM: Energy consumption per PKM (e.g., MJ per PKM)
    FE_TKM: Energy consumption per TKM (e.g., MJ per TKM)
    EF: CO2 emission factor (e.g., kg CO2 per MJ)

    Expected inputs:
    PKM: Passenger kilometers (Total distance traveled by passengers)
    TKM: Ton kilometers (Total distance goods are transported)
    FE_PKM: Energy consumption per PKM (e.g., MJ per PKM)
    FE_TKM: Energy consumption per TKM (e.g., MJ per TKM)
    EF: CO2 emission factor (e.g., kg CO2 per MJ)

    Expected output:
    Em_CO: Total emmisions
    """

    def China_eq_1(self, request):
        data = request.data
        required = ["PKM", "FE_PKM", "EF"]
        resp = check_missing_keys(data, required)
        if resp: return resp

        PKM = data.get("PKM")
        FE_PKM = data.get("FE_PKM")
        EF = data.get("EF")

        Em_CO = (PKM * FE_PKM * EF)
        return JsonResponse({"Result": Em_CO})
    """
    Tier 1 Emissions of CH4 and N2O
    Emission of sum of Fuel * EF over A
    Where: 
    Emission: Emssion in kg
    EF: Emission factor (kg/TJ)
    Fuel: Fuel consumed (TJ)
    A: Fuel type (eg, diesel, gasoline, natural gas, LPG)

    Expected inputs:
    EF: Emission factor (kg/TJ)
    Fuel: Fuel consumed (TJ)
    A: Fuel type (eg, diesel, gasoline, natural gas, LPG)

    Expected output:
    Emission: Emission in kg
    """

    def China_eq_3(self, request):
        data = request.data
        required = ["EF", "Fuel", "A_set"]
        resp = check_missing_keys(data, required)
        if resp: return resp
        EF = data.get("EF")
        Fuel = data.get("Fuel")
        A_set = data.get("A_set")

        Emission = sum(EF(A)*Fuel(A) for A in A_set)
        JsonResponse({"Result: "}, Emission)


    """
    Tier 2 Emissions of CH4 and N2O
    Emission of sum of Fuel * EF over A, B, and C

    Where: 
    Emission: Emssion in kg
    EF: Emission factor (kg/TJ)
    Fuel: Fuel consumed (TJ)
    A: Fuel type (eg, diesel, gasoline, natural gas, LPG)
    B: Vehicle Type
    C: Emission control technology (such as uncontrolled, catalytic converter, etc)

    Expected inputs:
    EF: Emission factor (kg/TJ)
    Fuel: Fuel consumed (TJ)
    A: Fuel type (eg, diesel, gasoline, natural gas, LPG)
    B: Vehicle Type
    C: Emission control technology (such as uncontrolled, catalytic converter, etc)

    Expected output:
    Emission: Emission in kg
    """

    def China_eq_4(self, request):
        data = request.data
        required = ["EF", "Fuel", "A_set", "B_set", "C_set"]
        resp = check_missing_keys(data, required)
        if resp: return resp
        EF = data.get("EF")
        Fuel = data.get("Fuel")
        A_set = data.get("A_set")
        B_set = data.get("B_set")
        C_set = data.get("C_set")

        Emission =  sum(sum(sum(EF(A, B, C) * Fuel(A, B, C) for A in A_set) for B in B_set) for C in C_set)
        JsonResponse({"Result: "}, Emission)
        

    """
    Tier 3 Emissions of CH4 and N2O
    Emission of sum of Distance * EF over A, B, C, D + sum of Warm_Up over A, B, C, D
    
    Where: 
    Emission: Emssion in kg
    EF: Emission factor (kg/TJ)
    Distance: Distance traveled during thermally stabilized 
        engine operation phase for a given mobile source activity (km)
    Warm_Up: Emissions during warm_up phase (cold start) (kg)
    A: Fuel type (eg, diesel, gasoline, natural gas, LPG)
    B: Vehicle Type
    C: Emission control technology (such as uncontrolled, catalytic converter, etc)
    D: Operating Conditions

    Expected inputs:
    EF: Emission factor (kg/TJ)
    Distance: Distance traveled during thermally stabilized 
        engine operation phase for a given mobile source activity (km)
    Warm_Up: Emissions during warm_up phase (cold start) (kg)
    A: Fuel type (eg, diesel, gasoline, natural gas, LPG)
    B: Vehicle Type
    C: Emission control technology (such as uncontrolled, catalytic converter, etc)
    D: Operating Conditions

    Expected output:
    Emission: Emission in kg
    """

    def China_eq_5(self, request):
        data = request.data
        required = ["EF", "Distance", "Warm_Up", "A_set", "B_set", "C_set", "D_set"]
        resp = check_missing_keys(data, required)
        if resp: return resp
        EF = data.get("EF")
        Distance = data.get("Distance")
        Warm_Up = data.get("Warm_Up")
        A_set = data.get("A_set")
        B_set = data.get("B_set")
        C_set = data.get("C_set")
        D_set = data.get("D_set")

        Emission = (sum(sum(sum(sum(EF(A, B, C, D) * Distance(A, B, C, D) for A in A_set) for B in B_set) for C in C_set) for D in D_set))
        +(sum(sum(sum(sum(Warm_Up(A, B, C, D) for A in A_set) for B in B_set) for C in C_set) for D in D_set))
        JsonResponse({"Result: "}, Emission)

    """
    Validating Fuel Consumption
    Placeholder
    """

    def China_eq_6(self, request):
        data = request.data
        required = ["V", "D", "Consume", "i_set", "j_set", "t_set"]
        resp = check_missing_keys(data, required)
        if resp: return resp
        V = data.get("V")
        D = data.get("D")
        Consume = data.get("Consume")
        i_set = data.get("i_set")
        j_set = data.get("j_set")
        t_set = data.get("t_set")

        Emission =  sum(sum(sum(V(i, j, t) * D(i, j, t) * Consume(i, j, t) for i in i_set) for j in j_set) for t in t_set)
        JsonResponse({"Result: "}, Emission)

    """
    Tier 1 Emissions Estate
    Emission of sum of Fuel * EF over A
    Where: 
    Emission: Emssion in kg
    EF: Emission factor (kg/TJ)
    Fuel: Fuel consumed (TJ)
    A: Fuel type (eg, diesel, gasoline, natural gas, LPG)

    Expected inputs:
    EF: Emission factor (kg/TJ)
    Fuel: Fuel consumed (TJ)
    A: Fuel type (eg, diesel, gasoline, natural gas, LPG)

    Expected output:
    Emission: Emission in kg
    """

    def China_eq_7(self, request):
        data = request.data
        required = ["EF", "Fuel", "A_set"]
        resp = check_missing_keys(data, required)
        if resp: return resp
        EF = data.get("EF")
        Fuel = data.get("Fuel")
        A_set = data.get("A_set")

        Emission = sum(EF(A)*Fuel(A) for A in A_set)
        JsonResponse({"Result: "}, Emission)

    """
    Tier 2 Emissions Estate
    Emission = sum of Fuel * EF over A and B
    Where: 
    Emission: Emssion in kg
    EF: Emission factor (kg/TJ)
    Fuel: Fuel consumed (TJ)
    A: Fuel type (eg, diesel, gasoline, natural gas, LPG)
    B: Vehicle type

    Expected inputs:
    EF: Emission factor (kg/TJ)
    Fuel: Fuel consumed (TJ)
    A: Fuel type (eg, diesel, gasoline, natural gas, LPG)
    B: Vehicle type

    Expected output:
    Emission: Emission in kg
    """
    
    def China_eq_8(self, request):
        data = request.data
        required = ["EF", "Fuel", "A_set", "B_set"]
        resp = check_missing_keys(data, required)
        if resp: return resp
        EF = data.get("EF")
        Fuel = data.get("Fuel")
        A_set = data.get("A_set")
        B_set = data.get("B_set")

        Emission =  sum(sum(EF(A, B) * Fuel(A, B) for A in A_set) for B in B_set)
        JsonResponse({"Result: "}, Emission)

    """
    Tier 3 Emissions Estate
    Emission = sum of N* H * P * LF * EF over i and j
    Where: 
    Emission: Emssion in kg
    EF: Emission factor (kg/TJ)
    LF: Typical load factor of a vehicle
    N: Source population
    P: Average rated power of vehicle (kW)
    i: Vehicle type
    j: Fuel type (eg, diesel, gasoline, natural gas, LPG)

    Expected inputs:
    EF: Emission factor (kg/TJ)
    LF: Typical load factor of a vehicle
    N: Source population
    P: Average rated power of vehicle (kW)
    i: Vehicle type
    j: Fuel type (eg, diesel, gasoline, natural gas, LPG)
    
    Expected output:
    Emission: Emission in kg
    """

    def China_eq_9(self, request):
        data = request.data
        required = ["N", "H", "P", "EF", "LF", "i_set", "j_set"]
        resp = check_missing_keys(data, required)
        if resp: return resp
        N = data.get("N")
        H = data.get("H")
        P = data.get("P")
        EF = data.get("EF")
        LF = data.get("LF")
        i_set = data.get("i_set")
        j_set = data.get("j_set")

        Emission = sum(sum(EF(i, j) * LF(i, j) * N(i, j) * H(i, j) * P(i, j) for i in i_set) for j in j_set)
        JsonResponse({"Result: "}, Emission)


# -----------------------------------------------------------------------------------------------------------------
# REGION - AFRICA
# -----------------------------------------------------------------------------------------------------------------

# ------------------------------ AVIATION ------------------------------
class CalculateAfricanAviationCO2Emissions(APIView):
    def post(self, request):
        method = request.data.get("method")
        if not method:
            return JsonResponse({"error": "Method parameter required (e.g., 'Africa_eq_1')"}, status=400)
        try:
            return getattr(self, method)(request)
        except AttributeError:
            return JsonResponse({"error": f"Method {method} not found"}, status=400)
    permission_classes = [AllowAny]
    """
    Calculate CO2 emissions for Africa for Aviation based on various parameters.
    """

    """
    Africa Tier 1: Basic fuel-based calculation
    Emissions = Fuel Consumption × Emission Factor
    """
    def Africa_eq_1(self, request):
        data = request.data
        required = ["fuel_consumption", "emission_factor"]
        resp = check_missing_keys(data, required)
        if resp: return resp
        fuel_consumption = data.get("fuel_consumption")
        emission_factor = data.get("emission_factor")

        emissions = fuel_consumption * emission_factor
        return JsonResponse({"Result": emissions})

    """
    Africa Tier 2: Distinguishes LTO and cruise phases
    Returns dictionary with separate values for each phase
    """
    def Africa_eq_2(self, request):
        data = request.data
        required = ["fuel_LTO", "EF_LTO", "fuel_cruise", "EF_cruise"]
        resp = check_missing_keys(data, required)
        if resp: return resp
        fuel_LTO = data.get("fuel_LTO")
        EF_LTO = data.get("EF_LTO")
        fuel_cruise = data.get("fuel_cruise")
        EF_cruise = data.get("EF_cruise")

        emissions = {
            "LTO": fuel_LTO * EF_LTO,
            "cruise": fuel_cruise * EF_cruise,
            "total": (fuel_LTO * EF_LTO) + (fuel_cruise * EF_cruise)
        }
        return JsonResponse({"Result": emissions})

# ------------------------------ MARINE ------------------------------
class CalculateAfricanMarineCO2Emissions(APIView):
    def post(self, request):
        method = request.data.get("method")
        if not method:
            return JsonResponse({"error": "Method parameter required (e.g., 'AFRICA_eq_1')"}, status=400)
        try:
            return getattr(self, method)(request)
        except AttributeError:
            return JsonResponse({"error": f"Method {method} not found"}, status=400)
    permission_classes = [AllowAny]
    """
    Calculate CO2 emissions for Africa for Marine based on various parameters.
    """
    
    
    """
    Equation: Emissions = ∑(Fuel_Consumed_ab * Emission_Factor_ab)

    Expected Input:
    - Fuel_Consumed_ab: Dictionary of fuel consumption values per fuel type 'a' and navigation mode 'b' 
        (e.g., { "diesel": { "ship": 1000, "boat": 500 }, "gasoline": { "ship": 300 } }) in tons or liters
    - Emission_Factor_ab: Dictionary of emission factors per fuel type 'a' and navigation mode 'b' 
        (e.g., { "diesel": { "ship": 3.2, "boat": 2.9 }, "gasoline": { "ship": 2.5 } }) in kg CO₂/unit

    Expected Output:
    - Emissions: Total CO₂ emissions from water-borne transport across all fuel types and modes (in kg CO₂)
    """
    def Africa_eq_1(self, request):

        data = request.data
        required = ["Fuel_Consumed", "Emission_Factor"]
        resp = check_missing_keys(data, required)
        if resp: return resp
        Fuel_Consumed = data.get("Fuel_Consumed")
        Emission_Factor = data.get("Emission_Factor")

        total_emissions = 0.0
        for fuel in Fuel_Consumed:
            for mode in Fuel_Consumed[fuel]:
                quantity = Fuel_Consumed[fuel][mode]
                factor = Emission_Factor.get(fuel, {}).get(mode, 0)
                total_emissions += quantity * factor
        return JsonResponse({"Result": round(total_emissions, 4)})
# ------------------------------ RAILROAD ------------------------------
class CalculateAfricanRailwaysCO2Emissions(APIView):
    def post(self, request):
        method = request.data.get("method")
        if not method:
            return JsonResponse({"error": "Method parameter required (e.g., 'Africa_eq_1')"}, status=400)
        try:
            return getattr(self, method)(request)
        except AttributeError:
            return JsonResponse({"error": f"Method {method} not found"}, status=400)
    permission_classes = [AllowAny]
    """
    Calculate CO2 emissions for Africa for Railroad based on various parameters.
    """
    
    """
    Emissions = Sum over j of (Fuel_j x EF_j)

    Expected input:
    - Fuel: dictionary mapping fuel type j to the amount of fuel consumed (in TJ)
    - EF: dictionary mapping fuel type j to the emission factor (in kg/TJ)
    - j_set: set of all fuel types

    Expected output:
    - Emissions: total estimated emissions for all fuel types combined (in kg)
    """
    def Africa_eq_1(self, request):
        data = request.data
        required = ["Fuel", "EF", "j_set"]
        resp = check_missing_keys(data, required)
        if resp: return resp

        Fuel = data.get("Fuel")
        EF = data.get("EF")
        j_set = data.get("j_set")

        result = sum(
            Fuel.get(j, 0) * EF.get(j, 0)
            for j in j_set
        )

        return JsonResponse({"Result": result})

    """
    Africa Tier 2 Method for CH₄ and N₂O from Locomotives:
    Emissions = Sum over i of (Fuel_i x EF_i)

    Expected input:
    - Fuel: dictionary mapping locomotive type i to fuel consumed (in TJ)
    - EF: dictionary mapping locomotive type i to emission factor (in kg/TJ)
    - i_set: set of locomotive types

    Expected output:
    - Emissions: total estimated emissions for CH₄ or N₂O (in kg)
    """
    def Africa_eq_2(self, request):

        data = request.data
        required = ["Fuel", "EF", "i_set"]
        resp = check_missing_keys(data, required)
        if resp: return resp
        Fuel = data.get("Fuel")
        EF = data.get("EF")
        i_set = data.get("i_set")

        result = sum(
            Fuel.get(i, 0) * EF.get(i, 0)
            for i in i_set
        )

        return JsonResponse({"Result": result})

    """
    Africa Tier 3 Method for CH₄ and N₂O from Locomotives:
    Emissions = Sum over i of (N_i x H_i x P_i x LF_i x EF_i)

    Expected input:
    - N: dictionary mapping locomotive type i to number of locomotives
    - H: dictionary mapping locomotive type i to annual hours of use
    - P: dictionary mapping locomotive type i to rated power (in kW)
    - LF: dictionary mapping locomotive type i to load factor (between 0 and 1)
    - EF: dictionary mapping locomotive type i to emission factor (in kg/kWh)
    - i_set: set of locomotive types

    Expected output:
    - Emissions: total estimated emissions of CH₄ or N₂O (in kg)
    """
    def Africa_eq_3(self, request):
        data = request.data
        required = ["N", "H", "P", "LF", "EF", "i_set"]
        resp = check_missing_keys(data, required)
        if resp: return resp

        N = data.get("N")
        H = data.get("H")
        P = data.get("P")
        LF = data.get("LF")
        EF = data.get("EF")
        i_set = data.get("i_set")

        result = sum(
            N.get(i, 0) * H.get(i, 0) * P.get(i, 0) * LF.get(i, 0) * EF.get(i, 0)
            for i in i_set
        )

        return JsonResponse({"Result": result})

# ------------------------------ ROAD ------------------------------
class CalculateAfricanRoadCO2Emissions(APIView):
    def post(self, request):
        method = request.data.get("method")
        if not method:
            return JsonResponse({"error": "Method parameter required (e.g., 'af_rd_tr')"}, status=400)
        try:
            return getattr(self, method)(request)
        except AttributeError:
            return JsonResponse({"error": f"Method {method} not found"}, status=400)
    permission_classes = [AllowAny]
    """ 
    Calculate CO2 emissions for Africa for Road based on various parameters.
    """
    
    
    """
    Africa Road Transport
    Tier 1: Calculates CO2 emissions by multiplying estimated fuel sold with a default CO2 emission factor.
    Takes into account all the carbon in the fuel including that emitted as CO2, CH4, CO, NMVOC and particulate matter.
    CO2 from Road Transport
    Emission = Sum of a over (Fuel_A * EF_A)
    Where:
    Emission: Emissions of CO2
    Fuel: fuel sold (TJ)
    EF: emission factor (kg/TJ)
    A: type of fuel(e.g., petrol, diesl, natural gas, LPG etc)

    Expected inputs: 
    Fuel: fuel sold (TJ)
    EF: emission factor (kg/TJ)
    A: type of fuel(e.g., petrol, diesl, natural gas, LPG etc)

    Expected outputs:
    Emissions
    """

    def Africa_eq_1(self, request):
        data = request.data
        required = ["Fuel_A", "EF_A", "A_Set"]
        resp = check_missing_keys(data, required)
        if resp: return resp

        Fuel = data.get("Fuel_A")
        EF = data.get("EF_A")
        A_Set = data.get("A_Set")

        Emissions = sum(Fuel.get(A, 0) * EF.get(A, 0) for A in A_Set)
        return JsonResponse({"Result": Emissions})

    """
    Tier 2: Same as tier 1 but country specific carbon contents of the fuel sold in road transportation are used. 
    The emission factor is based on the actual carbon content of fuels consumed (as represented by fuel sold) in the country during the inventory year. 
    the CO2 emission factors may be adjusted to take account of un-oxidised carbon or carbon emitted as a non-CO2 gas
    In order to reduce the uncertainties, efforts should concentrate on the carbon content and on improving the data on fuel sold
    Another major uncertainty component is the use of transport fuel for non-road purposes. 
    Cannot get significantly better results for CO2 than this
    CO2 Emissions from Urea-Based Catalysts:
    Emission = Activity * (12/60) * Purity * (44/12)
    Where:
    Emissions: CO2 emissions from urea-based additive in catalytic converters (Gg CO2)
    Activity: Amount of urea-based additive consumed for use in catalyic converters (Gg)
    Purity: The mass fraction (=percentage divided by 100) of urea in the urea-based additive

    Expected inputs:
    Activity: Amount of urea-based additive consumed for use in catalyic converters (Gg)
    Purity: The mass fraction (=percentage divided by 100) of urea in the urea-based additive

    Expected output:
    Emision: Total emissions output
    """
    
    def Africa_eq_2(self, request):
        data = request.data
        required = ["A", "P"]
        resp = check_missing_keys(data, required)
        if resp: return resp

        A = data.get("A")
        P = data.get("P")

        Emission = A * (12/60) * P * (44/12)
        JsonResponse({"Result: "}, Emission)


# -----------------------------------------------------------------------------------------------------------------
# UNIFORM CALCULATIONS
# -----------------------------------------------------------------------------------------------------------------

# ------------------------------ AVIATION ------------------------------

class CalculateUniformAviationCO2Emissions(APIView):
    def post(self, request):
        method = request.data.get("method")
        if not method:
            return JsonResponse({"error": "Method parameter required (e.g., 'Uni_eq_1')"}, status=400)
        try:
            return getattr(self, method)(request)
        except AttributeError:
            return JsonResponse({"error": f"Method {method} not found"}, status=400)
    permission_classes = [AllowAny]

    def Uni_eq_1(self, request):
        """
        Straightforward Equation for Aviation:
        E = ((R_N-1 - R_N) + U_N) × EF
        Where:
        - E = Emissions [t CO₂]
        - R_N-1 = Fuel remaining at end of previous flight [t]
        - R_N = Fuel remaining at end of current flight [t]
        - U_N = Fuel uplift for the flight [t]
        - EF = Emissions factor [t CO₂/t fuel]
        """
        data = request.data
        required = ["R_N_1", "R_N", "U_N", "EF"]
        resp = check_missing_keys(data, required)
        if resp: return resp
        R_N_1 = data.get("R_N_1")
        R_N = data.get("R_N")
        U_N = data.get("U_N")
        EF = data.get("EF")

        E = ((R_N_1 - R_N) + U_N) * EF
        return JsonResponse({"Result": E})

    def Uni_eq_2(self, request):
        """
        Cargo-based Equation for Aviation:
        ∑(TKM * FE_tkm * EF)
        Where:
        - TKM = Ton-kilometer
        - FE_tkm = Fuel consumption per ton-kilometer
        - EF = Emission factor
        """
        data = request.data
        required = ["TKM", "FE_tkm", "EF"]
        resp = check_missing_keys(data, required)
        if resp: return resp
        TKM = data.get("TKM")
        FE_tkm = data.get("FE_tkm")
        EF = data.get("EF")

        result = sum(tkm * fe * EF for tkm, fe in zip(TKM, FE_tkm))
        return JsonResponse({"Result": result})

# ------------------------------ MARINE ------------------------------
class CalculateUniformMarineCO2Emissions(APIView):
    def post(self, request):
        method = request.data.get("method")
        if not method:
            return JsonResponse({"error": "Method parameter required (e.g., 'Uniform_eq_1')"}, status=400)
        try:
            return getattr(self, method)(request)
        except AttributeError:
            return JsonResponse({"error": f"Method {method} not found"}, status=400)
    permission_classes = [AllowAny]
    '''
    Marine - Uniform Equation 2: CO2 Emissions
        CO2 = sum(M_i - M_i,NC) * EF_CO2,i
        Where:
        - M_i is the total mass of fuel type i consumed (tons)
        - M_i,NC is the non-combusted mass of fuel type i (tons)
        - EF_CO2,i is the CO2 emission factor for fuel type i (kg CO2/ton)

    Expected input: 
        JSON consisting of
        - M_i is a dict of masses of fuel types of format {fuel_type: mass}
        - M_i,NC is a dict of non-combusted masses of fuel types of format {fuel_type: non_combusted_mass}
    Other variables:
        - EF_CO2,i is a dict of constants 
    Expected output:
        - CO2 (kg CO2)
    '''

        
    
    '''
    Uniform Tier 1 CO2 Equation
    CO2 = sum(M_i -M_iNC)*EF_CO2

    Expected input:
    - M_i: total mass of fuel consumption by type (tons)
    - M_iNC: non-combustable mass of fuel (tons)
    - EF_CO2_i: CO2 emission factors for fuel (kg CO2/ton)

    Expected output:
    - Result: total CO2 emissions (kg CO2)
    '''
    def Uniform_eq_1(self, request):
        data = request.data
        required = ["M_i", "M_iNC", "EF_CO2"]
        resp = check_missing_keys(data, required)
        if resp: return resp
        M_i = data.get("M_i", {})
        M_iNC = data.get("M_iNC", {})
        EF_CO2 = data.get("EF_CO2", {})

        # Fallback: calculate M_iNC from slippage
        for fuel in M_i:
            if fuel not in M_iNC:
                M_iNC[fuel] = C_j.get(fuel, 0) * M_i[fuel]

        CO2 = sum((M_i[fuel] - M_iNC.get(fuel, 0)) * EF_CO2.get(fuel, 0) for fuel in M_i)
        return JsonResponse({"Result": round(CO2, 4)})

    '''
    Uniform mexico specific CO2 Calculations
    The equation: E_ip = (Qr_i * EF_rp) + (Qd_i * EF_dp)

    Expected input:
    - Qr_i: residual oil consumed (t)
    - Qd_i: distillate oil consumed (t)
    - EF_rp: emission factor for residual oil (g/t)
    - EF_dp: emission factor for distillate oil (g/t)

    Expected output:
    - Result: CO2 emissions from marine fuel use in Mexico (g)
    '''
    def Uniform_eq_2(self,request):
        data = request.data
        required = ["Qr_i", "Qd_i", "EF_rp", "EF_dp"]
        resp = check_missing_keys(data, required)
        if resp: return resp
        Qr_i = data.get("Qr_i")  
        Qd_i = data.get("Qd_i")  
        EF_rp = data.get("EF_rp")  
        EF_dp = data.get("EF_dp")  

        E_ip = (Qr_i * EF_rp) + (Qd_i * EF_dp)
        return JsonResponse({"Result": round(E_ip, 4)})

    '''
    Uniform Tier 1 CH4 Equation
    The equation: CH4 = sum[(M_i - M_iNC) * EF_CH4_i] + CH4_s

    Expected input:
    - M_i: dict of total fuel consumption (tons)
    - M_iNC: dict of non-combusted fuel (optional)
    - C_j: slippage % if M_iNC is not provided
    - EF_CH4_i:CH4 emission factor for fuel(kg CH4/ton)

    Expected output:
    - Result: total CH4 emissions(Non - combusted CH4) (kg CH4)
    '''
    def Uniform_eq_3(self, request):
        data = request.data
        required = ["M_i", "M_iNC", "C_j", "EF_CH4"]
        resp = check_missing_keys(data, required)
        if resp: return resp
        M_i = data.get("M_i", {})
        M_iNC = data.get("M_iNC", {})
        C_j = data.get("C_j", {})
        EF_CH4 = data.get("EF_CH4", {})

        for fuel in M_i:
            if fuel not in M_iNC:
                M_iNC[fuel] = C_j.get(fuel, 0) * M_i[fuel]

        CH4_combusted = sum((M_i[f] - M_iNC[f]) * EF_CH4.get(f, 0) for f in M_i)
        CH4_slipped = sum(M_iNC[f] for f in M_i)
        CH4_total = CH4_combusted + CH4_slipped

        return JsonResponse({"Result": round(CH4_total, 4), "Units": "kg CH4"})


    '''
    Uniform Tier 1 N2O Equation
    The equation: E_ip = (Qr_i * EF_rp) + (Qd_i * EF_dp)

    Expected input:
    - M_i: dict of total fuel consumption (tons)
    - M_iNC: dict of non-combusted fuel 
    - EF_NO2: emission factor for distillate oil (g/t)

    Expected output:
    - Result: total NO2 emissions (g)

    '''
    def Uniform_eq_4(self, request):
        data = request.data
        required = ["M_i", "M_iNC", "C_j", "EF_N2O"]
        resp = check_missing_keys(data, required)
        if resp: return resp
        M_i = data.get("M_i", {})
        M_iNC = data.get("M_iNC", {})
        C_j = data.get("C_j", {})
        EF_N2O = data.get("EF_N2O", {})

        for fuel in M_i:
            if fuel not in M_iNC:
                M_iNC[fuel] = C_j.get(fuel, 0) * M_i[fuel]

        N2O = sum((M_i[f] - M_iNC[f]) * EF_N2O.get(f, 0) for f in M_i)
        return JsonResponse({"Result": round(N2O, 4), "Units": "kg N2O"})
    

# ------------------------------ RAILROAD ------------------------------

class CalculateUniformRailwaysCO2Emissions(APIView):
    def post(self, request):
        method = request.data.get("method")
        if not method:
            return JsonResponse({"error": "Method parameter required (e.g., 'Uni_eq_1')"}, status=400)
        try:
            return getattr(self, method)(request)
        except AttributeError:
            return JsonResponse({"error": f"Method {method} not found"}, status=400)
    permission_classes = [AllowAny]
    
    #UNIFORM CALCULATIONS
    """The equation:
    E_i =  Sum through m and j of : N(j, m) * H(j, m) * P(j, m) * LF(j, m) * EF(i, j, m)
    Where:
    -Ei = emissions of pollutant i for the period concerned in the inventory (kg or g)
    -N(j, m) = the number of locomotives in category j using fuel type m 
    -H(j,m) = the average number of hours that locomotives of category j, operate in the time period concerned, using fuel type m (h) 
    -P(j , m) = the average nominal power output of locomotives in category j with fuel m (kW) 
    -LF(j,m) = the load factors for all combinations of locomotive categories and fuel types
    -EF(i,j,m) = emission factor of pollutant i for each unit of power output by locomotives in category j, using fuel type m (kg/kWh or g/kWh) 
    -j = locomotive category (line-haul, shunting, railcar), 
    -m = fuel type (gas oil, diesel).

    Expected input:
    - N : a dictionarry maping pairs j,m to a number n : {(locomotive_category, fuel_type) : number of locomotives}
    - H : a dictionary mapping (locomotive_category, fuel_type) to average operating hours

    - P : a dictionary mapping (locomotive_category, fuel_type) to nominal power output (in kW)

    - LF : a dictionary mapping (locomotive_category, fuel_type) to load factor (unitless)

    - EF : a dictionary mapping (pollutant, locomotive_category, fuel_type) to emission factor 
        (in kg/kWh or g/kWh)

    - i : the pollutant identifier (e.g., 'CO2', 'NOx') for which emissions are being calculated

    - j_set : a set of all locomotive categories to consider (e.g., {'line-haul', 'shunting', 'railcar'})

    - m_set : a set of all fuel types to consider (e.g., {'diesel', 'gas oil'})

    Expcted output:
    E_i : emissions of pollutant i for the period concerned in the inventory (kg or g)
    """
    def Uni_eq_1(self, request):
        data = request.data
        required = ["N", "H", "P", "LF", "EF", "i_set","j_set", "m_set"]
        resp = check_missing_keys(data, required)
        if resp: return resp

        N = data.get('N')
        H = data.get('H')
        P = data.get('P')
        LF = data.get('LF')
        EF = data.get('EF')
        i = data.get('i_set')
        j = data.get("j_set")
        m = data.get("m_set")

        result = sum(sum(N[(j, m)] *  H[(j, m)] * P[(j, m)] * LF[(j, m)] * EF[(i, j, m)] for j in j_set) for m in m_set)
        return JsonResponse({"Result": result})

    """The equation: EL_p_i = F_c_n * (TL_i/TL_n)) * EF_l_p
    Expected input:
    - F_cn : National railroad fuel consumption (in liters)
    - TL_i : Track length for the specific inventory area i (in kilometers)
    - TL_n : Total national railroad track length (in kilometers)
    - EF_lp : Emission factor for pollutant p (in kg/liter)
    - p : Pollutant identifier (e.g., 'CO2', 'CH4', 'NOx')
    Expected output:
    - EL_pi : Estimated annual emissions (in kg) for pollutant p in inventory area i for long-haul railroad operations
    """
    def Uni_eq_2(self, request):
        data = request.data
        required = ["F_cn", "TL_i", "TL_n", "EF_lp", "i"]
        resp = check_missing_keys(data, required)
        if resp: return resp

        F = data.get("F_cn")
        TL_i = data.get("TL_i")
        TL_n = data.get("TL_n")
        EF_lp = data.get("EF_lp")
        i = data.get("i")

        p = data.get("p")
        result = F * (TL_i / TL_n) * EF_lp

        return JsonResponse({"Result": result})

# ------------------------------ ROAD ------------------------------

class CalculateUniformRoadCO2Emissions(APIView):
    def post(self, request):
        method = request.data.get("method")
        if not method:
            return JsonResponse({"error": "Method parameter required (e.g., 'Uni_eq_d')"}, status=400)
        try:
            return getattr(self, method)(request)
        except AttributeError:
            return JsonResponse({"error": f"Method {method} not found"}, status=400)
    permission_classes = [AllowAny]

    """
    Distance-based CO_2 Emissions Formula
    Emissions_CO2 = ((F_Total/D_Total) * EF)
    Where
    F_Total: Total fuel consumed (mass or volume)
    D_Total: Total distance traveled (km or miles)
    EF: CO2 emission factor (e.g., kg CO2 per unit Fuel)

    Expected inputs:
    F_Total: Total fuel consumed (mass or volume)
    D_Total: Total distance traveled (km or miles)
    EF: CO2 emission factor (e.g., kg CO2 per unit Fuel)

    Expected output:
    Em_CO: Total emissions based on distance
    """
    def Uniform_eq_1(self, request):
        data = request.data
        required = ["F_Total", "D_Total", "EF"]
        resp = check_missing_keys(data, required)
        if resp: return resp

        F_Total = data.get("F_Total")
        D_Total = data.get("D_Total")
        EF = data.get("EF")

        Em_CO = ((F_Total/D_Total) * EF)

        return JsonResponse({"Result:": Em_CO})
    
    """
    Passenger and Freight-based CO2 Emissions Formula
    Passenger: Emission_CO2 = (PKM * FE_PKM * EF)
    Freight: Emissions_CO2 (TKM * FE_TKM * EF)
    Where:
    PKM: Passenger kilometers (Total distance traveled by passengers)
    TKM: Ton kilometers (Total distance goods are transported)
    FE_PKM: Energy consumption per PKM (e.g., MJ per PKM)
    FE_TKM: Energy consumption per TKM (e.g., MJ per TKM)
    EF: CO2 emission factor (e.g., kg CO2 per MJ)

    Expected inputs:
    PKM: Passenger kilometers (Total distance traveled by passengers)
    TKM: Ton kilometers (Total distance goods are transported)
    FE_PKM: Energy consumption per PKM (e.g., MJ per PKM)
    FE_TKM: Energy consumption per TKM (e.g., MJ per TKM)
    EF: CO2 emission factor (e.g., kg CO2 per MJ)

    Expected output:
    Em_CO: Total emmisions
    """

    def Uniform_eq_2(self, request):
        data = request.data
        required = ["PKM", "FE_PKM", "EF"]
        resp = check_missing_keys(data, required)
        if resp: return resp

        PKM = data.get("PKM")
        FE_PKM = data.get("FE_PKM")
        EF = data.get("EF")

        Em_CO = (PKM * FE_PKM * EF)
        return JsonResponse({"Result": Em_CO})

    def Uniform_eq_3(self, request):
        data = request.data
        required = ["TKM", "FE_TKM", "EF"]
        resp = check_missing_keys(data, required)
        if resp: return resp

        TKM = data.get("TKM")
        FE_TKM = data.get("FE_TKM")
        EF = data.get("EF")

        Em_CO = (TKM * FE_TKM * EF)
        return JsonResponse({"Result": Em_CO})

    """
    Energy-Based CO2 Emissions Formula
    Emissions_CO2 = F * HHV * EF
    Where:
    Fuel: Mass or volume of fuel combusted
    HHV: Higher heating value of fuel (e.g., MJ per liter)
    EF: CO2 emission factor per unit energy (e.g. kg CO2 per MJ)

    Expected Inputs:
    Fuel: Mass or volume of fuel combusted
    HHV: Higher heating value of fuel (e.g., MJ per liter)
    EF: CO2 emission factor per unit energy (e.g. kg CO2 per MJ)

    Expected Output:
    Em_CO: Total emissions
    """

    def Uniform_eq_4(self, request):
        data = request.data
        required = ["Fuel", "HHV", "EF"]
        resp = check_missing_keys(data, required)
        if resp: return resp

        Fuel = data.get("Fuel")
        HHV = data.get("HHV")
        EF = data.get("EF")

        Em_CO = Fuel * HHV * EF
        return JsonResponse({"Result": Em_CO})


    """
    Carbon Content-Based CO2 Emissions Formula
    Emissions_CO2 = Fuel * CC * (44/12)
    Where:
    CC: Carbon Content of Fuel (mass of carbon per mass or volume of fuel)
    44/12: Ratio of molecular weights of CO2 to carbon

    Expected inputs:
    Fuel: Mass or volume of fuel
    CC: Carbon Content of Fuel (mass of carbon per mass or volume of fuel)
    """

    def Uniform_eq_5(self, request):
        data = request.data
        required = ["Fuel", "CC"]
        resp = check_missing_keys(data, required)
        if resp: return resp

        Fuel = data.get("Fuel")
        CC = data.get("CC")

        Em_CO = (Fuel * CC * (44/12))
        return JsonResponse({"Result": Em_CO})
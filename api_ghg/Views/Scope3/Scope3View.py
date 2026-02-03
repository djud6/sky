from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from django.http import JsonResponse

def check_missing_keys(data, required_keys):
    missing = [key for key in required_keys if key not in data]
    if missing:
        return JsonResponse({"error": f"Missing required fields: {', '.join(missing)}"}, status=400)
    return None


# -----------------------------------------------------------------------------------------------------------------
# Supplier-Specific Method
# -----------------------------------------------------------------------------------------------------------------
"""
Scope 3 - Supplier-specific method
Formula:
Emissions = Σ(Quantity Purchased × Supplier-Specific Emission Factor)

Example input:
{
  "method": "S3_PG_Supplier_eq_1",
  "purchased_items": [
    {"quantity": 100, "emission_factor": 2.5},
    {"quantity": 50, "emission_factor": 3.2}
  ]
}
"""
class CalculateSupplierSpecificScope3Emissions(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        method = request.data.get("method")
        if not method:
            return JsonResponse({"error": "Method parameter required (e.g., 'S3_PG_Supplier_eq_1')"}, status=400)
        try:
            return getattr(self, method)(request)
        except AttributeError:
            return JsonResponse({"error": f"Method {method} not found"}, status=400)

    def S3_PG_Supplier_eq_1(self, request):
        data = request.data
        required = ["purchased_items"]
        resp = check_missing_keys(data, required)
        if resp: return resp

        purchased_items = data["purchased_items"]
        total_emissions = sum(item.get("quantity", 0) * item.get("emission_factor", 0)
                              for item in purchased_items)

        return JsonResponse({
            "Result": round(total_emissions, 4),
            "Units": "kg CO2e",
            "method": "supplier_specific"
        })

    def S3_UF_Supplier_eq_1(self, request):
        """Upstream Fuels - Supplier Specific"""
        data = request.data
        required = ["fuel_consumption", "upstream_emissions_factor"]
        resp = check_missing_keys(data, required)
        if resp: return resp

        emissions = data["fuel_consumption"] * data["upstream_emissions_factor"]
        return JsonResponse({
            "Result": round(emissions, 4),
            "Units": "kg CO2e",
            "method": "supplier_specific_upstream_fuels"
        })

    def S3_TD_Supplier_eq_1(self, request):
        """Transmission & Distribution Losses - Supplier Specific"""
        data = request.data
        required = ["electricity_consumed", "td_loss_rate", "grid_ef"]
        resp = check_missing_keys(data, required)
        if resp: return resp

        loss_emissions = data["electricity_consumed"] * (data["td_loss_rate"] / 100) * data["grid_ef"]
        return JsonResponse({
            "Result": round(loss_emissions, 4),
            "Units": "kg CO2e",
            "method": "supplier_specific_td_losses"
        })

    def S3_UE_Supplier_eq_1(self, request):
        """Upstream Electricity - Supplier Specific"""
        data = request.data
        required = ["electricity_consumed", "upstream_ef"]
        resp = check_missing_keys(data, required)
        if resp: return resp

        emissions = data["electricity_consumed"] * data["upstream_ef"]
        return JsonResponse({
            "Result": round(emissions, 4),
            "Units": "kg CO2e",
            "method": "supplier_specific_upstream_electricity"
        })


# -----------------------------------------------------------------------------------------------------------------
# Hybrid Method
# -----------------------------------------------------------------------------------------------------------------
"""
Scope 3 - Hybrid method
Formula:
Emissions = (Supplier Scope 1 & 2 Data) + (Activity-Based Emissions) + (Secondary Data Estimations)

Example input:
{
  "method": "S3_PG_Hybrid_eq_1",
  "supplier_emissions": 100,
  "activity_emissions": 250.5,
  "secondary_emissions": 80
}
"""
class CalculateHybridScope3Emissions(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        method = request.data.get("method")
        if not method:
            return JsonResponse({"error": "Method parameter required (e.g., 'S3_PG_Hybrid_eq_1')"}, status=400)
        try:
            return getattr(self, method)(request)
        except AttributeError:
            return JsonResponse({"error": f"Method {method} not found"}, status=400)

    def S3_PG_Hybrid_eq_1(self, request):
        data = request.data
        required = ["supplier_emissions", "activity_emissions", "secondary_emissions"]
        resp = check_missing_keys(data, required)
        if resp: return resp

        supplier_emissions = data.get("supplier_emissions", 0)
        activity_emissions = data.get("activity_emissions", 0)
        secondary_emissions = data.get("secondary_emissions", 0)

        total_emissions = supplier_emissions + activity_emissions + secondary_emissions

        return JsonResponse({
            "Result": round(total_emissions, 4),
            "Units": "kg CO2e",
            "method": "hybrid",
            "breakdown": {
                "supplier_emissions": supplier_emissions,
                "activity_emissions": activity_emissions,
                "secondary_emissions": secondary_emissions
            }
        })


# -----------------------------------------------------------------------------------------------------------------
# Average-Data Method
# -----------------------------------------------------------------------------------------------------------------
"""
Scope 3 - Average-data method
Formula:
Emissions = Σ(Quantity Purchased × Average Emission Factor)

Example input:
{
  "method": "S3_PG_Average_eq_1",
  "purchased_items": [
    {"quantity": 200, "average_factor": 1.6},
    {"quantity": 120, "average_factor": 2.3}
  ]
}
"""
class CalculateAverageDataScope3Emissions(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        method = request.data.get("method")
        if not method:
            return JsonResponse({"error": "Method parameter required (e.g., 'S3_PG_Average_eq_1')"}, status=400)
        try:
            return getattr(self, method)(request)
        except AttributeError:
            return JsonResponse({"error": f"Method {method} not found"}, status=400)

    def S3_PG_Average_eq_1(self, request):
        data = request.data
        required = ["purchased_items"]
        resp = check_missing_keys(data, required)
        if resp: return resp

        purchased_items = data["purchased_items"]
        total_emissions = sum(item.get("quantity", 0) * item.get("average_factor", 0)
                              for item in purchased_items)

        return JsonResponse({
            "Result": round(total_emissions, 4),
            "Units": "kg CO2e",
            "method": "average_data"
        })

    def S3_UF_Average_eq_1(self, request):
        """Upstream Fuels - Average Data"""
        data = request.data
        required = ["fuel_consumption", "average_upstream_factor"]
        resp = check_missing_keys(data, required)
        if resp: return resp

        emissions = data["fuel_consumption"] * data["average_upstream_factor"]
        return JsonResponse({
            "Result": round(emissions, 4),
            "Units": "kg CO2e",
            "method": "average_data_upstream_fuels"
        })

    def S3_TD_Average_eq_1(self, request):
        """Transmission & Distribution Losses - Average Data"""
        data = request.data
        required = ["electricity_consumed", "avg_td_loss_rate", "grid_ef"]
        resp = check_missing_keys(data, required)
        if resp: return resp

        loss_emissions = data["electricity_consumed"] * (data["avg_td_loss_rate"] / 100) * data["grid_ef"]
        return JsonResponse({
            "Result": round(loss_emissions, 4),
            "Units": "kg CO2e",
            "method": "average_data_td_losses"
        })

    def S3_UE_Average_eq_1(self, request):
        """Upstream Electricity - Average Data"""
        data = request.data
        required = ["electricity_consumed", "average_upstream_ef"]
        resp = check_missing_keys(data, required)
        if resp: return resp

        emissions = data["electricity_consumed"] * data["average_upstream_ef"]
        return JsonResponse({
            "Result": round(emissions, 4),
            "Units": "kg CO2e",
            "method": "average_data_upstream_electricity"
        })


# -----------------------------------------------------------------------------------------------------------------
# Spend-Based Method
# -----------------------------------------------------------------------------------------------------------------
"""
Scope 3 - Spend-based method
Formula:
Emissions = Σ(Amount Spent × Industry Emission Factor)

Example input:
{
  "method": "S3_PG_Spend_eq_1",
  "spend_items": [
    {"amount_spent": 10000, "industry_factor": 0.12},
    {"amount_spent": 5000, "industry_factor": 0.15}
  ]
}
"""
class CalculateSpendBasedScope3Emissions(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        method = request.data.get("method")
        if not method:
            return JsonResponse({"error": "Method parameter required (e.g., 'S3_PG_Spend_eq_1')"}, status=400)
        try:
            return getattr(self, method)(request)
        except AttributeError:
            return JsonResponse({"error": f"Method {method} not found"}, status=400)

    def S3_PG_Spend_eq_1(self, request):
        data = request.data
        required = ["spend_items"]
        resp = check_missing_keys(data, required)
        if resp: return resp

        spend_items = data["spend_items"]
        total_emissions = sum(item.get("amount_spent", 0) * item.get("industry_factor", 0)
                              for item in spend_items)

        return JsonResponse({
            "Result": round(total_emissions, 4),
            "Units": "kg CO2e",
            "method": "spend_based"
        })
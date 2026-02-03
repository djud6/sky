from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django.http import JsonResponse
import importlib
import logging

logger = logging.getLogger(__name__)

class GHGCalculateRouter(APIView):
    """
    Unified endpoint for performing GHG calculations.
    This router accepts:
        - scope
        - region
        - category
        - tier_id (the method)
        - inputs (dict)
    and then dispatches the request to the correct calculation class.
    """
    permission_classes = [AllowAny]

    def post(self, request):
        # Extract fields
        scope = request.data.get("scope")
        region = request.data.get("region")
        category = request.data.get("category")
        tier_id = request.data.get("tier_id")
        inputs = request.data.get("inputs", {})

        # Check for missing fields
        missing = [field for field in ["scope", "region", "category", "tier_id"] if not request.data.get(field)]
        if missing:
            return JsonResponse({"error": f"Missing required fields: {', '.join(missing)}"}, status=400)

        # Build the expected class name based on your actual class names
        class_name = self.build_class_name(scope, region, category)
        
        # Build module path based on your actual file structure
        module_path = self.build_module_path(scope, region, category)

        # Attempt to load the class dynamically
        try:
            module = importlib.import_module(module_path)
            view_class = getattr(module, class_name)
        except Exception as e:
            logger.error(f"Could not load class {class_name} from {module_path}: {e}")
            return JsonResponse({"error": f"Calculation class not found: {class_name}"}, status=404)

        # Inject tier_id and inputs into the request so the view can read them
        request.data["method"] = tier_id
        request.data.update(inputs)

        # Call the calculation class
        try:
            result = view_class().post(request)
            return result
        except Exception as e:
            logger.error(f"Error during calculation for {class_name}: {e}")
            return JsonResponse({"error": "Internal calculation error"}, status=500)

    def build_class_name(self, scope, region, category):
        """
        Convert user inputs into your ACTUAL calculation class names.
        """
        # Scope 1 classes
        if scope == "Scope1":
            region_map = {
                "NA": "NorthAmerican",
                "EU": "European", 
                "CH": "China",
                "AF": "African",
                "Uniform": "Uniform"
            }
            
            category_map = {
                "Aviation": "Aviation",
                "Marine": "Marine", 
                "Railway": "Railways",
                "Road": "Road"
            }
            
            region_prefix = region_map.get(region, region)
            category_suffix = category_map.get(category, category)
            return f"Calculate{region_prefix}{category_suffix}CO2Emissions"

        # Scope 2 classes
        elif scope == "Scope2":
            if region == "ES":
                return "CalculateEnergySource"
            elif region == "Uniform":
                return "CalculateUniformedScope2Equations"
            else:
                region_map = {
                    "NA": "NAScope2",
                    "EU": "EUScope2", 
                    "Asia": "AsiaScope2"
                }
                return f"Calculate{region_map.get(region, region)}Emissions"

        # Scope 3 classes  
        elif scope == "Scope3":
            category_map = {
                "SupplierSpecific": "SupplierSpecificScope3",
                "Hybrid": "HybridScope3",
                "AverageData": "AverageDataScope3", 
                "SpendBased": "SpendBasedScope3"
            }
            return f"Calculate{category_map.get(category, category)}Emissions"

        # Scope 4 classes
        elif scope == "Scope4":
            category_map = {
                "GreenHydrogen": "GreenHydrogenReplacingFossilFuels",
                "WorkFromHome": "WorkFromHomeAvoidedEmissions",
                "CO2Capture": "CO2CaptureAndSequestration"
            }
            return f"Calculate{category_map.get(category, category)}"

        return f"Calculate{region}{category}CO2Emissions"  # fallback

    def build_module_path(self, scope, region, category):
        """
        Build the correct module path for your file structure.
        """
        if scope == "Scope1":
            return "api_ghg.Views.Scope1.Scope1View"  # ← FIXED
        elif scope == "Scope2":
            return "api_ghg.Views.Scope2.Scope2View"   # ← FIXED
        elif scope == "Scope3":
            return "api_ghg.Views.Scope3.Scope3View"   # ← FIXED
        elif scope == "Scope4":
            return "api_ghg.Views.Scope4.Scope4View"   # ← FIXED
        
        return f"api_ghg.Views.{scope}.{scope}View"    # ← FIXED
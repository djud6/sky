from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from django.http import JsonResponse
import logging

# Ensure this import path is correct based on where you place ghg_inputs_data.py
from .ghg_inputs_data import GHG_INPUT_DEFINITIONS 

logger = logging.getLogger(__name__)

class GetGHGInputs(APIView):
    """
    API endpoint to retrieve input fields using Smart Tier Fallback Logic.
    It identifies the Highest Tier (index 0) as the default and the next tier 
    (index 1) as the explicit fallback option, while sending the full list 
    in 'calculation_tiers' for multi-level degradation.
    """
    permission_classes = [AllowAny] 

    def get(self, request):
        """
        Handles the GET request to retrieve input definitions based on: 
        ?scope=<Scope>&region=<Region>&category=<Category>
        """
        # 1. Extract and standardize parameters
        scope = request.query_params.get("scope")
        region = request.query_params.get("region") 
        category = request.query_params.get("category")
        
        # 2. Parameter Validation
        if not scope or not region or not category:
            missing_params = [p for p, val in [("scope", scope), ("region", region), ("category", category)] if not val]
            logger.warning(f"Input retrieval failed: Missing parameters: {', '.join(missing_params)}")
            return JsonResponse({"error": f"Missing required query parameters: {', '.join(missing_params)}"}, status=status.HTTP_400_BAD_REQUEST)

        # 3. Data Lookup (Retrieve the ORDERED list of all available tiers)
        try:
            # all_tiers is an ordered list (Highest Accuracy at index 0)
            all_tiers = GHG_INPUT_DEFINITIONS[scope][region][category]
            
        except KeyError:
            logger.error(f"Config not found for: {scope}/{region}/{category}")
            return JsonResponse(
                {"error": f"Configuration not found for: {scope}, {region}, {category}"}, 
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            logger.error(f"An unexpected error occurred during input retrieval: {e}")
            return JsonResponse({"error": "An internal server error occurred during data retrieval."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        # 4. Implement Smart Tier Fallback Logic

        # Identify the Highest Tier (Default)
        default_tier = all_tiers[0]

        # Determine if a fallback exists (list length > 1)
        fallback_available = len(all_tiers) > 1
        
        fallback_tier = None
        if fallback_available:
            # Identify the next Lower Tier (index 1)
            fallback_tier = all_tiers[1]

        # 5. Structure the Final Response Payload (Adhering to the specific contract)
        response_payload = {
            "scope": scope,
            "region": region, # Using 'continent' key as requested in the example payload
            "category": category,
            "fallback_available": fallback_available,
            
            # Highest Tier (Default) Inputs - Frontend displays this initially
            "default_tier_id": default_tier["tier_id"],
            "default_tier_inputs": default_tier["inputs"],
            
            # Next Lower Tier (Conditional Fallback) Inputs - Frontend stores this for the first swap
            "fallback_tier_id": fallback_tier["tier_id"] if fallback_tier else None,
            "fallback_tier_inputs": fallback_tier["inputs"] if fallback_tier else None,

            # Full List of Tiers - Enables multi-level degradation (3rd tier, 4th tier, etc.)
            "calculation_tiers": all_tiers 
        }

        # 6. Success Response
        return JsonResponse(response_payload, status=status.HTTP_200_OK)

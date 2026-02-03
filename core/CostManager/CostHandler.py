import math

from api.Models.Cost.delivery_cost import DeliveryCost
from core.AssetRequestManager.AssetRequestHelper import AssetRequestHelper
from core.HistoryManager.DeliveryCostHistory import DeliveryCostHistory
from core.AssetManager.AssetUpdater import AssetUpdater
from rest_framework.response import Response
from rest_framework import status
from django.conf import settings
from django.db import transaction
from core.RepairManager.RepairHelper import RepairHelper
from .CostHelper import DeliveryHelper, FuelHelper, LicenseHelper, RentalHelper, LaborHelper, InsuranceHelper, \
    PartsHelper, AcquisitionHelper, UnitChoicesHelper, InvoiceHelper, FuelCardHelper
from .CostUpdater import GeneralCostUpdater, DeliveryUpdater, FuelUpdater, LicenseUpdater, RentalUpdater, LaborUpdater, \
    InsuranceUpdater, PartsUpdater, AcquisitionUpdater, FuelCardUpdater
from api.Models.Cost.fuel_cost import FuelCost
from api.Models.Cost.license_cost import LicenseCost
from api.Models.Cost.rental_cost import RentalCost
from api.Models.Cost.labor_cost import LaborCost
from api.Models.Cost.insurance_cost import InsuranceCost
from api.Models.Cost.acquisition_cost import AcquisitionCost
from api.Models.Cost.parts import Parts
from api.Models.Cost.fuel_cost_check import FuelCostCheck

from api.Serializers.serializers import DeliveryCostSerializer, LightDeliveryCostSerializer, FuelSerializer, \
    FuelCostSerializer, LicenseSerializer, LicenseCostSerializer, LightRentalCostSerializer, RentalCostSerializer, \
    LightLaborCostSerializer, LaborCostSerializer, LightInsuranceCostSerializer, InsuranceCostSerializer, \
    PartCostSerializer, LightPartCostSerializer, AcquisitionCostSerializer, AcquisitionSerializer, FuelTypeSerializer, \
    CurrencyTypeSerializer, FuelCardSerializer, FuelCostCheckSerializer

from ..FileManager.FileHelper import FileHelper
from ..AssetManager.AssetHelper import AssetHelper
from ..AccidentManager.AccidentHelper import AccidentHelper
from ..MaintenanceManager.MaintenanceHelper import MaintenanceHelper
from ..IssueManager.IssueHelper import IssueHelper
from ..DisposalManager.DisposalHelper import DisposalHelper
from ..HistoryManager.PartsHistory import PartsHistory
from ..HistoryManager.LaborCostHistory import LaborHistory
from ..HistoryManager.FuelCostHistory import FuelCostHistory
from ..HistoryManager.InsuranceCostHistory import InsuranceCostHistory
from ..HistoryManager.LicenseCostHistory import LicenseCostHistory
from ..HistoryManager.RentalCostHistory import RentalCostHistory
from ..HistoryManager.AcquisitionCostHistory import AcquisitionCostHistory
from ..HistoryManager.AssetHistory import AssetHistory
from ..CostManager.CostHelper import CurrencyConversionHelper
from GSE_Backend.errors.ErrorDictionary import CustomError
from azure.ai.formrecognizer import FormRecognizerClient
from azure.core.credentials import AzureKeyCredential

import logging

from ..UserManager.UserHelper import UserHelper

import traceback
from core.FileManager.PdfManager import PdfManager
from communication.EmailService.EmailService import Email
from ..NotificationManager.NotificationHelper import NotificationHelper


class Logger():
    @staticmethod
    def getLogger():
        return logging.getLogger(__name__)


# ------------------------------------------------------------------------------------------------------------------------------------------------------

class FuelHandler():

    @staticmethod
    def handle_get_all_fuel_orders(user):
        try:
            fuel_orders = FuelHelper.select_related_to_fuel(FuelHelper.get_fuel_orders(user.db_access))
            ser = FuelSerializer(fuel_orders, many=True)
            return Response(ser.data, status=status.HTTP_200_OK)
        except Exception as e:
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.G_0, e))
            return Response(CustomError.get_full_error_json(CustomError.G_0, e), status=status.HTTP_400_BAD_REQUEST)

    # ---------------------------------------------------------------------------------------------------------------------
    
    @staticmethod
    def sanity_check_with_id(user,id):
        return FuelCostCheck.objects.using(user.db_access).filter(fuel_cost_check_id=id).get()
    
    @staticmethod
    def sanity_checks_with_company(user,company_id):
        return FuelCostCheck.objects.using(user.db_access).filter(company=company_id)
    
    @staticmethod
    def sanity_checks_with_type(user,company_id,type):
        return FuelHandler.sanity_checks_with_company(user,company_id).filter(type=type)

    @staticmethod
    def sanity_check_with_type(user,company_id,type):
        checks=FuelHandler.sanity_checks_with_type(user,company_id,type)
        if len(checks)==0:
            return None
        return checks[0]

    @staticmethod
    def sanity_check_enabled(user,company_id,type):
        return FuelHandler.sanity_check_with_type(user,company_id,type)!=None

    @staticmethod
    def sanity_check_matching_exists(user,company_id,check):
        key=FuelCostCheck.get_unique_per_company_key(check)
        for other in FuelHandler.sanity_checks_with_type(user,company_id,check.type):
            if FuelCostCheck.get_unique_per_company_key(other)==key:
                return True
        return False

    @staticmethod
    def handle_sanity_check_add(user,data):
        try:
            company_id=UserHelper.get_detailed_user_obj(user.email,user.db_access).company.company_id
            data["company"]=company_id
          
            serializer=FuelCostCheckSerializer(data=data)
            if not serializer.is_valid():
                print("deserialize error")
                return Response(CustomError.I_0,status.HTTP_400_BAD_REQUEST)
            
            # https://stackoverflow.com/a/42700833
            fake_object=FuelCostCheck(**serializer.validated_data)
            
            if FuelHandler.sanity_check_matching_exists(user,company_id,fake_object):
                print("duplicate error")
                return Response(CustomError.I_0,status.HTTP_400_BAD_REQUEST)
            
            serializer.save()
            
            return Response({},status=status.HTTP_200_OK)
        except Exception as error:
            traceback.print_exc()
            return Response(CustomError.get_full_error_json(CustomError.G_0,error),status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @staticmethod
    def handle_sanity_check_delete(user,data):
        try:
            id=data.get("fuel_cost_check_id")
            if id==None:
                return Response(CustomError.I_0,status.HTTP_400_BAD_REQUEST)
            
            existing=FuelHandler.sanity_check_with_id(user,id)
            existing.delete()
            
            return Response({},status=status.HTTP_200_OK)
        except Exception as error:
            traceback.print_exc()
            return Response(CustomError.get_full_error_json(CustomError.G_0,error),status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @staticmethod
    def handle_sanity_check_get_all(user):
        try:
            company_id=UserHelper.get_detailed_user_obj(user.email,user.db_access).company.company_id
            checks=FuelHandler.sanity_checks_with_company(user,company_id)
            serializer=FuelCostCheckSerializer(checks,many=True)
            return Response(serializer.data,status=status.HTTP_200_OK)
        except Exception as error:
            traceback.print_exc()
            return Response(CustomError.get_full_error_json(CustomError.G_0,error),status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @staticmethod
    def handle_sanity_check_get_all_types():
        try:
            types=FuelCostCheck.get_all_types()
            return Response(types,status=status.HTTP_200_OK)
        except Exception as error:
            traceback.print_exc()
            return Response(CustomError.get_full_error_json(CustomError.G_0,error),status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @staticmethod
    def sanity_check_warn(user,asset,fuel_cost,header,message):
      
        print("fuel anomaly: %s -- %s"%(header,message))
    
        html=PdfManager.gen_suspicious_fuel_html(user,asset,fuel_cost,header,message)
        # open("/Users/amy/Desktop/test.html","w").write(html)
        
        notification_config,response=NotificationHelper.get_notification_config_by_name("Unusual Fuel Cost",user.db_access)
        if response.status_code!=status.HTTP_302_FOUND:
            print("notification config missing from db")
            return
        
        title="Fuel Cost Monitoring - Auto-Generated Email"
        
        # TODO: partially copied from AssetRequestHandler.handle_update_asset_request(...)
        # all notifications stuff should really be centralized in one place?
        
        if notification_config.recipient_type=="auto":
            recipients=UserHelper.get_managers_emails_by_location(user.db_access,[asset.current_location.location_id])
        else:
            recipients=NotificationHelper.get_recipients_for_notification(notification_config,user.db_access)
        
        email_response=Email.send_email_notification(recipients,title,html,[],html_content=True)
        if email_response.status_code!=status.HTTP_200_OK:
            print("email send error")
            return
    
    @staticmethod
    def sanity_check_fuel_cost(user,fuel_cost):
      
        asset=fuel_cost.VIN
        detailed_user=UserHelper.get_detailed_user_obj(user.email,user.db_access)
        company_id=detailed_user.company.company_id
        
        header_prereq="More information is required to properly monitor fuel transactions on this asset."
        header_sus="An unusual fuel transaction was detected."
        
        if FuelHandler.sanity_check_enabled(user,company_id,FuelCostCheck.TYPE):
            if asset.fuel==None:
                FuelHandler.sanity_check_warn(user,asset,fuel_cost,header_prereq,"Fuel type is missing for asset \"%s\"."%(asset.VIN))
                return False
            elif fuel_cost.fuel_type==None:
                FuelHandler.sanity_check_warn(user,asset,fuel_cost,header_sus,"Fuel type is missing in cost record.")
                return False
            elif asset.fuel.name!=fuel_cost.fuel_type.name:
                FuelHandler.sanity_check_warn(user,asset,fuel_cost,header_sus,"Fuel type \"%s\" in cost record mismatches type \"%s\" set for asset \"%s\"."%(fuel_cost.fuel_type.name,asset.fuel.name,asset.VIN))
                return False
        
        should_check_units=False
        volume_ratio_check=FuelHandler.sanity_check_with_type(user,company_id,FuelCostCheck.VOLUME_RATIO)
        if volume_ratio_check!=None:
            should_check_units=True
        elif FuelHandler.sanity_check_enabled(user,company_id,FuelCostCheck.VOLUME_UNITS):
            should_check_units=True
        
        if should_check_units:
            if asset.fuel_tank_capacity_unit==None:
                FuelHandler.sanity_check_warn(user,asset,fuel_cost,header_prereq,"Fuel volume unit is missing for asset \"%s\"."%(asset.VIN))
                return False
            elif fuel_cost.volume_unit==None:
                FuelHandler.sanity_check_warn(user,asset,fuel_cost,header_sus,"Fuel volume unit is missing in cost record.")
                return False
            elif asset.fuel_tank_capacity_unit!=fuel_cost.volume_unit:
              
                # TODO: attempt to convert units?
                # if so, do the same for cost ratio.
                
                FuelHandler.sanity_check_warn(user,asset,fuel_cost,header_sus,"Fuel volume unit \"%s\" in cost record mismatches volume unit \"%s\" set for asset \"%s\"."%(fuel_cost.volume_unit,asset.fuel_tank_capacity_unit,asset.VIN))
                return False

        if volume_ratio_check!=None:
            if asset.fuel_tank_capacity==None or asset.fuel_tank_capacity<=0:
                FuelHandler.sanity_check_warn(user,asset,fuel_cost,header_prereq,"Fuel tank capacity is missing or invalid for asset \"%s\"."%(asset.VIN))
                return False

            if fuel_cost.volume>volume_ratio_check.volume_ratio_threshold*asset.fuel_tank_capacity:
                FuelHandler.sanity_check_warn(user,asset,fuel_cost,header_sus,"Fuel volume \"%d %s(s)\" in cost record exceeds set threshold of \"%d%%\" of fuel tank capacity for asset \"%s\"."%(fuel_cost.volume,fuel_cost.volume_unit,int(volume_ratio_check.volume_ratio_threshold*100),asset.VIN))
                return False

        cost_ratio_check=None
        for check in FuelHandler.sanity_checks_with_type(user,company_id,FuelCostCheck.COST_RATIO):
            if check.cost_ratio_type.name==asset.fuel.name:
                if check.cost_ratio_units==fuel_cost.volume_unit:
                    cost_ratio_check=check
                    break
        
        if cost_ratio_check:
            cost_per_unit=fuel_cost.total_cost/fuel_cost.volume
            if cost_per_unit>cost_ratio_check.cost_ratio_threshold:
                FuelHandler.sanity_check_warn(user,asset,fuel_cost,header_sus,"Fuel record cost of \"%.02f %s(s) / %s\" exceeds set threshold of \"%.02f %s(s) / %s\" for fuel type \"%s\"."%(cost_per_unit,fuel_cost.currency.name,cost_ratio_check.cost_ratio_units,cost_ratio_check.cost_ratio_threshold,fuel_cost.currency.name,cost_ratio_check.cost_ratio_units,cost_ratio_check.cost_ratio_type.name))
                return False
        
        # TODO: are there other types of validation needed?
        
        return True
    
    @staticmethod
    def sanity_check_fuel_cost_updating_flag(user,object):
        check_passed=FuelHandler.sanity_check_fuel_cost(user,object)
        
        if not check_passed and not object.flagged:
            print("sanity check failed; setting flag")
            object.flagged=True
            object.save()

    @staticmethod
    def handle_add_fuel_cost(request_data, user):
        try:
            db_name = user.db_access
            request_data = CurrencyConversionHelper.convert_currency_request_data(request_data, ['total_cost', 'taxes'], db_name)

            if request_data == None:
                return Response(CustomError.get_full_error_json(CustomError.CDNE_0), status=status.HTTP_400_BAD_REQUEST)

            ser = FuelCostSerializer(data=request_data)

            if (ser.is_valid()):
                fuelcost_obj = ser.save()
                db_name = user.db_access

                # set created_by and modified_by
                fuelcost_obj, created_by_status = FuelUpdater.update_fuel_cost_created_by(fuelcost_obj, user)
                if created_by_status.status_code != status.HTTP_202_ACCEPTED:
                    return created_by_status

                # set location based on VIN location
                fuelcost_obj = GeneralCostUpdater.set_cost_obj_location_by_VIN(fuelcost_obj, request_data.get("VIN"), user)
                fuelcost_obj = ser.save()

                # create fuel cost record
                if not FuelCostHistory.create_fuel_cost_record_by_obj(fuelcost_obj, True):
                    Logger.getLogger().error(CustomError.get_error_dev(CustomError.MHF_13))
                    return Response(CustomError.get_full_error_json(CustomError.MHF_13), status=status.HTTP_400_BAD_REQUEST)

                # update asset total_cost
                asset_obj = AssetHelper.get_asset_by_VIN(request_data.get("VIN"), db_name)
                asset_obj, update_cost_response = AssetUpdater.update_asset_total_cost(float(request_data.get("total_cost")), asset_obj)
                if update_cost_response.status_code != status.HTTP_202_ACCEPTED:
                    return update_cost_response
                asset_obj.save()

                # create asset record
                if (not AssetHistory.create_asset_record_by_obj(asset_obj)):
                    Logger.getLogger().error(CustomError.get_error_dev(CustomError.MHF_0))
                    return Response(CustomError.get_full_error_json(CustomError.MHF_0), status=status.HTTP_400_BAD_REQUEST)
                
                FuelHandler.sanity_check_fuel_cost_updating_flag(user,fuelcost_obj)

                return Response(status=status.HTTP_201_CREATED)
            else:
                Logger.getLogger().error(CustomError.get_error_dev(CustomError.S_0, ser.errors))
                return Response(CustomError.get_full_error_json(CustomError.S_0, ser.errors), status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.G_0, e))
            return Response(CustomError.get_full_error_json(CustomError.G_0, e), status=status.HTTP_400_BAD_REQUEST)

    # ---------------------------------------------------------------------------------------------------------------------

    """
        Input: 
        request_data:
        {
            "id": int,   # fuel_cost_id
            "volume": double,
            "total_cost": double, 
            "taxes": double, 
        }
        Based on how fuel cost data is displayed on the frontend and created on the backend, the user should only be 
        able to edit numeric values. If other fields (foreign keys) need to be updated, use delete then add a new entry.
    """
    @staticmethod
    @transaction.atomic
    def handle_update_fuel_cost(request_data, user):
        try:
            with transaction.atomic():
                fuel_cost_id = request_data.pop("id")
                db_name = user.db_access
                cost_entry = FuelHelper.get_fuel_cost_by_id(fuel_cost_id, db_name)
                if cost_entry.exists() is False:
                    raise Exception(CustomError.get_error_user(CustomError.FCDNE_0))
                cost_entry = cost_entry.first()
                previous_total_cost = cost_entry.total_cost
                # if the cost entry is already 'deleted', ignore this delete request
                if cost_entry.volume == 0.0 and cost_entry.total_cost == 0.0:
                    raise Exception(CustomError.get_error_user(CustomError.FCDNE_0))

                has_update = False
                for key in request_data:
                    if hasattr(cost_entry, key):
                        if (isinstance(getattr(cost_entry, key), float) and
                                not math.isclose(float(getattr(cost_entry, key)), float(request_data.get(key)))):
                            setattr(cost_entry, key, request_data.get(key))
                            has_update = True
                detailed_user = UserHelper.get_detailed_user_obj(user.email, user.db_access)
                if cost_entry.modified_by != detailed_user:
                    has_update = True
                    cost_entry.modified_by = detailed_user
                
                new_flag=request_data.get("flagged")
                skip_sanity_check=False
                if new_flag!=None:
                    print("overriding flag state to %d and skipping sanity check this time"%(new_flag))
                    cost_entry.flagged=new_flag
                    has_update=True
                    skip_sanity_check=True
                
                if not has_update:
                    raise Exception("Update asset total_cost failed. No data update found.")

                cost_entry.save()
                if not FuelCostHistory.create_fuel_cost_record_by_obj(cost_entry, False):
                    raise Exception(CustomError.get_error_user(CustomError.MHF_13))
                # update asset total_cost
                entry_total_cost = float(cost_entry.total_cost) - float(previous_total_cost)
                asset_obj = AssetHelper.get_asset_by_VIN(cost_entry.VIN, db_name)
                asset_obj, update_cost_response = AssetUpdater.update_asset_total_cost(entry_total_cost, asset_obj)
                if update_cost_response.status_code != status.HTTP_202_ACCEPTED:
                    raise Exception("Update asset total_cost failed. Total cost update failed.")
                asset_obj.save()
                # Create asset record
                if not AssetHistory.create_asset_record_by_obj(asset_obj):
                    raise Exception(CustomError.get_error_user(CustomError.MHF_0))
                
                if not skip_sanity_check:
                    FuelHandler.sanity_check_fuel_cost_updating_flag(user,cost_entry)

                return Response(status=status.HTTP_202_ACCEPTED)
        except Exception as e:
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.G_0, e))
            return Response(CustomError.get_full_error_json(CustomError.G_0, e), status=status.HTTP_400_BAD_REQUEST)

    # ---------------------------------------------------------------------------------------------------------------------

    @staticmethod
    def handle_update_fuel_flagged(request_data, user):
        try:
            db_name = user.db_access

            cost_entry = FuelHelper.get_fuel_cost_by_id(request_data.get('id'), db_name)
            if cost_entry.exists() is False:
                raise Exception(CustomError.get_error_user(CustomError.FCDNE_0))

            cost_entry = cost_entry.first()

            new_flag = request_data.get("flagged")
            if new_flag is not None:
                cost_entry.flagged = new_flag
                cost_entry.save()
                return Response(status=status.HTTP_202_ACCEPTED)
            else:
                error_message = "Missing flagged value."
                raise Exception(CustomError.get_error_dev(CustomError.G_0, error_message))
        except Exception as e:
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.G_0, e))
            return Response(CustomError.get_full_error_json(CustomError.G_0, e), status=status.HTTP_400_BAD_REQUEST)

    # ---------------------------------------------------------------------------------------------------------------------

    """
    Input: 
        request_data:
        {
            "id": int   # fuel_cost_id
        }
    Update [volume, total_cost, taxes] of a fuel_cost entry to 0. Do not delete the entry.
    Append a new transaction to fuel_model_history with the same fuel_cost_id
    """
    @staticmethod
    @transaction.atomic
    def handle_delete_fuel_cost(request_data, user):
        try:
            with transaction.atomic():
                db_name = user.db_access
                cost_entry = FuelCost.objects.using(db_name).get(id=request_data.get("id"))
                if cost_entry is None:
                    raise Exception(CustomError.get_error_user(CustomError.FCDNE_0))
                # if the cost entry is already 'deleted', ignore this delete request
                if cost_entry.volume == 0.0 and cost_entry.total_cost == 0.0:
                    raise Exception(CustomError.get_error_user(CustomError.FCDNE_0))
                entry_total_cost = 0 - float(cost_entry.total_cost)
                # update values to 0 and add to fuel transaction history; DO NOT DELETE FUEL COST ENTRY
                detailed_user = UserHelper.get_detailed_user_obj(user.email, user.db_access)
                cost_entry.modified_by = detailed_user
                cost_entry.total_cost = 0.0
                cost_entry.volume = 0.0
                cost_entry.taxes = 0.0
                cost_entry.save()
                if not FuelCostHistory.create_fuel_cost_record_by_obj(cost_entry, False):
                    raise Exception(CustomError.get_error_user(CustomError.MHF_13))
                # update asset total_cost
                asset_obj = AssetHelper.get_asset_by_VIN(cost_entry.VIN, db_name)
                asset_obj, update_cost_response = AssetUpdater.update_asset_total_cost(entry_total_cost, asset_obj)
                if update_cost_response.status_code != status.HTTP_202_ACCEPTED:
                    raise Exception("Update asset total_cost failed.")
                asset_obj.save()
                # Create asset record
                if not AssetHistory.create_asset_record_by_obj(asset_obj):
                    raise Exception(CustomError.get_error_user(CustomError.MHF_0))

                return Response(status=status.HTTP_200_OK)
        except Exception as e:
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.G_0, e))
            return Response(CustomError.get_full_error_json(CustomError.G_0, e), status=status.HTTP_400_BAD_REQUEST)

    # ---------------------------------------------------------------------------------------------------------------------

    @staticmethod
    def handle_get_fuel_cost_by_vin(vin, user):
        try:
            if not AssetHelper.asset_exists(vin, user.db_access):
                Logger.getLogger().error(CustomError.VDNE_0)
                return Response(CustomError.get_full_error_json(CustomError.VDNE_0), status=status.HTTP_400_BAD_REQUEST)
            fuel_cost = FuelHelper.select_related_to_fuel(FuelHelper.get_fuel_cost_by_vin(vin, user.db_access))
            ser = FuelSerializer(fuel_cost, many=True)
            return Response(ser.data, status=status.HTTP_200_OK)
        except Exception as e:
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.G_0, e))
            return Response(CustomError.get_full_error_json(CustomError.G_0, e), status=status.HTTP_400_BAD_REQUEST)


# ------------------------------------------------------------------------------------------------------------------------------------------------------

class LicenseHandler():

    @staticmethod
    def handle_add_license_cost(request_data, user):
        try:
            db_name = user.db_access
            request_data = CurrencyConversionHelper.convert_currency_request_data(
                request_data,
                ['license_registration', 'taxes', 'license_plate_renewal', "total_cost"],
                db_name)

            if request_data == None:
                return Response(CustomError.get_full_error_json(CustomError.CDNE_0), status=status.HTTP_400_BAD_REQUEST)

            ser = LicenseCostSerializer(data=request_data)

            if (ser.is_valid()):
                licensecost_obj = ser.save()

                # set created_by and modified_by
                licensecost_obj, created_by_status = LicenseUpdater.update_license_cost_created_by(licensecost_obj,
                                                                                                   user)
                if created_by_status.status_code != status.HTTP_202_ACCEPTED:
                    return created_by_status

                # set location based on VIN location
                licensecost_obj = GeneralCostUpdater.set_cost_obj_location_by_VIN(licensecost_obj,
                                                                                  request_data.get("VIN"), user)
                licensecost_obj = ser.save()

                # create license cost record
                if (not LicenseCostHistory.create_license_cost_record_by_obj(licensecost_obj)):
                    Logger.getLogger().error(CustomError.get_error_dev(CustomError.MHF_15))
                    return Response(CustomError.get_full_error_json(CustomError.MHF_15),
                                    status=status.HTTP_400_BAD_REQUEST)

                    # update asset total_cost
                asset_obj = AssetHelper.get_asset_by_VIN(request_data.get("VIN"), db_name)

                if not AssetHelper.check_asset_status_active(asset_obj.VIN, db_name):
                    Logger.getLogger().error(CustomError.get_error_dev(CustomError.TUF_16,
                                                                       CustomError.get_error_user(CustomError.TUF_16)))
                    return Response(CustomError.get_full_error_json(CustomError.TUF_16,
                                                                    CustomError.get_error_user(CustomError.TUF_16)),
                                    status=status.HTTP_400_BAD_REQUEST)

                asset_obj, update_cost_response = AssetUpdater.update_asset_total_cost(
                    float(request_data.get("total_cost")), asset_obj)
                if update_cost_response.status_code != status.HTTP_202_ACCEPTED:
                    return update_cost_response
                asset_obj.save()

                # Create asset record
                if (not AssetHistory.create_asset_record_by_obj(asset_obj)):
                    Logger.getLogger().error(CustomError.get_error_dev(CustomError.MHF_0))
                    return Response(CustomError.get_full_error_json(CustomError.MHF_0),
                                    status=status.HTTP_400_BAD_REQUEST)

                return Response(status=status.HTTP_201_CREATED)
            else:
                Logger.getLogger().error(CustomError.get_error_dev(CustomError.S_0, ser.errors))
                return Response(CustomError.get_full_error_json(CustomError.S_0, ser.errors),
                                status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.G_0, e))
            return Response(CustomError.get_full_error_json(CustomError.G_0, e), status=status.HTTP_400_BAD_REQUEST)

    # ---------------------------------------------------------------------------------------------------------------------

    @staticmethod
    def handle_delete_license_cost(request_data, user):
        try:
            db_name = user.db_access
            cost_entry = LicenseCost.objects.using(db_name).filter(id=request_data.get("id"))
            cost_entry_values = cost_entry.values()[0]  # We only have one result as id is the PK
            entry_total_cost = 0 - float(cost_entry_values.get("total_cost"))

            # update asset total_cost
            asset_obj = AssetHelper.get_asset_by_VIN(cost_entry_values.get("VIN_id"), db_name)
            if not AssetHelper.check_asset_status_active(asset_obj.VIN, db_name):
                Logger.getLogger().error(CustomError.get_error_dev(CustomError.TUF_16,
                                                                   CustomError.get_error_user(CustomError.TUF_16)))
                return Response(CustomError.get_full_error_json(CustomError.TUF_16,
                                                                CustomError.get_error_user(CustomError.TUF_16)),
                                status=status.HTTP_400_BAD_REQUEST)

            cost_entry.delete()
            asset_obj, update_cost_response = AssetUpdater.update_asset_total_cost(entry_total_cost, asset_obj)
            if update_cost_response.status_code != status.HTTP_202_ACCEPTED:
                return update_cost_response
            asset_obj.save()

            # Create asset record
            if (not AssetHistory.create_asset_record_by_obj(asset_obj)):
                Logger.getLogger().error(CustomError.get_error_dev(CustomError.MHF_0))
                return Response(CustomError.get_full_error_json(CustomError.MHF_0), status=status.HTTP_400_BAD_REQUEST)

            return Response(status=status.HTTP_200_OK)

        except Exception as e:
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.G_0, e))
            return Response(CustomError.get_full_error_json(CustomError.G_0, e), status=status.HTTP_400_BAD_REQUEST)

    # ---------------------------------------------------------------------------------------------------------------------
    @staticmethod
    def handle_get_all_license_cost(user):
        try:
            license_cost = LicenseHelper.select_related_to_license(LicenseHelper.get_license_cost(user.db_access))
            ser = LicenseSerializer(license_cost, many=True)
            return Response(ser.data, status=status.HTTP_200_OK)
        except Exception as e:
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.G_0, e))
            return Response(CustomError.get_full_error_json(CustomError.G_0, e), status=status.HTTP_400_BAD_REQUEST)

    # ---------------------------------------------------------------------------------------------------------------------

    @staticmethod
    def handle_get_license_cost_by_vin(vin, user):
        try:
            if not AssetHelper.asset_exists(vin, user.db_access):
                Logger.getLogger().error(CustomError.VDNE_0)
                return Response(CustomError.get_full_error_json(CustomError.VDNE_0), status=status.HTTP_400_BAD_REQUEST)
            license_cost = LicenseHelper.select_related_to_license(
                LicenseHelper.get_license_cost_by_vin(vin, user.db_access))
            ser = LicenseSerializer(license_cost, many=True)
            return Response(ser.data, status=status.HTTP_200_OK)
        except Exception as e:
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.G_0, e))
            return Response(CustomError.get_full_error_json(CustomError.G_0, e), status=status.HTTP_400_BAD_REQUEST)


# ------------------------------------------------------------------------------------------------------------------------------------------------------

class RentalHandler():

    @staticmethod
    def handle_add_rental_cost(request_data, user):
        try:
            db_name = user.db_access
            request_data = CurrencyConversionHelper.convert_currency_request_data(request_data, ['total_cost'], db_name)

            if request_data == None:
                return Response(CustomError.get_full_error_json(CustomError.CDNE_0), status=status.HTTP_400_BAD_REQUEST)

            ser = RentalCostSerializer(data=request_data)

            if (ser.is_valid()):
                rentalcost_obj = ser.save()

                # set created_by and modified_by
                rentalcost_obj, created_by_status = RentalUpdater.update_rental_cost_created_by(rentalcost_obj, user)
                if created_by_status.status_code != status.HTTP_202_ACCEPTED:
                    return created_by_status

                if not AssetHelper.check_asset_status_active(RentalHelper.get_rental_cost_obj_VIN(rentalcost_obj),
                                                             db_name):
                    Logger.getLogger().error(CustomError.get_error_dev(CustomError.TUF_16,
                                                                       CustomError.get_error_user(CustomError.TUF_16)))
                    return Response(CustomError.get_full_error_json(CustomError.TUF_16,
                                                                    CustomError.get_error_user(CustomError.TUF_16)),
                                    status=status.HTTP_400_BAD_REQUEST)

                # set location based on VIN location
                asset_vin = RentalHelper.get_rental_cost_obj_VIN(rentalcost_obj)
                rentalcost_obj = GeneralCostUpdater.set_cost_obj_location_by_VIN(rentalcost_obj, asset_vin, user)
                rentalcost_obj.save()

                # create rental cost record
                if (not RentalCostHistory.create_rental_cost_record_by_obj(rentalcost_obj)):
                    Logger.getLogger().error(CustomError.get_error_dev(CustomError.MHF_16))
                    return Response(CustomError.get_full_error_json(CustomError.MHF_16),
                                    status=status.HTTP_400_BAD_REQUEST)

                # update asset total_cost
                asset_obj = AssetHelper.get_asset_by_VIN(asset_vin, db_name)
                asset_obj, update_cost_response = AssetUpdater.update_asset_total_cost(
                    float(request_data.get("total_cost")), asset_obj)
                if update_cost_response.status_code != status.HTTP_202_ACCEPTED:
                    return update_cost_response
                asset_obj.save()

                # Create asset record
                if (not AssetHistory.create_asset_record_by_obj(asset_obj)):
                    Logger.getLogger().error(CustomError.get_error_dev(CustomError.MHF_0))
                    return Response(CustomError.get_full_error_json(CustomError.MHF_0),
                                    status=status.HTTP_400_BAD_REQUEST)

                return Response(status=status.HTTP_201_CREATED)
            else:
                Logger.getLogger().error(CustomError.get_error_dev(CustomError.S_0, ser.errors))
                return Response(CustomError.get_full_error_json(CustomError.S_0, ser.errors),
                                status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.G_0, e))
            return Response(CustomError.get_full_error_json(CustomError.G_0, e), status=status.HTTP_400_BAD_REQUEST)

    # ---------------------------------------------------------------------------------------------------------------------

    @staticmethod
    def handle_delete_rental_cost(request_data, user):
        try:
            db_name = user.db_access
            cost_entry = RentalCost.objects.using(db_name).get(id=request_data.get("id"))
            entry_total_cost = 0 - float(cost_entry.total_cost)

            # update asset total_cost
            asset_obj = AssetHelper.get_asset_by_VIN(RentalHelper.get_rental_cost_obj_VIN(cost_entry), db_name)
            if not AssetHelper.check_asset_status_active(asset_obj.VIN, db_name):
                Logger.getLogger().error(CustomError.get_error_dev(CustomError.TUF_16,
                                                                   CustomError.get_error_user(CustomError.TUF_16)))
                return Response(CustomError.get_full_error_json(CustomError.TUF_16,
                                                                CustomError.get_error_user(CustomError.TUF_16)),
                                status=status.HTTP_400_BAD_REQUEST)

            cost_entry.delete()
            asset_obj, update_cost_response = AssetUpdater.update_asset_total_cost(entry_total_cost, asset_obj)
            if update_cost_response.status_code != status.HTTP_202_ACCEPTED:
                return update_cost_response
            asset_obj.save()

            # Create asset record
            if (not AssetHistory.create_asset_record_by_obj(asset_obj)):
                Logger.getLogger().error(CustomError.get_error_dev(CustomError.MHF_0))
                return Response(CustomError.get_full_error_json(CustomError.MHF_0), status=status.HTTP_400_BAD_REQUEST)

            return Response(status=status.HTTP_200_OK)

        except Exception as e:
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.G_0, e))
            return Response(CustomError.get_full_error_json(CustomError.G_0, e), status=status.HTTP_400_BAD_REQUEST)

    # ---------------------------------------------------------------------------------------------------------------------

    @staticmethod
    def handle_get_all_rental_cost(user):
        try:
            rental_cost = RentalHelper.select_related_to_rental(RentalHelper.get_rental_cost(user.db_access))
            ser = LightRentalCostSerializer(rental_cost, many=True)
            return Response(ser.data, status=status.HTTP_200_OK)
        except Exception as e:
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.G_0, e))
            return Response(CustomError.get_full_error_json(CustomError.G_0, e), status=status.HTTP_400_BAD_REQUEST)

    # ---------------------------------------------------------------------------------------------------------------------

    @staticmethod
    def handle_get_rental_cost_by_vin(_vin, user):
        try:
            if not AssetHelper.asset_exists(_vin, user.db_access):
                Logger.getLogger().error(CustomError.VDNE_0)
                return Response(CustomError.get_full_error_json(CustomError.VDNE_0), status=status.HTTP_400_BAD_REQUEST)
            rental_cost = RentalHelper.select_related_to_rental(
                RentalHelper.get_rental_cost_by_vin(_vin, user.db_access))
            ser = LightRentalCostSerializer(rental_cost, many=True)
            return Response(ser.data, status=status.HTTP_200_OK)
        except Exception as e:
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.G_0, e))
            return Response(CustomError.get_full_error_json(CustomError.G_0, e), status=status.HTTP_400_BAD_REQUEST)

    # ---------------------------------------------------------------------------------------------------------------------

    @staticmethod
    def handle_get_rental_cost_by_accident_id(accident_id, user):
        try:
            if not AccidentHelper.get_accident_exists(accident_id, user.db_access):
                Logger.getLogger().error(CustomError.ADNE_0)
                return Response(CustomError.get_full_error_json(CustomError.ADNE_0), status=status.HTTP_400_BAD_REQUEST)
            rental_cost = RentalHelper.select_related_to_rental(
                RentalHelper.get_rental_cost_by_accident_id(accident_id, user.db_access))
            ser = LightRentalCostSerializer(rental_cost, many=True)
            return Response(ser.data, status=status.HTTP_200_OK)
        except Exception as e:
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.G_0, e))
            return Response(CustomError.get_full_error_json(CustomError.G_0, e), status=status.HTTP_400_BAD_REQUEST)

    # ---------------------------------------------------------------------------------------------------------------------

    @staticmethod
    def handle_get_rental_cost_by_maintenance_id(maintenance_id, user):
        try:
            if not MaintenanceHelper.get_maintenance_exists_by_id(maintenance_id, user.db_access):
                Logger.getLogger().error(CustomError.MRDNE_0)
                return Response(CustomError.get_full_error_json(CustomError.MRDNE_0),
                                status=status.HTTP_400_BAD_REQUEST)
            rental_cost = RentalHelper.select_related_to_rental(
                RentalHelper.get_rental_cost_by_maintenance_id(maintenance_id, user.db_access))
            ser = LightRentalCostSerializer(rental_cost, many=True)
            return Response(ser.data, status=status.HTTP_200_OK)
        except Exception as e:
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.G_0, e))
            return Response(CustomError.get_full_error_json(CustomError.G_0, e), status=status.HTTP_400_BAD_REQUEST)

    # ---------------------------------------------------------------------------------------------------------------------

    @staticmethod
    def handle_get_rental_cost_by_repair_id(repair_id, user):
        try:
            if not RepairHelper.repair_exists_by_id(repair_id, user.db_access):
                Logger.getLogger().error(CustomError.RDNE_0)
                return Response(CustomError.get_full_error_json(CustomError.RDNE_0), status=status.HTTP_400_BAD_REQUEST)
            rental_cost = RentalHelper.select_related_to_rental(
                RentalHelper.get_rental_cost_by_repair_id(repair_id, user.db_access))
            ser = LightRentalCostSerializer(rental_cost, many=True)
            return Response(ser.data, status=status.HTTP_200_OK)
        except Exception as e:
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.G_0, e))
            return Response(CustomError.get_full_error_json(CustomError.G_0, e), status=status.HTTP_400_BAD_REQUEST)


# ------------------------------------------------------------------------------------------------------------------------------------------------------

class LaborHandler():

    @staticmethod
    def handle_add_labor_cost(request_data, user):
        try:
            db_name = user.db_access
            request_data = CurrencyConversionHelper.convert_currency_request_data(
                request_data,
                ['base_hourly_rate', "overtime_rate", "taxes", "total_cost"],
                db_name)

            if request_data == None:
                return Response(CustomError.get_full_error_json(CustomError.CDNE_0), status=status.HTTP_400_BAD_REQUEST)

            ser = LaborCostSerializer(data=request_data)

            if (ser.is_valid()):
                laborcost_obj = ser.save()

                # set created_by and modified_by
                laborcost_obj, created_by_status = LaborUpdater.update_labor_cost_created_by(laborcost_obj, user)
                if created_by_status.status_code != status.HTTP_202_ACCEPTED:
                    return created_by_status

                asset_obj = AssetHelper.get_asset_by_VIN(LaborHelper.get_labor_cost_obj_VIN(laborcost_obj), db_name)
                if not AssetHelper.check_asset_status_active(asset_obj.VIN, db_name):
                    Logger.getLogger().error(CustomError.get_error_dev(CustomError.TUF_16,
                                                                       CustomError.get_error_user(CustomError.TUF_16)))
                    return Response(CustomError.get_full_error_json(CustomError.TUF_16,
                                                                    CustomError.get_error_user(CustomError.TUF_16)),
                                    status=status.HTTP_400_BAD_REQUEST)

                # set location based on VIN location
                laborcost_obj = GeneralCostUpdater.set_cost_obj_location_by_VIN(laborcost_obj,
                                                                                LaborHelper.get_labor_cost_obj_VIN(
                                                                                    laborcost_obj), user)
                laborcost_obj = ser.save()

                # Create labor history record
                if (not LaborHistory.create_labor_cost_record_by_obj(laborcost_obj)):
                    Logger.getLogger().error(CustomError.get_error_dev(CustomError.MHF_11))
                    return Response(CustomError.get_full_error_json(CustomError.MHF_11),
                                    status=status.HTTP_400_BAD_REQUEST)

                # update asset total_cost
                asset_obj = AssetHelper.get_asset_by_VIN(LaborHelper.get_labor_cost_obj_VIN(laborcost_obj), db_name)
                asset_obj, update_cost_response = AssetUpdater.update_asset_total_cost(
                    float(request_data.get("total_cost")), asset_obj)
                if update_cost_response.status_code != status.HTTP_202_ACCEPTED:
                    return update_cost_response
                asset_obj.save()

                # Create asset record
                if (not AssetHistory.create_asset_record_by_obj(asset_obj)):
                    Logger.getLogger().error(CustomError.get_error_dev(CustomError.MHF_0))
                    return Response(CustomError.get_full_error_json(CustomError.MHF_0),
                                    status=status.HTTP_400_BAD_REQUEST)

                return Response(status=status.HTTP_201_CREATED)
            else:
                Logger.getLogger().error(CustomError.get_error_dev(CustomError.S_0, ser.errors))
                return Response(CustomError.get_full_error_json(CustomError.S_0, ser.errors),
                                status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.G_0, e))
            return Response(CustomError.get_full_error_json(CustomError.G_0, e), status=status.HTTP_400_BAD_REQUEST)

    # ---------------------------------------------------------------------------------------------------------------------

    @staticmethod
    def handle_delete_labor_cost(request_data, user):
        try:
            db_name = user.db_access
            cost_entry = LaborCost.objects.using(db_name).filter(id=request_data.get("id"))

            cost_entry_values = cost_entry.values_list("total_cost", "issue__VIN", "maintenance__VIN", "disposal__VIN")[
                0]
            entry_total_cost = 0 - float(cost_entry_values[0])

            # update asset total_cost
            asset_obj = AssetHelper.get_asset_by_VIN(LaborHelper.get_labor_cost_values_list_VIN(cost_entry_values),
                                                     db_name)

            if not AssetHelper.check_asset_status_active(asset_obj.VIN, db_name):
                Logger.getLogger().error(CustomError.get_error_dev(CustomError.TUF_16,
                                                                   CustomError.get_error_user(CustomError.TUF_16)))
                return Response(CustomError.get_full_error_json(CustomError.TUF_16,
                                                                CustomError.get_error_user(CustomError.TUF_16)),
                                status=status.HTTP_400_BAD_REQUEST)

            cost_entry.delete()
            asset_obj, update_cost_response = AssetUpdater.update_asset_total_cost(entry_total_cost, asset_obj)
            if update_cost_response.status_code != status.HTTP_202_ACCEPTED:
                return update_cost_response
            asset_obj.save()

            # # Create asset record
            if (not AssetHistory.create_asset_record_by_obj(asset_obj)):
                Logger.getLogger().error(CustomError.get_error_dev(CustomError.MHF_0))
                return Response(CustomError.get_full_error_json(CustomError.MHF_0), status=status.HTTP_400_BAD_REQUEST)

            return Response(status=status.HTTP_200_OK)

        except Exception as e:
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.G_0, e))
            return Response(CustomError.get_full_error_json(CustomError.G_0, e), status=status.HTTP_400_BAD_REQUEST)

    # ---------------------------------------------------------------------------------------------------------------------

    @staticmethod
    def handle_get_all_labor_cost(user):
        try:
            labor_cost = LaborHelper.select_related_to_labor(LaborHelper.get_labor_cost(user.db_access))
            ser = LightLaborCostSerializer(labor_cost, many=True)
            return Response(ser.data, status=status.HTTP_200_OK)
        except Exception as e:
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.G_0, e))
            return Response(CustomError.get_full_error_json(CustomError.G_0, e), status=status.HTTP_400_BAD_REQUEST)

    # ---------------------------------------------------------------------------------------------------------------------
    @staticmethod
    def handle_get_labor_cost_by_vin(_vin, user):
        try:
            if not AssetHelper.asset_exists(_vin, user.db_access):
                Logger.getLogger().error(CustomError.VDNE_0)
                return Response(CustomError.get_full_error_json(CustomError.VDNE_0), status=status.HTTP_400_BAD_REQUEST)
            labor_costs = LaborHelper.select_related_to_labor(LaborHelper.get_labor_cost_by_vin(_vin, user.db_access))
            ser = LightLaborCostSerializer(labor_costs, many=True)
            return Response(ser.data, status=status.HTTP_200_OK)
        except Exception as e:
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.G_0, e))
            return Response(CustomError.get_full_error_json(CustomError.G_0, e), status=status.HTTP_400_BAD_REQUEST)

    # ---------------------------------------------------------------------------------------------------------------------

    @staticmethod
    def handle_get_labor_cost_by_maintenance_id(maintenance_id, user):
        try:
            if not MaintenanceHelper.get_maintenance_exists_by_id(maintenance_id, user.db_access):
                Logger.getLogger().error(CustomError.MRDNE_0)
                return Response(CustomError.get_full_error_json(CustomError.MRDNE_0),
                                status=status.HTTP_400_BAD_REQUEST)
            labor_cost = LaborHelper.select_related_to_labor(
                LaborHelper.get_labor_cost_by_maintenance_id(maintenance_id, user.db_access))
            ser = LightLaborCostSerializer(labor_cost, many=True)
            return Response(ser.data, status=status.HTTP_200_OK)
        except Exception as e:
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.G_0, e))
            return Response(CustomError.get_full_error_json(CustomError.G_0, e), status=status.HTTP_400_BAD_REQUEST)

    # ---------------------------------------------------------------------------------------------------------------------

    @staticmethod
    def handle_get_labor_cost_by_issue_id(issue_id, user):
        try:
            if not IssueHelper.get_issue_exists(issue_id, user.db_access):
                Logger.getLogger().error(CustomError.IDNE_0)
                return Response(CustomError.get_full_error_json(CustomError.IDNE_0), status=status.HTTP_400_BAD_REQUEST)
            labor_cost = LaborHelper.select_related_to_labor(
                LaborHelper.get_labor_cost_by_issue_id(issue_id, user.db_access))
            ser = LightLaborCostSerializer(labor_cost, many=True)
            return Response(ser.data, status=status.HTTP_200_OK)
        except Exception as e:
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.G_0, e))
            return Response(CustomError.get_full_error_json(CustomError.G_0, e), status=status.HTTP_400_BAD_REQUEST)

    # ---------------------------------------------------------------------------------------------------------------------

    @staticmethod
    def handle_get_labor_cost_by_issue_id_list(request_data, user):
        try:
            issue_id_list = request_data.get("issue_ids")
            for issue_id in issue_id_list:
                if not IssueHelper.get_issue_exists(issue_id, user.db_access):
                    Logger.getLogger().error(CustomError.IDNE_0)
                    return Response(CustomError.get_full_error_json(CustomError.IDNE_0),
                                    status=status.HTTP_400_BAD_REQUEST)

            labor_cost = LaborHelper.select_related_to_labor(
                LaborHelper.get_labor_cost_by_issue_id_list(issue_id_list, user.db_access))
            ser = LightLaborCostSerializer(labor_cost, many=True)
            return Response(ser.data, status=status.HTTP_200_OK)
        except Exception as e:
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.G_0, e))
            return Response(CustomError.get_full_error_json(CustomError.G_0, e), status=status.HTTP_400_BAD_REQUEST)

    # ---------------------------------------------------------------------------------------------------------------------

    @staticmethod
    def handle_get_labor_cost_by_disposal_id(disposal_id, user):
        try:
            if not DisposalHelper.disposal_exists(disposal_id, user.db_access):
                Logger.getLogger().error(CustomError.DDNE_0)
                return Response(CustomError.get_full_error_json(CustomError.DDNE_0), status=status.HTTP_400_BAD_REQUEST)

            labor_cost = LaborHelper.select_related_to_labor(
                LaborHelper.get_labor_cost_by_disposal_id(disposal_id, user.db_access))
            ser = LightLaborCostSerializer(labor_cost, many=True)
            return Response(ser.data, status=status.HTTP_200_OK)
        except Exception as e:
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.G_0, e))
            return Response(CustomError.get_full_error_json(CustomError.G_0, e), status=status.HTTP_400_BAD_REQUEST)

    # ---------------------------------------------------------------------------------------------------------------------

    @staticmethod
    def handle_update_labor_cost(request_data, user):
        try:
            db_name = user.db_access
            labor_obj = LaborHelper.get_labor_obj_by_id(request_data.get('id'), db_name)

            asset_obj = AssetHelper.get_asset_by_VIN(LaborHelper.get_labor_cost_obj_VIN(labor_obj), db_name)
            if not AssetHelper.check_asset_status_active(asset_obj.VIN, db_name):
                Logger.getLogger().error(CustomError.get_error_dev(CustomError.TUF_16,
                                                                   CustomError.get_error_user(CustomError.TUF_16)))
                return Response(CustomError.get_full_error_json(CustomError.TUF_16,
                                                                CustomError.get_error_user(CustomError.TUF_16)),
                                status=status.HTTP_400_BAD_REQUEST)

            old_total_cost = labor_obj.total_cost

            request_data = CurrencyConversionHelper.convert_currency_request_data(
                request_data,
                ['base_hourly_rate', "overtime_rate", "taxes", "total_cost"],
                db_name)

            if request_data == None:
                return Response(CustomError.get_full_error_json(CustomError.CDNE_0), status=status.HTTP_400_BAD_REQUEST)

            # Update parts fields
            updated_labor_obj, update_response = LaborUpdater.update_labor_cost_fields(labor_obj, request_data, db_name)
            if update_response.status_code != status.HTTP_200_OK:
                return update_response

            updated_labor_obj.save()

            # Create parts history record
            if (not LaborHistory.create_labor_cost_record_by_obj(updated_labor_obj)):
                Logger.getLogger().error(CustomError.get_error_dev(CustomError.MHF_11))
                return Response(CustomError.get_full_error_json(CustomError.MHF_11), status=status.HTTP_400_BAD_REQUEST)

            # update asset total_cost
            asset_obj = AssetHelper.get_asset_by_VIN(LaborHelper.get_labor_cost_obj_VIN(updated_labor_obj), db_name)
            asset_obj, update_cost_response = AssetUpdater.update_asset_total_cost(
                float(updated_labor_obj.total_cost) - float(old_total_cost), asset_obj)
            if update_cost_response.status_code != status.HTTP_202_ACCEPTED:
                return update_cost_response
            asset_obj.save()

            # Create asset record
            if (not AssetHistory.create_asset_record_by_obj(asset_obj)):
                Logger.getLogger().error(CustomError.get_error_dev(CustomError.MHF_0))
                return Response(CustomError.get_full_error_json(CustomError.MHF_0), status=status.HTTP_400_BAD_REQUEST)

            serializer = LaborCostSerializer(updated_labor_obj)
            return Response(serializer.data, status=status.HTTP_200_OK)

        except Exception as e:
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.G_0, e))
            return Response(CustomError.get_full_error_json(CustomError.G_0, e), status=status.HTTP_400_BAD_REQUEST)


# ------------------------------------------------------------------------------------------------------------------------------------------------------

class PartsHandler():

    @staticmethod
    def handle_add_parts_cost(request_data, user):
        try:
            db_name = user.db_access
            request_data = CurrencyConversionHelper.convert_currency_request_data(
                request_data,
                ['price', "taxes", "total_cost"],
                db_name)




            if request_data == None:
                return Response(CustomError.get_full_error_json(CustomError.CDNE_0), status=status.HTTP_400_BAD_REQUEST)

            ser = PartCostSerializer(data=request_data)

            if (ser.is_valid()):
                parts_obj = ser.save()

                # set created_by and modified_by
                parts_obj, created_by_status = PartsUpdater.update_parts_created_by(parts_obj, user)
                if created_by_status.status_code != status.HTTP_202_ACCEPTED:
                    return created_by_status

                # set location based on VIN location
                parts_obj = GeneralCostUpdater.set_cost_obj_location_by_VIN(parts_obj,
                                                                            PartsHelper.get_parts_cost_obj_VIN(
                                                                                parts_obj), user)
                parts_obj = ser.save()

                # Create parts history record
                if (not PartsHistory.create_parts_record_by_obj(parts_obj)):
                    Logger.getLogger().error(CustomError.get_error_dev(CustomError.MHF_10))
                    return Response(CustomError.get_full_error_json(CustomError.MHF_10),
                                    status=status.HTTP_400_BAD_REQUEST)

                # update asset total_cost
                asset_obj = AssetHelper.get_asset_by_VIN(PartsHelper.get_parts_cost_obj_VIN(parts_obj), db_name)

                if not AssetHelper.check_asset_status_active(asset_obj.VIN, db_name):
                    Logger.getLogger().error(CustomError.get_error_dev(CustomError.TUF_16,
                                                                       CustomError.get_error_user(CustomError.TUF_16)))
                    return Response(CustomError.get_full_error_json(CustomError.TUF_16,
                                                                    CustomError.get_error_user(CustomError.TUF_16)),
                                    status=status.HTTP_400_BAD_REQUEST)

                asset_obj, update_cost_response = AssetUpdater.update_asset_total_cost(
                    float(request_data.get("total_cost")), asset_obj)
                if update_cost_response.status_code != status.HTTP_202_ACCEPTED:
                    return update_cost_response
                asset_obj.save()

                # Create asset record
                if (not AssetHistory.create_asset_record_by_obj(asset_obj)):
                    Logger.getLogger().error(CustomError.get_error_dev(CustomError.MHF_0))
                    return Response(CustomError.get_full_error_json(CustomError.MHF_0),
                                    status=status.HTTP_400_BAD_REQUEST)

                return Response(status=status.HTTP_201_CREATED)
            else:
                Logger.getLogger().error(CustomError.get_error_dev(CustomError.S_0, ser.errors))
                return Response(CustomError.get_full_error_json(CustomError.S_0, ser.errors),
                                status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.G_0, e))
            return Response(CustomError.get_full_error_json(CustomError.G_0, e), status=status.HTTP_400_BAD_REQUEST)

    # ---------------------------------------------------------------------------------------------------------------------

    @staticmethod
    def handle_delete_part_cost(request_data, user):
        try:
            db_name = user.db_access
            cost_entry = Parts.objects.using(db_name).filter(id=request_data.get("id"))
            cost_entry_values = cost_entry.values_list("total_cost", "issue__VIN", "maintenance__VIN", "disposal__VIN")[
                0]
            asset_obj = AssetHelper.get_asset_by_VIN(PartsHelper.get_parts_cost_values_list_VIN(cost_entry_values),
                                                     db_name)

            if not AssetHelper.check_asset_status_active(asset_obj.VIN, db_name):
                Logger.getLogger().error(CustomError.get_error_dev(CustomError.TUF_16,
                                                                   CustomError.get_error_user(CustomError.TUF_16)))
                return Response(CustomError.get_full_error_json(CustomError.TUF_16,
                                                                CustomError.get_error_user(CustomError.TUF_16)),
                                status=status.HTTP_400_BAD_REQUEST)

            entry_total_cost = 0 - float(cost_entry_values[0])
            cost_entry.delete()

            # update asset total_cost
            asset_obj, update_cost_response = AssetUpdater.update_asset_total_cost(entry_total_cost, asset_obj)
            if update_cost_response.status_code != status.HTTP_202_ACCEPTED:
                return update_cost_response
            asset_obj.save()

            # # Create asset record
            if (not AssetHistory.create_asset_record_by_obj(asset_obj)):
                Logger.getLogger().error(CustomError.get_error_dev(CustomError.MHF_0))
                return Response(CustomError.get_full_error_json(CustomError.MHF_0), status=status.HTTP_400_BAD_REQUEST)

            return Response(status=status.HTTP_200_OK)

        except Exception as e:
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.G_0, e))
            return Response(CustomError.get_full_error_json(CustomError.G_0, e), status=status.HTTP_400_BAD_REQUEST)

    # ---------------------------------------------------------------------------------------------------------------------

    @staticmethod
    def handle_get_all_parts_cost(user):
        try:
            parts_cost = PartsHelper.select_related_to_parts(PartsHelper.get_parts(user.db_access))
            ser = LightPartCostSerializer(parts_cost, many=True)
            return Response(ser.data, status=status.HTTP_200_OK)
        except Exception as e:
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.G_0, e))
            return Response(CustomError.get_full_error_json(CustomError.G_0, e), status=status.HTTP_400_BAD_REQUEST)

    # ---------------------------------------------------------------------------------------------------------------------

    @staticmethod
    def handle_get_parts_by_maintenance(maintenance_id, user):
        try:
            if not MaintenanceHelper.get_maintenance_exists_by_id(maintenance_id, user.db_access):
                Logger.getLogger().error(CustomError.MRDNE_0)
                return Response(CustomError.get_full_error_json(CustomError.MRDNE_0),
                                status=status.HTTP_400_BAD_REQUEST)
            parts = PartsHelper.select_related_to_parts(
                PartsHelper.get_parts_by_maintenance(maintenance_id, user.db_access))
            ser = LightPartCostSerializer(parts, many=True)
            return Response(ser.data, status=status.HTTP_200_OK)
        except Exception as e:
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.G_0, e))
            return Response(CustomError.get_full_error_json(CustomError.G_0, e), status=status.HTTP_400_BAD_REQUEST)

    # ---------------------------------------------------------------------------------------------------------------------

    @staticmethod
    def handle_get_parts_by_issue(asset_issue_id, user):
        try:
            if not IssueHelper.get_issue_exists(asset_issue_id, user.db_access):
                Logger.getLogger().error(CustomError.IDNE_0)
                return Response(CustomError.get_full_error_json(CustomError.IDNE_0), status=status.HTTP_400_BAD_REQUEST)
            parts = PartsHelper.select_related_to_parts(PartsHelper.get_parts_by_issue(asset_issue_id, user.db_access))
            ser = LightPartCostSerializer(parts, many=True)
            return Response(ser.data, status=status.HTTP_200_OK)
        except Exception as e:
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.G_0, e))
            return Response(CustomError.get_full_error_json(CustomError.G_0, e), status=status.HTTP_400_BAD_REQUEST)

    # ---------------------------------------------------------------------------------------------------------------------

    @staticmethod
    def handle_get_parts_by_number(part_number, user):
        try:
            if not PartsHelper.part_number_exists(part_number, user.db_access):
                Logger.getLogger().error(CustomError.PNDNE_0)
                return Response(CustomError.get_full_error_json(CustomError.PNDNE_0),
                                status=status.HTTP_400_BAD_REQUEST)
            parts = PartsHelper.select_related_to_parts(PartsHelper.get_parts_by_number(part_number, user.db_access))
            ser = LightPartCostSerializer(parts, many=True)
            return Response(ser.data, status=status.HTTP_200_OK)
        except Exception as e:
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.G_0, e))
            return Response(CustomError.get_full_error_json(CustomError.G_0, e), status=status.HTTP_400_BAD_REQUEST)

    # ---------------------------------------------------------------------------------------------------------------------

    @staticmethod
    def handle_get_parts_by_vin(_vin, user):
        try:
            if not AssetHelper.asset_exists(_vin, user.db_access):
                Logger.getLogger().error(CustomError.VDNE_0)
                return Response(CustomError.get_full_error_json(CustomError.VDNE_0), status=status.HTTP_400_BAD_REQUEST)
            parts_costs = PartsHelper.select_related_to_parts(PartsHelper.get_parts_by_vin(_vin, user.db_access))
            ser = LightPartCostSerializer(parts_costs, many=True)
            return Response(ser.data, status=status.HTTP_200_OK)
        except Exception as e:
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.G_0, e))
            return Response(CustomError.get_full_error_json(CustomError.G_0, e), status=status.HTTP_400_BAD_REQUEST)

    # ---------------------------------------------------------------------------------------------------------------------

    @staticmethod
    def handle_get_parts_cost_by_issue_id_list(request_data, user):
        try:
            issue_id_list = request_data.get("issue_ids")
            for issue_id in issue_id_list:
                if not IssueHelper.get_issue_exists(issue_id, user.db_access):
                    Logger.getLogger().error(CustomError.IDNE_0)
                    return Response(CustomError.get_full_error_json(CustomError.IDNE_0),
                                    status=status.HTTP_400_BAD_REQUEST)

            parts_cost = PartsHelper.select_related_to_parts(
                PartsHelper.get_parts_by_issue_list(issue_id_list, user.db_access))
            ser = LightPartCostSerializer(parts_cost, many=True)
            return Response(ser.data, status=status.HTTP_200_OK)
        except Exception as e:
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.G_0, e))
            return Response(CustomError.get_full_error_json(CustomError.G_0, e), status=status.HTTP_400_BAD_REQUEST)

    # ---------------------------------------------------------------------------------------------------------------------

    @staticmethod
    def handle_get_parts_cost_by_disposal_id(disposal_id, user):
        try:
            if not DisposalHelper.disposal_exists(disposal_id, user.db_access):
                Logger.getLogger().error(CustomError.DDNE_0)
                return Response(CustomError.get_full_error_json(CustomError.DDNE_0), status=status.HTTP_400_BAD_REQUEST)

            parts_cost = PartsHelper.select_related_to_parts(
                PartsHelper.get_parts_by_disposal(disposal_id, user.db_access))
            ser = LightPartCostSerializer(parts_cost, many=True)
            return Response(ser.data, status=status.HTTP_200_OK)
        except Exception as e:
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.G_0, e))
            return Response(CustomError.get_full_error_json(CustomError.G_0, e), status=status.HTTP_400_BAD_REQUEST)

    # ---------------------------------------------------------------------------------------------------------------------

    @staticmethod
    def handle_update_parts_cost(request_data, user):
        try:
            db_name = user.db_access
            part_obj = PartsHelper.get_parts_obj_by_id(request_data.get('id'), db_name)
            old_total_cost = part_obj.total_cost

            if not AssetHelper.check_asset_status_active(
                    AssetHelper.get_asset_by_VIN(PartsHelper.get_parts_cost_obj_VIN(part_obj), db_name), user.db_access):
                Logger.getLogger().error(CustomError.get_error_dev(CustomError.TUF_16,
                                                                   CustomError.get_error_user(CustomError.TUF_16)))
                return Response(CustomError.get_full_error_json(CustomError.TUF_16,
                                                                CustomError.get_error_user(CustomError.TUF_16)),
                                status=status.HTTP_400_BAD_REQUEST)

            request_data = CurrencyConversionHelper.convert_currency_request_data(
                request_data,
                ['price', "taxes", "total_cost"],
                db_name)

            if request_data == None:
                return Response(CustomError.get_full_error_json(CustomError.CDNE_0), status=status.HTTP_400_BAD_REQUEST)

            # Update parts fields
            updated_parts_obj, update_response = PartsUpdater.update_parts_fields(part_obj, request_data, db_name)
            if update_response.status_code != status.HTTP_200_OK:
                return update_response

            updated_parts_obj.save()

            # Create parts history record
            if (not PartsHistory.create_parts_record_by_obj(updated_parts_obj)):
                Logger.getLogger().error(CustomError.get_error_dev(CustomError.MHF_10))
                return Response(CustomError.get_full_error_json(CustomError.MHF_10), status=status.HTTP_400_BAD_REQUEST)

            # update asset total_cost
            asset_obj = AssetHelper.get_asset_by_VIN(PartsHelper.get_parts_cost_obj_VIN(updated_parts_obj), db_name)
            asset_obj, update_cost_response = AssetUpdater.update_asset_total_cost(
                float(updated_parts_obj.total_cost) - float(old_total_cost), asset_obj)
            if update_cost_response.status_code != status.HTTP_202_ACCEPTED:
                return update_cost_response
            asset_obj.save()

            # Create asset record
            if (not AssetHistory.create_asset_record_by_obj(asset_obj)):
                Logger.getLogger().error(CustomError.get_error_dev(CustomError.MHF_0))
                return Response(CustomError.get_full_error_json(CustomError.MHF_0), status=status.HTTP_400_BAD_REQUEST)

            serializer = PartCostSerializer(updated_parts_obj)
            return Response(serializer.data, status=status.HTTP_200_OK)

        except Exception as e:
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.G_0, e))
            return Response(CustomError.get_full_error_json(CustomError.G_0, e), status=status.HTTP_400_BAD_REQUEST)


# ------------------------------------------------------------------------------------------------------------------------------------------------------

class InsuranceHandler():

    @staticmethod
    def handle_add_insurance_cost(request_data, user):
        try:
            db_name = user.db_access
            request_data = CurrencyConversionHelper.convert_currency_request_data(
                request_data,
                ['deductible', "total_cost"],
                db_name)

            if request_data == None:
                return Response(CustomError.get_full_error_json(CustomError.CDNE_0), status=status.HTTP_400_BAD_REQUEST)

            ser = InsuranceCostSerializer(data=request_data)

            if (ser.is_valid()):
                insurance_cost_obj = ser.save()

                # set created_by and modified_by
                insurance_cost_obj, created_by_status = InsuranceUpdater.update_insurance_cost_created_by(
                    insurance_cost_obj, user)
                if created_by_status.status_code != status.HTTP_202_ACCEPTED:
                    return created_by_status

                # set location based on VIN location
                insurance_cost_obj = GeneralCostUpdater.set_cost_obj_location_by_VIN(insurance_cost_obj,
                                                                                     InsuranceHelper.get_insurance_cost_obj_VIN(
                                                                                         insurance_cost_obj), user)
                insurance_cost_obj = ser.save()

                # create insurance cost record
                if (not InsuranceCostHistory.create_insurance_cost_record_by_obj(insurance_cost_obj)):
                    Logger.getLogger().error(CustomError.get_error_dev(CustomError.MHF_14))
                    return Response(CustomError.get_full_error_json(CustomError.MHF_14),
                                    status=status.HTTP_400_BAD_REQUEST)

                # update asset total_cost
                asset_obj = AssetHelper.get_asset_by_VIN(InsuranceHelper.get_insurance_cost_obj_VIN(insurance_cost_obj),
                                                         db_name)

                if not AssetHelper.check_asset_status_active(asset_obj.VIN, db_name):
                    Logger.getLogger().error(CustomError.get_error_dev(CustomError.TUF_16,
                                                                       CustomError.get_error_user(CustomError.TUF_16)))
                    return Response(CustomError.get_full_error_json(CustomError.TUF_16,
                                                                    CustomError.get_error_user(CustomError.TUF_16)),
                                    status=status.HTTP_400_BAD_REQUEST)

                asset_obj, update_cost_response = AssetUpdater.update_asset_total_cost(
                    float(request_data.get("total_cost")), asset_obj)
                if update_cost_response.status_code != status.HTTP_202_ACCEPTED:
                    return update_cost_response
                asset_obj.save()

                # Create asset record
                if (not AssetHistory.create_asset_record_by_obj(asset_obj)):
                    Logger.getLogger().error(CustomError.get_error_dev(CustomError.MHF_0))
                    return Response(CustomError.get_full_error_json(CustomError.MHF_0),
                                    status=status.HTTP_400_BAD_REQUEST)

                return Response(status=status.HTTP_201_CREATED)
            else:
                Logger.getLogger().error(CustomError.get_error_dev(CustomError.S_0, ser.errors))
                return Response(CustomError.get_full_error_json(CustomError.S_0, ser.errors),
                                status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.G_0, e))
            return Response(CustomError.get_full_error_json(CustomError.G_0, e), status=status.HTTP_400_BAD_REQUEST)

    # ---------------------------------------------------------------------------------------------------------------------

    @staticmethod
    def handle_delete_insurance_cost(request_data, user):
        try:
            db_name = user.db_access
            cost_entry = InsuranceCost.objects.using(db_name).get(id=request_data.get("id"))
            entry_total_cost = 0 - float(cost_entry.total_cost)
            cost_entry.delete()

            # update asset total_cost
            asset_obj = AssetHelper.get_asset_by_VIN(InsuranceHelper.get_insurance_cost_obj_VIN(cost_entry), db_name)
            asset_obj, update_cost_response = AssetUpdater.update_asset_total_cost(entry_total_cost, asset_obj)
            if update_cost_response.status_code != status.HTTP_202_ACCEPTED:
                return update_cost_response
            asset_obj.save()

            # # Create asset record
            if (not AssetHistory.create_asset_record_by_obj(asset_obj)):
                Logger.getLogger().error(CustomError.get_error_dev(CustomError.MHF_0))
                return Response(CustomError.get_full_error_json(CustomError.MHF_0), status=status.HTTP_400_BAD_REQUEST)

            return Response(status=status.HTTP_200_OK)

        except Exception as e:
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.G_0, e))
            return Response(CustomError.get_full_error_json(CustomError.G_0, e), status=status.HTTP_400_BAD_REQUEST)

    # ---------------------------------------------------------------------------------------------------------------------

    @staticmethod
    def handle_get_insurance_cost_by_accident_ID(accident_id, user):
        try:
            if not AccidentHelper.get_accident_exists(accident_id, user.db_access):
                Logger.getLogger().error(CustomError.ADNE_0)
                return Response(CustomError.get_full_error_json(CustomError.ADNE_0), status=status.HTTP_400_BAD_REQUEST)
            Insurance_cost = InsuranceHelper.select_related_to_Insurance(
                InsuranceHelper.get_insurance_cost_by_accident_ID(accident_id, user.db_access))
            ser = LightInsuranceCostSerializer(Insurance_cost, many=True)
            return Response(ser.data, status=status.HTTP_200_OK)
        except Exception as e:
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.G_0, e))
            return Response(CustomError.get_full_error_json(CustomError.G_0, e), status=status.HTTP_400_BAD_REQUEST)

    # ---------------------------------------------------------------------------------------------------------------------

    @staticmethod
    def handle_get_insurance_cost_by_vin(_vin, user):
        try:
            if not AssetHelper.asset_exists(_vin, user.db_access):
                Logger.getLogger().error(CustomError.VDNE_0)
                return Response(CustomError.get_full_error_json(CustomError.VDNE_0), status=status.HTTP_400_BAD_REQUEST)
            Insurance_cost = InsuranceHelper.select_related_to_Insurance(
                InsuranceHelper.get_insurance_cost_by_vin(_vin, user.db_access))
            ser = LightInsuranceCostSerializer(Insurance_cost, many=True)
            return Response(ser.data, status=status.HTTP_200_OK)
        except Exception as e:
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.G_0, e))
            return Response(CustomError.get_full_error_json(CustomError.G_0, e), status=status.HTTP_400_BAD_REQUEST)

    # ---------------------------------------------------------------------------------------------------------------------

    @staticmethod
    def handle_get_all_insurance_cost(user):
        try:
            Insurance_cost = InsuranceHelper.select_related_to_Insurance(
                InsuranceHelper.get_insurance_cost_list(user.db_access))
            ser = LightInsuranceCostSerializer(Insurance_cost, many=True)
            return Response(ser.data, status=status.HTTP_200_OK)
        except Exception as e:
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.G_0, e))
            return Response(CustomError.get_full_error_json(CustomError.G_0, e), status=status.HTTP_400_BAD_REQUEST)


# ------------------------------------------------------------------------------------------------------------------------------------------------------

class AcquisitionHandler():

    @staticmethod
    def handle_add_acquisition_cost(request_data, user):
        try:
            db_name = user.db_access
            request_data = CurrencyConversionHelper.convert_currency_request_data(
                request_data,
                ["taxes", "total_cost", "administrative_cost", "misc_cost"],
                db_name)

            if request_data == None:
                return Response(CustomError.get_full_error_json(CustomError.CDNE_0), status=status.HTTP_400_BAD_REQUEST)

            ser = AcquisitionCostSerializer(data=request_data)

            if (ser.is_valid()):
                acquisition_cost_obj = ser.save()

                # set created_by and modified_by
                acquisition_cost_obj, created_by_status = AcquisitionUpdater.update_acquisition_cost_created_by(
                    acquisition_cost_obj, user)
                if created_by_status.status_code != status.HTTP_202_ACCEPTED:
                    return created_by_status

                # set location based on VIN location
                acquisition_cost_obj = GeneralCostUpdater.set_cost_obj_location_by_VIN(acquisition_cost_obj,
                                                                                       request_data.get("VIN"), user)
                acquisition_cost_obj = ser.save()

                # create acquisition cost record
                if (not AcquisitionCostHistory.create_acquisition_cost_record_by_obj(acquisition_cost_obj)):
                    Logger.getLogger().error(CustomError.get_error_dev(CustomError.MHF_17))
                    return Response(CustomError.get_full_error_json(CustomError.MHF_17),
                                    status=status.HTTP_400_BAD_REQUEST)

                # update asset total_cost
                asset_obj = AssetHelper.get_asset_by_VIN(acquisition_cost_obj.VIN, db_name)
                asset_obj, update_cost_response = AssetUpdater.update_asset_total_cost(
                    float(request_data.get("total_cost")), asset_obj)
                if update_cost_response.status_code != status.HTTP_202_ACCEPTED:
                    return update_cost_response
                asset_obj.save()

                # Create asset record
                if (not AssetHistory.create_asset_record_by_obj(asset_obj)):
                    Logger.getLogger().error(CustomError.get_error_dev(CustomError.MHF_0))
                    return Response(CustomError.get_full_error_json(CustomError.MHF_0),
                                    status=status.HTTP_400_BAD_REQUEST)

                return Response(status=status.HTTP_201_CREATED)
            else:
                Logger.getLogger().error(CustomError.get_error_dev(CustomError.S_0, ser.errors))
                return Response(CustomError.get_full_error_json(CustomError.S_0, ser.errors),
                                status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.G_0, e))
            return Response(CustomError.get_full_error_json(CustomError.G_0, e), status=status.HTTP_400_BAD_REQUEST)

    # ---------------------------------------------------------------------------------------------------------------------

    @staticmethod
    def handle_delete_acquisition_cost(request_data, user):
        try:
            db_name = user.db_access
            cost_entry = AcquisitionCost.objects.using(db_name).filter(id=request_data.get("id"))
            cost_entry_values = cost_entry.values_list("total_cost", "VIN")[0]
            entry_total_cost = 0 - float(cost_entry_values[0])

            # update asset total_cost
            asset_obj = AssetHelper.get_asset_by_VIN(cost_entry_values[1], db_name)

            if not AssetHelper.check_asset_status_active(asset_obj.VIN, db_name):
                Logger.getLogger().error(CustomError.get_error_dev(CustomError.TUF_16,
                                                                   CustomError.get_error_user(CustomError.TUF_16)))
                return Response(CustomError.get_full_error_json(CustomError.TUF_16,
                                                                CustomError.get_error_user(CustomError.TUF_16)),
                                status=status.HTTP_400_BAD_REQUEST)

            cost_entry.delete()
            asset_obj, update_cost_response = AssetUpdater.update_asset_total_cost(entry_total_cost, asset_obj)
            if update_cost_response.status_code != status.HTTP_202_ACCEPTED:
                return update_cost_response
            asset_obj.save()

            # Create asset record
            if (not AssetHistory.create_asset_record_by_obj(asset_obj)):
                Logger.getLogger().error(CustomError.get_error_dev(CustomError.MHF_0))
                return Response(CustomError.get_full_error_json(CustomError.MHF_0), status=status.HTTP_400_BAD_REQUEST)

            return Response(status=status.HTTP_200_OK)

        except Exception as e:
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.G_0, e))
            return Response(CustomError.get_full_error_json(CustomError.G_0, e), status=status.HTTP_400_BAD_REQUEST)

    # ---------------------------------------------------------------------------------------------------------------------

    @staticmethod
    def handle_get_acquisition_cost_by_vin(_vin, user):
        try:
            acquisition_cost = AcquisitionHelper.select_related_to_acquisition(
                AcquisitionHelper.get_acquisition_cost_by_vin(_vin, user.db_access))
            ser = AcquisitionSerializer(acquisition_cost, many=True)
            return Response(ser.data, status=status.HTTP_200_OK)
        except Exception as e:
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.G_0, e))
            return Response(CustomError.get_full_error_json(CustomError.G_0, e), status=status.HTTP_400_BAD_REQUEST)

    # ---------------------------------------------------------------------------------------------------------------------

    @staticmethod
    def handle_get_all_acquisition_cost(user):
        try:
            acquisition_cost = AcquisitionHelper.select_related_to_acquisition(
                AcquisitionHelper.get_acquisition_cost_list(user.db_access))
            ser = AcquisitionSerializer(acquisition_cost, many=True)
            return Response(ser.data, status=status.HTTP_200_OK)
        except Exception as e:
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.G_0, e))
            return Response(CustomError.get_full_error_json(CustomError.G_0, e), status=status.HTTP_400_BAD_REQUEST)


# ------------------------------------------------------------------------------------------------------------------------------------------------------

class DeliveryHandler():

    @staticmethod
    def handle_add_delivery_cost(request_data, user):
        try:
            db_name = user.db_access
            request_data = CurrencyConversionHelper.convert_currency_request_data(
                request_data,
                ["taxes", "total_cost", "price"],
                db_name)

            if request_data == None:
                return Response(CustomError.get_full_error_json(CustomError.CDNE_0), status=status.HTTP_400_BAD_REQUEST)



            ser = DeliveryCostSerializer(data=request_data)

            if (ser.is_valid()):
                delivery_cost_obj = ser.save()

                # set created_by and modified_by
                delivery_cost_obj, created_by_status = DeliveryUpdater.update_delivery_cost_created_by(
                    delivery_cost_obj, user)
                if created_by_status.status_code != status.HTTP_202_ACCEPTED:
                    return created_by_status

                # set location based on VIN location
                delivery_cost_obj = GeneralCostUpdater.set_cost_obj_location_by_VIN(delivery_cost_obj,
                                                                                    DeliveryHelper.get_delivery_cost_obj_VIN(
                                                                                        delivery_cost_obj), user)
                delivery_cost_obj = ser.save()

                # create delivery cost history record
                if (not DeliveryCostHistory.create_delivery_cost_record_by_obj(delivery_cost_obj)):
                    Logger.getLogger().error(CustomError.get_error_dev(CustomError.MHF_17))
                    return Response(CustomError.get_full_error_json(CustomError.MHF_17),
                                    status=status.HTTP_400_BAD_REQUEST)

                # update asset total_cost
                asset_obj = AssetHelper.get_asset_by_VIN(DeliveryHelper.get_delivery_cost_obj_VIN(delivery_cost_obj),
                                                         db_name)

                if not AssetHelper.check_asset_status_active(asset_obj.VIN, db_name):
                    Logger.getLogger().error(CustomError.get_error_dev(CustomError.TUF_16,
                                                                       CustomError.get_error_user(CustomError.TUF_16)))
                    return Response(CustomError.get_full_error_json(CustomError.TUF_16,
                                                                    CustomError.get_error_user(CustomError.TUF_16)),
                                    status=status.HTTP_400_BAD_REQUEST)

                asset_obj, update_cost_response = AssetUpdater.update_asset_total_cost(
                    float(request_data.get("total_cost")), asset_obj)
                if update_cost_response.status_code != status.HTTP_202_ACCEPTED:
                    return update_cost_response
                asset_obj.save()

                # Create asset record
                if (not AssetHistory.create_asset_record_by_obj(asset_obj)):
                    Logger.getLogger().error(CustomError.get_error_dev(CustomError.MHF_0))
                    return Response(CustomError.get_full_error_json(CustomError.MHF_0),
                                    status=status.HTTP_400_BAD_REQUEST)

                return Response(status=status.HTTP_201_CREATED)
            else:
                Logger.getLogger().error(CustomError.get_error_dev(CustomError.S_0, ser.errors))
                return Response(CustomError.get_full_error_json(CustomError.S_0, ser.errors),
                                status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.G_0, e))
            return Response(CustomError.get_full_error_json(CustomError.G_0, e), status=status.HTTP_400_BAD_REQUEST)

    # ---------------------------------------------------------------------------------------------------------------------

    @staticmethod
    def handle_delete_delivery_cost(request_data, user):
        try:
            db_name = user.db_access
            cost_entry = DeliveryCost.objects.using(db_name).filter(id=request_data.get("id")).first()
            asset_obj = AssetHelper.get_asset_by_VIN(DeliveryHelper.get_delivery_cost_obj_VIN(cost_entry), db_name)

            if not AssetHelper.check_asset_status_active(asset_obj.VIN, db_name):
                Logger.getLogger().error(CustomError.get_error_dev(CustomError.TUF_16,
                                                                   CustomError.get_error_user(CustomError.TUF_16)))
                return Response(CustomError.get_full_error_json(CustomError.TUF_16,
                                                                CustomError.get_error_user(CustomError.TUF_16)),
                                status=status.HTTP_400_BAD_REQUEST)

            entry_total_cost = 0 - float(cost_entry.total_cost)
            cost_entry.delete()

            # update asset total_cost
            asset_obj, update_cost_response = AssetUpdater.update_asset_total_cost(entry_total_cost, asset_obj)
            if update_cost_response.status_code != status.HTTP_202_ACCEPTED:
                return update_cost_response
            asset_obj.save()

            # Create asset record
            if (not AssetHistory.create_asset_record_by_obj(asset_obj)):
                Logger.getLogger().error(CustomError.get_error_dev(CustomError.MHF_0))
                return Response(CustomError.get_full_error_json(CustomError.MHF_0), status=status.HTTP_400_BAD_REQUEST)

            return Response(status=status.HTTP_200_OK)

        except Exception as e:
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.G_0, e))
            return Response(CustomError.get_full_error_json(CustomError.G_0, e), status=status.HTTP_400_BAD_REQUEST)

    # ---------------------------------------------------------------------------------------------------------------------

    @staticmethod
    def handle_get_delivery_cost_by_maintenance(maintenance_id, user):
        try:
            if not MaintenanceHelper.get_maintenance_exists_by_id(maintenance_id, user.db_access):
                Logger.getLogger().error(CustomError.MRDNE_0)
                return Response(CustomError.get_full_error_json(CustomError.MRDNE_0),
                                status=status.HTTP_400_BAD_REQUEST)

            del_costs = DeliveryHelper.select_related_to_delivery(
                DeliveryHelper.get_delivery_cost_by_maintenance(maintenance_id, user.db_access))
            ser = LightDeliveryCostSerializer(del_costs, many=True)
            return Response(ser.data, status=status.HTTP_200_OK)
        except Exception as e:
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.G_0, e))
            return Response(CustomError.get_full_error_json(CustomError.G_0, e), status=status.HTTP_400_BAD_REQUEST)

    # ---------------------------------------------------------------------------------------------------------------------

    @staticmethod
    def handle_get_delivery_cost_by_repair(repair_id, user):
        try:
            if not RepairHelper.repair_exists_by_id(repair_id, user.db_access):
                Logger.getLogger().error(CustomError.RDNE_0)
                return Response(CustomError.get_full_error_json(CustomError.RDNE_0), status=status.HTTP_400_BAD_REQUEST)

            del_costs = DeliveryHelper.select_related_to_delivery(
                DeliveryHelper.get_delivery_cost_by_repair(repair_id, user.db_access))
            ser = LightDeliveryCostSerializer(del_costs, many=True)
            return Response(ser.data, status=status.HTTP_200_OK)
        except Exception as e:
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.G_0, e))
            return Response(CustomError.get_full_error_json(CustomError.G_0, e), status=status.HTTP_400_BAD_REQUEST)

    # ---------------------------------------------------------------------------------------------------------------------

    @staticmethod
    def handle_get_delivery_cost_by_asset_request(asset_request_id, user):
        try:
            if not AssetRequestHelper.asset_request_exists_by_id(asset_request_id, user.db_access):
                Logger.getLogger().error(CustomError.ARDNE_0)
                return Response(CustomError.get_full_error_json(CustomError.ARDNE_0),
                                status=status.HTTP_400_BAD_REQUEST)

            del_costs = DeliveryHelper.select_related_to_delivery(
                DeliveryHelper.get_delivery_cost_by_asset_request(asset_request_id, user.db_access))
            ser = LightDeliveryCostSerializer(del_costs, many=True)
            return Response(ser.data, status=status.HTTP_200_OK)
        except Exception as e:
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.G_0, e))
            return Response(CustomError.get_full_error_json(CustomError.G_0, e), status=status.HTTP_400_BAD_REQUEST)

    # ---------------------------------------------------------------------------------------------------------------------

    @staticmethod
    def handle_get_delivery_cost_by_disposal_id(disposal_id, user):
        try:
            if not DisposalHelper.disposal_exists(disposal_id, user.db_access):
                Logger.getLogger().error(CustomError.DDNE_0)
                return Response(CustomError.get_full_error_json(CustomError.DDNE_0), status=status.HTTP_400_BAD_REQUEST)

            del_costs = DeliveryHelper.select_related_to_delivery(
                DeliveryHelper.get_delivery_cost_by_disposal(disposal_id, user.db_access))
            ser = LightDeliveryCostSerializer(del_costs, many=True)
            return Response(ser.data, status=status.HTTP_200_OK)
        except Exception as e:
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.G_0, e))
            return Response(CustomError.get_full_error_json(CustomError.G_0, e), status=status.HTTP_400_BAD_REQUEST)

    # ---------------------------------------------------------------------------------------------------------------------

    @staticmethod
    def handle_get_delivery_cost_by_vin(vin, user):
        try:
            if not AssetHelper.asset_exists(vin, user.db_access):
                Logger.getLogger().error(CustomError.get_error_dev(CustomError.VDNE_0))
                return Response(CustomError.get_full_error_json(CustomError.VDNE_0), status=status.HTTP_400_BAD_REQUEST)

            del_costs = DeliveryHelper.select_related_to_delivery(
                DeliveryHelper.get_delivery_cost_by_vin(vin, user.db_access))
            ser = LightDeliveryCostSerializer(del_costs, many=True)
            return Response(ser.data, status=status.HTTP_200_OK)
        except Exception as e:
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.G_0, e))
            return Response(CustomError.get_full_error_json(CustomError.G_0, e), status=status.HTTP_400_BAD_REQUEST)

    # ---------------------------------------------------------------------------------------------------------------------

    @staticmethod
    def handle_get_all_delivery_cost(user):
        try:
            delivery_costs = DeliveryHelper.select_related_to_delivery(
                DeliveryHelper.get_delivery_costs(user.db_access))
            ser = LightDeliveryCostSerializer(delivery_costs, many=True)
            return Response(ser.data, status=status.HTTP_200_OK)
        except Exception as e:
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.G_0, e))
            return Response(CustomError.get_full_error_json(CustomError.G_0, e), status=status.HTTP_400_BAD_REQUEST)


# ------------------------------------------------------------------------------------------------------------------------------------------------------

class UnitChoicesHandler():

    @staticmethod
    def handle_get_all_fuel_types(user):
        try:
            fuel_types = UnitChoicesHelper.select_related_to_fueltype(
                UnitChoicesHelper.get_all_fuel_types(user.db_access))
            ser = FuelTypeSerializer(fuel_types, many=True)
            return Response(ser.data, status=status.HTTP_200_OK)
        except Exception as e:
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.G_0, e))
            return Response(CustomError.get_full_error_json(CustomError.G_0, e), status=status.HTTP_400_BAD_REQUEST)

    @staticmethod
    def handle_get_all_fuel_cards(user):
        try:
            fuel_cards = FuelCardHelper.get_fuel_cards(user.db_access)
            serializer = FuelCardSerializer(fuel_cards, many=True)
            return Response({"fuel_cards": serializer.data}, status=status.HTTP_200_OK)
        except Exception as e:
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.G_0, e))
            return Response(CustomError.get_full_error_json(CustomError.G_0, e), status=status.HTTP_400_BAD_REQUEST)

    @staticmethod
    def handle_get_all_currency_types(user):
        try:
            currency_types = UnitChoicesHelper.get_all_currency_types(user.db_access).order_by('code')
            ser = CurrencyTypeSerializer(currency_types, many=True)
            return Response(ser.data, status=status.HTTP_200_OK)
        except Exception as e:
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.G_0, e))
            return Response(CustomError.get_full_error_json(CustomError.G_0, e), status=status.HTTP_400_BAD_REQUEST)

    @staticmethod
    def handle_get_all_volume_unit_types(user):
        try:
            volume_units = UnitChoicesHelper.get_all_volume_units_types()
            return Response({"volume_unit_choices": volume_units}, status=status.HTTP_200_OK)
        except Exception as e:
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.G_0, e))
            return Response(CustomError.get_full_error_json(CustomError.G_0, e), status=status.HTTP_400_BAD_REQUEST)


# ------------------------------------------------------------------------------------------------------------------------------------------------------

class InvoiceHandler():
    @staticmethod
    def handle_analyze_invoices(request):
        try:
            files = request.FILES.getlist('files')
            valid_file_types = ["application/pdf", "image/jpeg", "image/png", "image/bmp", "image/tiff",
                                "application/json"]

            if not len(files) == 1:
                Logger.getLogger().error(CustomError.get_error_dev(CustomError.FUF_3))
                return Response(CustomError.get_full_error_json(CustomError.FUF_3), status=status.HTTP_400_BAD_REQUEST)

            extra_error_info = "The allowed file types are: ['pdf', 'bmp', 'jpeg', 'png', 'tiff', 'json']"
            if not FileHelper.verify_files_are_accepted_types(files, valid_file_types):
                Logger.getLogger().error(CustomError.get_error_dev(CustomError.FUF_1, extra_error_info))
                return Response(CustomError.get_full_error_json(CustomError.FUF_1, extra_error_info),
                                status=status.HTTP_400_BAD_REQUEST)

                # Authenicate
            form_recognizer_client = FormRecognizerClient(settings.ENDPOINT, AzureKeyCredential(settings.KEY))

            response_data = InvoiceHelper.recognize_invoice_content(form_recognizer_client, files[0])

            return Response(response_data, status=status.HTTP_200_OK)

        except Exception as e:
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.G_0, e))
            return Response(CustomError.get_full_error_json(CustomError.G_0, e), status=status.HTTP_400_BAD_REQUEST)


# ------------------------------------------------------------------------------------------------------------------------------------------------------

class FuelCardHandler():
    @staticmethod
    def handle_get_all_fuel_cards_by_business_unit(business_unit_id, user):
        try:
            fuel_cards = FuelCardHelper.get_fuel_cards_by_business_unit(business_unit_id, user.db_access)
            serializer = FuelCardSerializer(fuel_cards, many=True)
            return Response({"fuel_cards": serializer.data}, status=status.HTTP_200_OK)
        except Exception as e:
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.G_0, e))
            return Response(CustomError.get_full_error_json(CustomError.G_0, e), status=status.HTTP_400_BAD_REQUEST)

    @staticmethod
    def handle_add_fuel_card(request_data, user):
        try:
            ser = FuelCardSerializer(data=request_data)

            if (ser.is_valid()):
                fuelcard_obj = ser.save()

                # set issuer
                fuelcard_obj, created_by_status = FuelCardUpdater.update_fuel_card_issuer(fuelcard_obj, user)
                if created_by_status.status_code != status.HTTP_202_ACCEPTED:
                    return created_by_status

                fuelcard_obj.save()

                return Response(status=status.HTTP_201_CREATED)
            else:
                Logger.getLogger().error(CustomError.get_error_dev(CustomError.S_0, ser.errors))
                return Response(CustomError.get_full_error_json(CustomError.S_0, ser.errors),
                                status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.G_0, e))
            return Response(CustomError.get_full_error_json(CustomError.G_0, e), status=status.HTTP_400_BAD_REQUEST)

    @staticmethod
    def handle_update_fuel_card(request_data, user):
        try:
            fuelcard_obj = FuelCardHelper.get_fuel_card_by_card_id(request_data["card_id"], user.db_access)
            ser = FuelCardSerializer(fuelcard_obj, data=request_data, partial=True)

            if (ser.is_valid()):
                # set issuer
                fuelcard_obj, created_by_status = FuelCardUpdater.update_fuel_card_issuer(fuelcard_obj, user)
                if created_by_status.status_code != status.HTTP_202_ACCEPTED:
                    return created_by_status

                ser.save()

                return Response(status=status.HTTP_200_OK)
            else:
                Logger.getLogger().error(CustomError.get_error_dev(CustomError.S_0, ser.errors))
                return Response(CustomError.get_full_error_json(CustomError.S_0, ser.errors),
                                status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.G_0, e))
            return Response(CustomError.get_full_error_json(CustomError.G_0, e), status=status.HTTP_400_BAD_REQUEST)

# ------------------------------------------------------------------------------------------------------------------------------------------------------

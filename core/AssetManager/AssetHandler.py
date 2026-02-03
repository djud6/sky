from django.core.mail.message import sanitize_address
from rest_framework.response import Response
from rest_framework import status
from api.Models.asset_model_history import AssetModelHistory
from .AssetHelper import AssetHelper
from .AssetUpdater import AssetUpdater
from ..AssetTypeChecksManager.AssetTypeChecksHelper import AssetTypeChecksHelper
from api.Serializers.serializers import AssetModelSerializer, LightAssetModelSerializer, LightIssueSerializer, AssetFileSerializer, AssetTypeChecksSerializer, JobSpecificationSerializer, AnnualReportSerializer, AssetFileWithReportsSerializer
from api.Models.asset_model import AssetModel
from api.Models.asset_file import AssetFile
from ..HistoryManager.AssetHistory import AssetHistory
from ..FileManager.FileHelper import FileHelper
from ..BlobStorageManager.BlobStorageHelper import BlobStorageHelper
from ..UserManager.UserHelper import UserHelper
from ..DisposalManager.DisposalHelper import DisposalHelper
from ..TransferManager.TransferHelper import TransferHelper
from ..NotificationManager.NotificationHelper import NotificationHelper
from ..Helper import HelperMethods
from core.JobSpecificationManager.JobSpecificationHelper import JobSpecificationHelper
from ..FileManager.PdfManager import PdfManager
from ..VendorOpsManager.VendorOpsHelper import VendorOpsHelper
from communication.EmailService.EmailService import Email
from GSE_Backend.errors.ErrorDictionary import CustomError
from core.CostManager.CostHelper import PartsHelper, LaborHelper
from datetime import datetime, timedelta
from django.utils import timezone
import ast
import logging
from django.utils import timezone
from api.Models.repairs import RepairsModel
from api.Models.maintenance_request import MaintenanceRequestModel
from api.Models.accident_report import AccidentModel
from api.Models.annual_report import AnnualReport
from itertools import chain
from math import ceil
import requests


class Logger():
    @staticmethod
    def getLogger():
        return logging.getLogger(__name__)

class AssetHandler():
    @staticmethod
    def handle_add_asset(request_data, user):
        try:
            # Check if asset already exists
            if AssetHelper.asset_exists(request_data.get('VIN'), user.db_access):
                Logger.getLogger().error(CustomError.get_error_dev(CustomError.ACF_2))
                return Response(CustomError.get_full_error_json(CustomError.ACF_2), status=status.HTTP_400_BAD_REQUEST) 

            #Check the VIN Length - Minimum 6
            if(len(str(request_data.get('VIN'))) < 6):
                Logger.getLogger().error(CustomError.get_error_dev(CustomError.VL_1))
                return Response(CustomError.get_full_error_json(CustomError.VL_1), status=status.HTTP_400_BAD_REQUEST)

            # Add asset with only required fields
            asset, create_asset_response = AssetUpdater.create_asset(request_data, user)
            if create_asset_response.status_code != status.HTTP_201_CREATED:
                return create_asset_response

            # Add any optional fields provided
            updated_asset, update_asset_response = AssetUpdater.update_asset_optional_fields(asset, request_data, user)
            if update_asset_response.status_code != status.HTTP_200_OK:
                return update_asset_response

            updated_asset.save()

            # Create asset record
            if(not AssetHistory.create_asset_record_by_obj(updated_asset)):
                Logger.getLogger().error(CustomError.MHF_0)
                return Response(CustomError.get_full_error_json(CustomError.MHF_0), status=status.HTTP_400_BAD_REQUEST)

            return Response(status=status.HTTP_201_CREATED)
        except Exception as e:
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.G_0, e))
            return Response(CustomError.get_full_error_json(CustomError.G_0, e), status=status.HTTP_400_BAD_REQUEST)

    # ------------------------------------------------------------------------------------------------------------------

    @staticmethod
    def handle_add_bulk_asset(request_data, user):
        try:
            # Check if VINs already exist
            vin_list = [asset['VIN'] for asset in request_data['VINs']]
            if AssetHelper.assets_exist(vin_list, user.db_access):
                Logger.getLogger().error(CustomError.get_error_dev(CustomError.ACF_2))
                return Response(CustomError.get_full_error_json(CustomError.ACF_2), status=status.HTTP_400_BAD_REQUEST)

            # Check if all VINs have a unique unit number
            unit_numbers = [asset['unit_number'] for asset in request_data['VINs']]
            if len(set(unit_numbers)) != len(unit_numbers):
                Logger.getLogger().error(CustomError.get_error_dev(CustomError.UN_0))
                return Response(CustomError.get_full_error_json(CustomError.UN_0), status=status.HTTP_400_BAD_REQUEST)

            # Create assets with the provided attributes
            assets = []
            for vin in request_data['VINs']:
                asset, create_asset_response = AssetUpdater.create_asset(request_data, user)
                if create_asset_response.status_code != status.HTTP_201_CREATED:
                    return create_asset_response
                asset.VIN = vin['VIN']
                asset.unit_number = vin['unit_number']
                assets.append(asset)

            # Add any optional fields provided
            updated_assets = []
            for asset in assets:
                updated_asset, update_asset_response = AssetUpdater.update_asset_optional_fields(asset, request_data, user)
                if update_asset_response.status_code != status.HTTP_200_OK:
                    return update_asset_response
                updated_assets.append(updated_asset)

            # Save all assets at once
            AssetModel.objects.using(user.db_access).bulk_create(updated_assets)

            # Create asset records
            if not AssetHistory.create_bulk_asset_records_by_VINs(vin_list, user.db_access):
                Logger.getLogger().error(CustomError.MHF_0)
                return Response(CustomError.get_full_error_json(CustomError.MHF_0), status=status.HTTP_400_BAD_REQUEST)

            return Response(status=status.HTTP_201_CREATED)

        except Exception as e:
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.G_0, e))
            return Response(CustomError.get_full_error_json(CustomError.G_0, e), status=status.HTTP_400_BAD_REQUEST)
    
    # ------------------------------------------------------------------------------------------------------------------

    @staticmethod
    def handle_search_by_full_vin_or_unit_number(pk, user):
        try:
            asset_by_vin = AssetHelper.get_asset(pk)
            asset_by_unit_number = AssetHelper.get_asset_by_unit_number(pk, user.db_access)

            # Check to see if the request has been found and it is serializable
            if not asset_by_vin == status.HTTP_404_NOT_FOUND:
                if AssetHelper.asset_for_user(asset_by_vin, user):
                    try:
                        all_assets = AssetHelper.get_all_assets(user.db_access)
                        context = AssetHelper.get_serializer_context_2(all_assets,user)
                        serializer = LightAssetModelSerializer(asset_by_vin, context = context)
                        return Response(serializer.data, status=status.HTTP_200_OK)
                    except Exception as e:
                        Logger.getLogger().error(CustomError.get_error_dev(CustomError.S_0, e))
                        return Response(CustomError.get_full_error_json(CustomError.S_0, e), status=status.HTTP_400_BAD_REQUEST)

            if not asset_by_unit_number == status.HTTP_404_NOT_FOUND:
                if AssetHelper.asset_for_user(asset_by_unit_number, user):
                    try:
                        all_assets = AssetHelper.get_all_assets(user.db_access)
                        context = AssetHelper.get_serializer_context_2(all_assets,user)
                        serializer = LightAssetModelSerializer(asset_by_unit_number, context = context)
                        return Response(serializer.data, status=status.HTTP_200_OK)
                    except Exception as e:
                        Logger.getLogger().error(CustomError.get_error_dev(CustomError.S_0, e))
                        return Response(CustomError.get_full_error_json(CustomError.S_0, e), status=status.HTTP_400_BAD_REQUEST)

            # Req VIN and unit number Has not been found in the DB
            try:
                if(len(pk)==17):
                    url = f"https://vpic.nhtsa.dot.gov/api/vehicles/DecodeVin/{pk}?format=json"
                    response = requests.get(url, timeout=10)
                    response.raise_for_status()
                    data = response.json()
                    # Required fields
                    fields_required = ["Vehicle Descriptor","Make","Manufacturer Name","Model","Model Year","Plant City","Vehicle Type","Plant Country","Plant Company Name","Plant State","Series2","Body Class","Doors","Gross Vehicle Weight Rating From","Number of Wheels","Drive Type","Displacement (CC)","Displacement (CI)","Displacement (L)","Fuel Type - Primary"]
                    decoded_data = {
                        item['Variable']: item['Value']
                        for item in data.get('Results', [])
                        if item.get('Variable') in fields_required and item.get('Value') not in [None, "Not Applicable", "0", ""]
                    }
                    if decoded_data:
                        return Response({
                            "vin": pk,
                            **decoded_data
                        }, status=status.HTTP_200_OK)
                    else:
                        Logger.getLogger().error(CustomError.get_error_dev(CustomError.VDF_0))
                        return Response(CustomError.get_full_error_json(CustomError.VDF_0), status=status.HTTP_400_BAD_REQUEST)
                else:
                    Logger.getLogger().error(CustomError.get_error_dev(CustomError.VDF_0))
                    return Response(CustomError.get_full_error_json(CustomError.VDF_0), status=status.HTTP_400_BAD_REQUEST)

            except Exception as e:
                Logger.getLogger().error(CustomError.get_error_dev(CustomError.VDNE_0, e))
                return Response(CustomError.get_full_error_json(CustomError.VDNE_0, e), status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.G_0, e))
            return Response(CustomError.get_full_error_json(CustomError.G_0, e), status=status.HTTP_400_BAD_REQUEST)
        
    # ------------------------------------------------------------------------------------------------------------------

    @staticmethod
    def handle_search_asset_by_VIN_and_Unit_Number(substring, user):
        try:
            suggestions = []
            assets_by_vin = AssetHelper.filter_assets_for_user(AssetHelper.get_assets_by_VIN_endswith(substring, user.db_access), user)
            assets_by_unit_number = AssetHelper.filter_assets_for_user(AssetHelper.get_assets_by_unit_number_endswith(substring, user.db_access), user)

            # Check if both vin and unit number returned the same asset
            if list(assets_by_vin) == list(assets_by_unit_number):
                if assets_by_vin.count() + assets_by_unit_number.count() == 2:
                    all_assets = AssetHelper.get_all_assets(user.db_access)
                    context = AssetHelper.get_serializer_context_2(all_assets,user)
                    serializer = LightAssetModelSerializer(assets_by_vin, many=True, context=context)
                    return Response(serializer.data, status=status.HTTP_200_OK)

            # If we have more than one potential asset that fits our substring
            if assets_by_vin.count() + assets_by_unit_number.count() > 1:
                suggestions.extend(list(assets_by_vin.values_list('VIN', flat=True)))
                suggestions.extend(list(assets_by_unit_number.values_list('unit_number', flat=True)))
                suggestions = list(dict.fromkeys(suggestions)) # remove duplicates
                return Response(suggestions, status=status.HTTP_300_MULTIPLE_CHOICES)

            # If the other cases were not true, return the asset by vin if it exists
            if assets_by_vin.count() == 1:
                all_assets = AssetHelper.get_all_assets(user.db_access)
                context = AssetHelper.get_serializer_context_2(all_assets,user)
                serializer = LightAssetModelSerializer(assets_by_vin, many=True, context=context)
                return Response(serializer.data, status=status.HTTP_200_OK)

            # If the other cases were not true, return the asset by unit number if it exists
            if assets_by_unit_number.count() == 1:
                all_assets = AssetHelper.get_all_assets(user.db_access)
                context = AssetHelper.get_serializer_context_2(all_assets,user)
                serializer = LightAssetModelSerializer(assets_by_unit_number, many=True, context=context)
                return Response(serializer.data, status=status.HTTP_200_OK)

            # Req VIN/Unit# Has not been found in the DB
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.VDNE_0))
            return Response(CustomError.get_full_error_json(CustomError.VDNE_0), status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.G_0, e))
            return Response(CustomError.get_full_error_json(CustomError.G_0, e), status=status.HTTP_400_BAD_REQUEST)

    # ------------------------------------------------------------------------------------------------------------------

    @staticmethod
    def handle_get_all_asset_vins(user):
        try:
            qs = AssetModel.objects.all()
            relevant_vins = AssetHelper.filter_assets_for_user(qs, user).values('VIN')
            return Response(relevant_vins, status=status.HTTP_200_OK)

        except Exception as e:
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.G_0, e))
            return Response(CustomError.get_full_error_json(CustomError.G_0, e), status=status.HTTP_400_BAD_REQUEST)

    # ------------------------------------------------------------------------------------------------------------------

    @staticmethod
    def handle_get_all_assets(user):
        try:
            qs = AssetHelper.select_related_to_asset(AssetModel.objects.using(user.db_access).all())
            relevant_qs = AssetHelper.filter_assets_for_user(qs, user)
            context = AssetHelper.get_serializer_context_2(relevant_qs,user)
            ser = LightAssetModelSerializer(relevant_qs, many=True, context=context)
            return Response(ser.data, status=status.HTTP_200_OK)

        except Exception as e:
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.G_0, e))
            return Response(CustomError.get_full_error_json(CustomError.G_0, e), status=status.HTTP_400_BAD_REQUEST)

    # ------------------------------------------------------------------------------------------------------------------

    @staticmethod
    def handle_add_warranty_files(request, vin):
        try:
            if not AssetHelper.check_asset_status_active(vin, request.user.db_access):
                Logger.getLogger().error(CustomError.get_error_dev(CustomError.TUF_16,
                                                                   CustomError.get_error_user(CustomError.TUF_16)))
                return Response(CustomError.get_full_error_json(CustomError.TUF_16,
                                                                CustomError.get_error_user(CustomError.TUF_16)),
                                status=status.HTTP_400_BAD_REQUEST)

            data = request.POST.get('data')
            if data:
                data = HelperMethods.json_str_to_dict(data)

            expiration_date = data.get("expiration_date") if data else None
            files = request.FILES.getlist('files')

            valid_issue_file_types = ["application/pdf"]
            if not FileHelper.verify_files_are_accepted_types(files, valid_issue_file_types):
                Logger.getLogger().error(CustomError.get_error_dev(CustomError.FUF_1, "File(s) not pdf."))
                return Response(CustomError.get_full_error_json(CustomError.FUF_1, "File(s) not pdf."), status=status.HTTP_400_BAD_REQUEST) 

            # ------------ Upload files to blob --------------
            detailed_user = UserHelper.get_detailed_user_obj(request.user.email, request.user.db_access)
            company_name = detailed_user.company.company_name
            file_prefix = str(AssetFile.warranty) + "_" + str(vin) + "_"
            file_status, file_infos = BlobStorageHelper.write_files_to_blob(files, "asset/warranty", file_prefix, company_name, request.user.db_access)
            if(not file_status):
                Logger.getLogger().error(CustomError.get_error_dev(CustomError.FUF_0))
                return Response(CustomError.get_full_error_json(CustomError.FUF_0), status=status.HTTP_400_BAD_REQUEST)

            # ----------- Upload file urls to DB --------------
            asset_obj = AssetHelper.get_asset_by_VIN(vin, request.user.db_access)
            file_record_response = AssetUpdater.create_asset_file_records(asset_obj, file_infos,
            AssetFile.warranty, expiration_date, detailed_user, request.user.db_access)
            if file_record_response.status_code != status.HTTP_201_CREATED:
                return file_record_response

            # Apply to similar assets
            apply_to_similar_type = request.POST.get('apply_to_similar_type')
            if apply_to_similar_type:
                similar_assets = AssetHelper.get_similar_assets_make_model(vin, request.user.db_access)
                for similar_asset in similar_assets:
                    file_record_response = AssetUpdater.create_asset_file_records(similar_asset, file_infos, AssetFile.warranty, expiration_date, detailed_user, request.user.db_access)
                    if file_record_response.status_code != status.HTTP_201_CREATED:
                        return file_record_response

        except Exception as e:
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.G_0, e))
            return Response(CustomError.get_full_error_json(CustomError.G_0, e), status=status.HTTP_400_BAD_REQUEST)

        return Response(status=status.HTTP_200_OK)

    # -----------------------------------------------------------------------------------------------------------------

    @staticmethod
    def handle_add_insurance_files(request, vin):
        try:
            if not AssetHelper.check_asset_status_active(vin, request.user.db_access):
                Logger.getLogger().error(CustomError.get_error_dev(CustomError.TUF_16,
                                                                   CustomError.get_error_user(CustomError.TUF_16)))
                return Response(CustomError.get_full_error_json(CustomError.TUF_16,
                                                                CustomError.get_error_user(CustomError.TUF_16)),
                                status=status.HTTP_400_BAD_REQUEST)

            data = request.POST.get('data')
            if data:
                data = HelperMethods.json_str_to_dict(data)
            
            expiration_date = data.get("expiration_date") if data else None
            files = request.FILES.getlist('files')

            valid_issue_file_types = ["application/pdf"]
            if not FileHelper.verify_files_are_accepted_types(files, valid_issue_file_types):
                Logger.getLogger().error(CustomError.get_error_dev(CustomError.FUF_1, "File(s) not pdf."))
                return Response(CustomError.get_full_error_json(CustomError.FUF_1, "File(s) not pdf."), status=status.HTTP_400_BAD_REQUEST) 

            # ------------ Upload files to blob --------------
            detailed_user = UserHelper.get_detailed_user_obj(request.user.email, request.user.db_access)
            company_name = detailed_user.company.company_name
            file_prefix = str(AssetFile.insurance) + "_" + str(vin) + "_"
            file_status, file_infos = BlobStorageHelper.write_files_to_blob(files, "asset/insurance", file_prefix, company_name, request.user.db_access)
            if(not file_status):
                Logger.getLogger().error(CustomError.get_error_dev(CustomError.FUF_0))
                return Response(CustomError.get_full_error_json(CustomError.FUF_0), status=status.HTTP_400_BAD_REQUEST)

            # ----------- Upload file urls to DB --------------
            asset_obj = AssetHelper.get_asset_by_VIN(vin, request.user.db_access)
            file_record_response = AssetUpdater.create_asset_file_records(asset_obj, file_infos,
            AssetFile.insurance, expiration_date, detailed_user, request.user.db_access)
            if file_record_response.status_code != status.HTTP_201_CREATED:
                return file_record_response

            # Apply to similar assets
            apply_to_similar_type = request.POST.get('apply_to_similar_type')
            if apply_to_similar_type:
                similar_assets = AssetHelper.get_similar_assets_make_model(vin, request.user.db_access)
                for similar_asset in similar_assets:
                    file_record_response = AssetUpdater.create_asset_file_records(similar_asset, file_infos, AssetFile.insurance, expiration_date, detailed_user, request.user.db_access)
                    if file_record_response.status_code != status.HTTP_201_CREATED:
                        return file_record_response

        except Exception as e:
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.G_0, e))
            return Response(CustomError.get_full_error_json(CustomError.G_0, e), status=status.HTTP_400_BAD_REQUEST)

        return Response(status=status.HTTP_200_OK)



    # -----------------------------------------------------------------------------------------------------------------

    @staticmethod
    def handle_add_registration_files(request, vin):
        try:
            if not AssetHelper.check_asset_status_active(vin, request.user.db_access):
                Logger.getLogger().error(CustomError.get_error_dev(CustomError.TUF_16,
                                                                   CustomError.get_error_user(CustomError.TUF_16)))
                return Response(CustomError.get_full_error_json(CustomError.TUF_16,
                                                                CustomError.get_error_user(CustomError.TUF_16)),
                                status=status.HTTP_400_BAD_REQUEST)

            data = request.POST.get('data')
            if data:
                data = HelperMethods.json_str_to_dict(data)

            expiration_date = data.get("expiration_date") if data else None
            files = request.FILES.getlist('files')

            valid_issue_file_types = ["application/pdf"]
            if not FileHelper.verify_files_are_accepted_types(files, valid_issue_file_types):
                Logger.getLogger().error(CustomError.get_error_dev(CustomError.FUF_1, "File(s) not pdf."))
                return Response(CustomError.get_full_error_json(CustomError.FUF_1, "File(s) not pdf."), status=status.HTTP_400_BAD_REQUEST)

            # ------------ Upload files to blob --------------
            detailed_user = UserHelper.get_detailed_user_obj(request.user.email, request.user.db_access)
            company_name = detailed_user.company.company_name
            file_prefix = str(AssetFile.registration) + "_" + str(vin) + "_"
            file_status, file_infos = BlobStorageHelper.write_files_to_blob(files, "asset/registration", file_prefix, company_name, request.user.db_access)
            if(not file_status):
                Logger.getLogger().error(CustomError.get_error_dev(CustomError.FUF_0))
                return Response(CustomError.get_full_error_json(CustomError.FUF_0), status=status.HTTP_400_BAD_REQUEST)

            # ----------- Upload file urls to DB --------------
            asset_obj = AssetHelper.get_asset_by_VIN(vin, request.user.db_access)
            file_record_response = AssetUpdater.create_asset_file_records(asset_obj, file_infos,
                AssetFile.registration, expiration_date, detailed_user, request.user.db_access)
            if file_record_response.status_code != status.HTTP_201_CREATED:
                return file_record_response

            # Apply to similar assets
            apply_to_similar_type = request.POST.get('apply_to_similar_type')
            if apply_to_similar_type:
                similar_assets = AssetHelper.get_similar_assets_make_model(vin, request.user.db_access)
                for similar_asset in similar_assets:
                    file_record_response = AssetUpdater.create_asset_file_records(similar_asset, file_infos, AssetFile.registration, expiration_date, detailed_user, request.user.db_access)
                    if file_record_response.status_code != status.HTTP_201_CREATED:
                        return file_record_response

        except Exception as e:
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.G_0, e))
            return Response(CustomError.get_full_error_json(CustomError.G_0, e), status=status.HTTP_400_BAD_REQUEST)

        return Response(status=status.HTTP_200_OK)



    # -----------------------------------------------------------------------------------------------------------------

    @staticmethod
    def handle_add_other_files(request, vin):
        try:
            if not AssetHelper.check_asset_status_active(vin, request.user.db_access):
                Logger.getLogger().error(CustomError.get_error_dev(CustomError.TUF_16,
                                                                   CustomError.get_error_user(CustomError.TUF_16)))
                return Response(CustomError.get_full_error_json(CustomError.TUF_16,
                                                                CustomError.get_error_user(CustomError.TUF_16)),
                                status=status.HTTP_400_BAD_REQUEST)

            data = request.POST.get('data')
            if data:
                data = HelperMethods.json_str_to_dict(data)

            expiration_date = data.get("expiration_date") if data else None
            files = request.FILES.getlist('files')

            valid_issue_file_types = ["application/pdf"]
            if not FileHelper.verify_files_are_accepted_types(files, valid_issue_file_types):
                Logger.getLogger().error(CustomError.get_error_dev(CustomError.FUF_1, "File(s) not pdf."))
                return Response(CustomError.get_full_error_json(CustomError.FUF_1, "File(s) not pdf."), status=status.HTTP_400_BAD_REQUEST) 

            # ------------ Upload files to blob --------------
            detailed_user = UserHelper.get_detailed_user_obj(request.user.email, request.user.db_access)
            company_name = detailed_user.company.company_name
            file_prefix = str(AssetFile.other) + "_" + str(vin) + "_"
            file_status, file_infos = BlobStorageHelper.write_files_to_blob(files, "asset/other", file_prefix, company_name, request.user.db_access)
            if(not file_status):
                Logger.getLogger().error(CustomError.get_error_dev(CustomError.FUF_0))
                return Response(CustomError.get_full_error_json(CustomError.FUF_0), status=status.HTTP_400_BAD_REQUEST)

            # ----------- Upload file urls to DB --------------
            asset_obj = AssetHelper.get_asset_by_VIN(vin, request.user.db_access)
            file_record_response = AssetUpdater.create_asset_file_records(asset_obj, file_infos,
            AssetFile.other, expiration_date, detailed_user, request.user.db_access)
            if file_record_response.status_code != status.HTTP_201_CREATED:
                return file_record_response

            # Apply to similar assets
            apply_to_similar_type = request.POST.get('apply_to_similar_type')
            if apply_to_similar_type:
                similar_assets = AssetHelper.get_similar_assets_make_model(vin, request.user.db_access)
                for similar_asset in similar_assets:
                    file_record_response = AssetUpdater.create_asset_file_records(similar_asset, file_infos, AssetFile.other, expiration_date, detailed_user, request.user.db_access)
                    if file_record_response.status_code != status.HTTP_201_CREATED:
                        return file_record_response

        except Exception as e:
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.G_0, e))
            return Response(CustomError.get_full_error_json(CustomError.G_0, e), status=status.HTTP_400_BAD_REQUEST)

        return Response(status=status.HTTP_200_OK)

    # -----------------------------------------------------------------------------------------------------------------

    @staticmethod
    def handle_add_supporting_files(vin, request_file_specs, request_files, user):
        try:
            if not AssetHelper.asset_exists(vin, user.db_access):
                Logger.getLogger().error(CustomError.get_error_dev(CustomError.VDNE_0))
                return Response(CustomError.get_full_error_json(CustomError.VDNE_0), status=status.HTTP_400_BAD_REQUEST)

            if not AssetHelper.check_asset_status_active(vin, user.db_access):
                Logger.getLogger().error(CustomError.get_error_dev(CustomError.TUF_16,
                                                                   CustomError.get_error_user(CustomError.TUF_16)))
                return Response(CustomError.get_full_error_json(CustomError.TUF_16,
                                                                CustomError.get_error_user(CustomError.TUF_16)),
                                status=status.HTTP_400_BAD_REQUEST)

            detailed_user = UserHelper.get_detailed_user_obj(user.email, user.db_access)
            company_name = detailed_user.company.company_name
            file_specs = request_file_specs.get("file_info")
            files = request_files

            file_entries = []
            for _file in files:
                file_purpose = ""
                for info in file_specs:
                    if info.get("file_name") == _file.name:
                        file_purpose = info.get("purpose").lower()
                        expiration_date = info.get("expiration_date")
                        break

                # Check if purpose is valid
                if not AssetHelper.validate_purpose(file_purpose):
                    Logger.getLogger().error(CustomError.get_error_dev(CustomError.FUF_2))
                    return Response(CustomError.get_full_error_json(CustomError.FUF_2), status=status.HTTP_400_BAD_REQUEST)

                # Check if file type is valid
                valid_issue_file_types = AssetHelper.get_allowed_file_types_for_purpose(file_purpose)
                if not FileHelper.verify_file_is_accepted_type(_file, valid_issue_file_types):
                    Logger.getLogger().error(CustomError.get_error_dev(CustomError.FUF_1))
                    return Response(CustomError.get_full_error_json(CustomError.FUF_1), status=status.HTTP_400_BAD_REQUEST) 

                # ------------ Upload files to blob --------------
                file_prefix = str(file_purpose.replace(" ", "_")) + "_" + str(vin) + "_"
                container = "asset/" + BlobStorageHelper.clean_container_name(file_purpose)

                file_status, file_info = BlobStorageHelper.write_file_to_blob(_file, container, file_prefix, company_name, user.db_access)
                if(not file_status):
                    Logger.getLogger().error(CustomError.get_error_dev(CustomError.FUF_0))
                    return Response(CustomError.get_full_error_json(CustomError.FUF_0), status=status.HTTP_400_BAD_REQUEST)

                # ------------ Create file entry -----------------
                asset_obj = AssetHelper.get_asset_by_VIN(vin, user.db_access)
                file_entry = AssetUpdater.construct_asset_file_instance(asset_obj, file_info, file_purpose, expiration_date, detailed_user)

                file_entries.append(file_entry)

            # Upload file entries to db
            AssetFile.objects.using(user.db_access).bulk_create(file_entries)

        except Exception as e:
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.G_0, e))
            return Response(CustomError.get_full_error_json(CustomError.G_0, e), status=status.HTTP_400_BAD_REQUEST)

        return Response(status=status.HTTP_200_OK)


    # -----------------------------------------------------------------------------------------------------------------

    @staticmethod
    def handle_get_asset_files(vin, user):
        try:
            all_files = AssetHelper.get_asset_files_by_vin(vin, user.db_access).order_by('-file_id')
            ser = AssetFileSerializer(all_files, many=True)
            return Response(AssetHelper.secure_asset_file_ser_urls(ser.data, user.db_access), status=status.HTTP_200_OK)

        except Exception as e:
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.G_0, e))
            return Response(CustomError.get_full_error_json(CustomError.G_0, e), status=status.HTTP_400_BAD_REQUEST)  

    # -----------------------------------------------------------------------------------------------------------------

    @staticmethod
    def handle_get_all_ins_and_reg_files(vin, user):
        try:
            detailed_user_info = UserHelper.get_detailed_user_obj(user.email, user.db_access)
            registration_files_qs = AssetHelper.get_all_reg_files_by_vin(vin, user.db_access, detailed_user_info).order_by('-file_id')
            insurance_files_qs = AssetHelper.get_all_ins_files_by_vin(vin, user.db_access, detailed_user_info).order_by('-file_id')
            asset_files_qs = list(chain(insurance_files_qs, registration_files_qs))
            ser = AssetFileSerializer(asset_files_qs, many=True)
            return Response(ser.data, status=status.HTTP_200_OK)

        except Exception as e:
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.G_0, e))
            return Response(CustomError.get_full_error_json(CustomError.G_0, e), status=status.HTTP_400_BAD_REQUEST) 

    # -----------------------------------------------------------------------------------------------------------------

    @staticmethod
    def handle_get_asset_downtime(vin, user):
        try:
            return Response({"non_preventable_hours": 60, "preventable_hours": 140, "percent_non_preventable": 30, "percent_preventable": 70}, status=status.HTTP_200_OK)

        except Exception as e:
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.G_0, e))
            return Response(CustomError.get_full_error_json(CustomError.G_0, e), status=status.HTTP_400_BAD_REQUEST)

    # -----------------------------------------------------------------------------------------------------------------

    @staticmethod
    def handle_get_fleet_downtime(user):
        try:
            return Response({"non_preventable_hours": 6000, "preventable_hours": 14000, "percent_non_preventable": 30, "percent_preventable": 70}, status=status.HTTP_200_OK)

        except Exception as e:
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.G_0, e))
            return Response(CustomError.get_full_error_json(CustomError.G_0, e), status=status.HTTP_400_BAD_REQUEST)

    # -----------------------------------------------------------------------------------------------------------------
    
    @staticmethod
    def handle_is_usage_valid(request_data, user):
        try:
            asset_obj = AssetHelper.get_asset_by_VIN(request_data.get('VIN'), user.db_access)
            mileage = request_data.get('mileage')
            hours = request_data.get('hours')
            return AssetHelper.validate_usage_update(asset_obj, mileage, hours, user.db_access, tolerance_percentage=300)

        except Exception as e:
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.G_0, e))
            return Response(CustomError.get_full_error_json(CustomError.G_0, e), status=status.HTTP_400_BAD_REQUEST)

    # -----------------------------------------------------------------------------------------------------------------
    
    @staticmethod
    def handle_get_asset_checks(vin, user):
        try:
            asset_type_checks_id = None
            try:
                asset_type_checks_id = AssetHelper.get_asset_by_VIN(vin, user.db_access).equipment_type.asset_type.asset_type_checks.id
            except Exception:
                pass
            asset_type_checks = AssetTypeChecksHelper.get_checks_by_id(asset_type_checks_id, user.db_access)
            ser = AssetTypeChecksSerializer(asset_type_checks)
            return Response(ser.data, status=status.HTTP_200_OK)
        except Exception as e:
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.G_0, e))
            return Response(CustomError.get_full_error_json(CustomError.G_0, e), status=status.HTTP_400_BAD_REQUEST)
        
    # -----------------------------------------------------------------------------------------------------------------

    @staticmethod
    def handle_list_job_specification(user):
        try:
            qs = JobSpecificationHelper.get_all_job_specification(user.db_access).order_by('name')
            ser = JobSpecificationSerializer(qs, many=True)
            return Response(ser.data, status=status.HTTP_200_OK)
        except Exception as e:
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.G_0, e))
            return Response(CustomError.get_full_error_json(CustomError.G_0, e), status=status.HTTP_400_BAD_REQUEST)

    # -----------------------------------------------------------------------------------------------------------------

    @staticmethod
    def handle_get_usage_tracking_types():
        try:
            choices = AssetModel.hours_or_mileage_choices
            usage_tracking_types = [x[1] for x in choices]
            return Response(usage_tracking_types, status=status.HTTP_200_OK)
        except Exception as e:
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.G_0, e))
            return Response(CustomError.get_full_error_json(CustomError.G_0, e), status=status.HTTP_400_BAD_REQUEST)
    
    # -----------------------------------------------------------------------------------------------------------------

    @staticmethod
    def handle_update_asset(request_data, user):
        try:
            # Check if VIN exists
            if not AssetHelper.asset_exists(request_data.get("VIN"), user.db_access):
                Logger.getLogger().error(CustomError.get_error_dev(CustomError.VDNE_0))
                return Response(CustomError.get_full_error_json(CustomError.VDNE_0), status=status.HTTP_400_BAD_REQUEST)

            asset = AssetHelper.get_asset_by_VIN(request_data.get("VIN"), user.db_access)
            if not AssetHelper.check_asset_status_active(asset.VIN, user.db_access):
                Logger.getLogger().error(CustomError.get_error_dev(CustomError.TUF_16,
                                                                   CustomError.get_error_user(CustomError.TUF_16)))
                return Response(CustomError.get_full_error_json(CustomError.TUF_16,
                                                                CustomError.get_error_user(CustomError.TUF_16)),
                                status=status.HTTP_400_BAD_REQUEST)

            # Update asset fields
            updated_asset, update_response = AssetUpdater.update_asset_fields(asset, request_data, user)
            if update_response.status_code != status.HTTP_202_ACCEPTED:
                return update_response

            # Create asset record
            if(not AssetHistory.create_asset_record_by_obj(updated_asset)):
                Logger.getLogger().error(CustomError.MHF_0)
                return Response(CustomError.get_full_error_json(CustomError.MHF_0), status=status.HTTP_400_BAD_REQUEST)
            
            context = AssetHelper.get_serializer_context_2(None,user)
            serializer = LightAssetModelSerializer(updated_asset,context=context)

            return Response(serializer.data, status=status.HTTP_200_OK)

        except Exception as e:
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.G_0, e))
            return Response(CustomError.get_full_error_json(CustomError.G_0, e), status=status.HTTP_400_BAD_REQUEST)

    # -----------------------------------------------------------------------------------------------------------------

    @staticmethod
    def handle_update_asset_custom_fields(request_data, vin, user):
        try:
            if not AssetHelper.check_asset_status_active(vin, user.db_access):
                Logger.getLogger().error(CustomError.get_error_dev(CustomError.TUF_16,
                                                                   CustomError.get_error_user(CustomError.TUF_16)))
                return Response(CustomError.get_full_error_json(CustomError.TUF_16,
                                                                CustomError.get_error_user(CustomError.TUF_16)),
                                status=status.HTTP_400_BAD_REQUEST)

            # Convert the custom_fields string to a dictionary
            config_obj = AssetHelper.get_asset_by_VIN(vin, user.db_access)
            custom_fields_dict = {}
            if config_obj.custom_fields:
                custom_fields_dict = ast.literal_eval(config_obj.custom_fields)

            # Update the custom_fields dictionary with the request_data
            custom_fields_dict.update(request_data)

            # Convert the updated custom_fields dictionary back to a string and update the AssetModel object
            updated_custom_fields = str(custom_fields_dict)
            config_obj.custom_fields = updated_custom_fields
            config_obj.save()

            serializer = AssetModelSerializer(config_obj)

            return Response(serializer.data, status=status.HTTP_200_OK)

        except Exception as e:
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.G_0, e))
            return Response(CustomError.get_full_error_json(CustomError.G_0, e), status=status.HTTP_400_BAD_REQUEST)
        
    # -----------------------------------------------------------------------------------------------------------------
    
    @staticmethod
    def handle_delete_asset_custom_fields(request_data, vin, user):
        try:
            if not AssetHelper.check_asset_status_active(vin, user.db_access):
                Logger.getLogger().error(CustomError.get_error_dev(CustomError.TUF_16,
                                                                   CustomError.get_error_user(CustomError.TUF_16)))
                return Response(CustomError.get_full_error_json(CustomError.TUF_16,
                                                                CustomError.get_error_user(CustomError.TUF_16)),
                                status=status.HTTP_400_BAD_REQUEST)

            # Convert the custom_fields string to a dictionary
            config_obj = AssetHelper.get_asset_by_VIN(vin, user.db_access)
            custom_fields_dict = {}
            if config_obj.custom_fields:
                custom_fields_dict = ast.literal_eval(config_obj.custom_fields)

            # Update the custom_fields dictionary with the request_data
            keys = list(request_data.keys())
            for key in keys:
                if request_data[key] == None or len(request_data[key]) == 0:
                    del custom_fields_dict[key]
                else:
                    for subkey in request_data[key]:
                        del custom_fields_dict[key][subkey]    
                    if custom_fields_dict[key] == None or len(custom_fields_dict[key]) == 0:
                        del custom_fields_dict[key]

            # Convert the updated custom_fields dictionary back to a string and update the AssetModel object
            updated_custom_fields = str(custom_fields_dict)
            config_obj.custom_fields = updated_custom_fields
            config_obj.save()

            serializer = AssetModelSerializer(config_obj)

            return Response(serializer.data, status=status.HTTP_200_OK)

        except Exception as e:
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.G_0, e))
            return Response(CustomError.get_full_error_json(CustomError.G_0, e), status=status.HTTP_400_BAD_REQUEST)
        
    # -----------------------------------------------------------------------------------------------------------------
    
    @staticmethod
    def handle_reassign_asset(request_data, user):
        try:
            if not AssetHelper.check_asset_status_active(request_data.get("VIN"), user.db_access):
                Logger.getLogger().error(CustomError.get_error_dev(CustomError.TUF_16,
                                                                   CustomError.get_error_user(CustomError.TUF_16)))
                return Response(CustomError.get_full_error_json(CustomError.TUF_16,
                                                                CustomError.get_error_user(CustomError.TUF_16)),
                                status=status.HTTP_400_BAD_REQUEST)

            original_asset = AssetHelper.get_asset_by_VIN(request_data.get("VIN"), user.db_access)
            update_response = AssetHandler.handle_update_asset(request_data, user)
            updated_asset_dict = update_response.data
            if update_response.status_code != status.HTTP_200_OK:
                return update_response

            if HelperMethods.validate_bool(request_data.get("notify_managers")):
                # -------------- Email managers about reassignment ---------------
                notification_config, resp = NotificationHelper.get_notification_config_by_name("Asset Reassigned", user.db_access)
                if resp.status_code != status.HTTP_302_FOUND:
                    return resp
                if notification_config.active and (
                    notification_config.triggers is None or (
                        "reassign_asset" in NotificationHelper.parse_triggers_to_list(notification_config.triggers)
                    )
                ):
                    html_message = PdfManager.gen_reassign_asset_html(original_asset, updated_asset_dict, notification_config, user)
                    email_title = "Asset (VIN: " + str(updated_asset_dict.get("VIN")) + ") Reassignment Notification"

                    if notification_config.recipient_type == "auto":
                        recipients = AssetHelper.get_asset_managers_emails(updated_asset_dict.get("VIN"), user.db_access)
                    else:
                        recipients = NotificationHelper.get_recipients_for_notification(notification_config, user.db_access)

                    email_response = Email.send_email_notification(recipients, email_title, html_message, [], html_content=True)
                    if email_response.status_code != status.HTTP_200_OK:
                        return email_response
                # ----------------------------------------------------------------

            return Response(status=status.HTTP_200_OK)

        except Exception as e:
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.G_0, e))
            return Response(CustomError.get_full_error_json(CustomError.G_0, e), status=status.HTTP_400_BAD_REQUEST)

    # -----------------------------------------------------------------------------------------------------------------


    @staticmethod
    def handle_set_asset_parent(request_data, user):
        try:
            # Check if parent VIN exists
            if not AssetHelper.asset_exists(request_data.get("parent_VIN"), user.db_access): 
                Logger.getLogger().error(CustomError.get_error_dev(CustomError.VDNE_0, "Parent VIN does not exist."))
                return Response(CustomError.get_full_error_json(CustomError.VDNE_0, "Parent VIN does not exist."), status=status.HTTP_400_BAD_REQUEST)

            if not AssetHelper.check_asset_status_active(request_data.get("parent_VIN"), user.db_access):
                Logger.getLogger().error(CustomError.get_error_dev(CustomError.TUF_16,
                                                                   CustomError.get_error_user(CustomError.TUF_16)))
                return Response(CustomError.get_full_error_json(CustomError.TUF_16,
                                                                CustomError.get_error_user(CustomError.TUF_16)),
                                status=status.HTTP_400_BAD_REQUEST)

            # Check if asset is its own parent
            if request_data.get('parent_VIN') == request_data.get('VIN'):
                Logger.getLogger().error(CustomError.get_error_dev(CustomError.PCF_0))
                return Response(CustomError.get_full_error_json(CustomError.PCF_0), status=status.HTTP_400_BAD_REQUEST)

            # Check if child VIN exists
            if not AssetHelper.asset_exists(request_data.get('VIN'), user.db_access):
                Logger.getLogger().error(CustomError.get_error_dev(CustomError.VDNE_0, "Child VIN does not exist."))
                return Response(CustomError.get_full_error_json(CustomError.VDNE_0, "Child VIN does not exist."), status=status.HTTP_400_BAD_REQUEST)

            if not AssetHelper.check_asset_status_active(request_data.get("VIN"), user.db_access):
                Logger.getLogger().error(CustomError.get_error_dev(CustomError.TUF_16,
                                                                   CustomError.get_error_user(CustomError.TUF_16)))
                return Response(CustomError.get_full_error_json(CustomError.TUF_16,
                                                                CustomError.get_error_user(CustomError.TUF_16)),
                                status=status.HTTP_400_BAD_REQUEST)

            # Check for circular dependency
            if(AssetHelper.asset_circular_dependency_check(request_data.get('VIN'), request_data.get('parent_VIN'))):
                Logger.getLogger().error(CustomError.get_error_dev(CustomError.PCF_1))
                return Response(CustomError.get_full_error_json(CustomError.PCF_1), status=status.HTTP_400_BAD_REQUEST)

            update_response = AssetHandler.handle_update_asset(request_data, user)
            if update_response.status_code != status.HTTP_200_OK:
                return update_response

            # Asset record is created inside handle_update_asset()

            return Response(status=status.HTTP_200_OK)

        except Exception as e:
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.G_0, e))
            return Response(CustomError.get_full_error_json(CustomError.G_0, e), status=status.HTTP_400_BAD_REQUEST)

    # -----------------------------------------------------------------------------------------------------------------

    @staticmethod
    def handle_add_asset_children(request_data, user):
        try:
            # Check if parent VIN exists
            if not AssetHelper.asset_exists(request_data.get('parent_VIN'), user.db_access):
                Logger.getLogger().error(CustomError.get_error_dev(CustomError.VDNE_0, "Parent VIN does not exist."))
                return Response(CustomError.get_full_error_json(CustomError.VDNE_0, "Parent VIN does not exist."),
                                status=status.HTTP_400_BAD_REQUEST)

            # Check if parent VIN is active (Cannot be Inoperative)
            if not AssetHelper.check_asset_status_active(request_data.get("parent_VIN"),
                                                         user.db_access, allow_inoperative=False):
                Logger.getLogger().error(CustomError.get_error_dev(CustomError.TUF_16,
                                                                   CustomError.get_error_user(CustomError.TUF_16)))
                return Response(CustomError.get_full_error_json(CustomError.TUF_16,
                                                                CustomError.get_error_user(CustomError.TUF_16)),
                                status=status.HTTP_400_BAD_REQUEST)

            # Check if child VINs == parent VIN
            if request_data.get('parent_VIN') in request_data.get('child_VINs'):
                Logger.getLogger().error(CustomError.get_error_dev(CustomError.PCF_0))
                return Response(CustomError.get_full_error_json(CustomError.PCF_0), status=status.HTTP_400_BAD_REQUEST)

            # Check if child VIN(s) exist
            if not AssetHelper.assets_exist(request_data.get('child_VINs'), user.db_access):
                Logger.getLogger().error(CustomError.get_error_dev(CustomError.VDNE_0,
                                                                   "One or more of the child VINs DNE."))
                return Response(CustomError.get_full_error_json(CustomError.VDNE_0,
                                                                "One or more of the child VINs DNE."),
                                status=status.HTTP_400_BAD_REQUEST)

            # Check for circular dependency
            for VIN in request_data.get('child_VINs'):
                # Check if child VIN is active (Cannot be Inoperative)
                if not AssetHelper.check_asset_status_active(VIN, user.db_access, allow_inoperative=False):
                    Logger.getLogger().error(CustomError.get_error_dev(CustomError.TUF_16,
                                                                       CustomError.get_error_user(CustomError.TUF_16)))
                    return Response(CustomError.get_full_error_json(CustomError.TUF_16,
                                                                    CustomError.get_error_user(CustomError.TUF_16)),
                                    status=status.HTTP_400_BAD_REQUEST)

                if AssetHelper.asset_circular_dependency_check(VIN, request_data.get('parent_VIN'), user.db_access):
                    Logger.getLogger().error(CustomError.get_error_dev(CustomError.PCF_1))
                    return Response(CustomError.get_full_error_json(CustomError.PCF_1),
                                    status=status.HTTP_400_BAD_REQUEST)

            # Add children to parent
            detailed_user = UserHelper.get_detailed_user_obj(user.email, user.db_access)
            AssetModel.objects.using(user.db_access).filter(
                VIN__in=request_data.get('child_VINs')).update(parent=request_data.get('parent_VIN'),
                                                               modified_by=detailed_user)

            # Create asset record
            if not AssetHistory.create_bulk_asset_records_by_VINs(request_data.get('child_VINs'), user.db_access):
                Logger.getLogger().error(CustomError.MHF_0)
                return Response(CustomError.get_full_error_json(CustomError.MHF_0), status=status.HTTP_400_BAD_REQUEST)

            return Response(status=status.HTTP_200_OK)

        except Exception as e:
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.G_0, e))
            return Response(CustomError.get_full_error_json(CustomError.G_0, e), status=status.HTTP_400_BAD_REQUEST)

    # -----------------------------------------------------------------------------------------------------------------
    
    @staticmethod
    def handle_remove_asset_parent(request_data, user):
        try:
            # Check if child VIN exists
            if not AssetHelper.asset_exists(request_data.get('VIN'), user.db_access):
                Logger.getLogger().error(CustomError.get_error_dev(CustomError.VDNE_0, "Child VIN does not exist."))
                return Response(CustomError.get_full_error_json(CustomError.VDNE_0, "Child VIN does not exist."), status=status.HTTP_400_BAD_REQUEST)

            if not AssetHelper.check_asset_status_active(request_data.get("VIN"), user.db_access):
                Logger.getLogger().error(CustomError.get_error_dev(CustomError.TUF_16,
                                                                   CustomError.get_error_user(CustomError.TUF_16)))
                return Response(CustomError.get_full_error_json(CustomError.TUF_16,
                                                                CustomError.get_error_user(CustomError.TUF_16)),
                                status=status.HTTP_400_BAD_REQUEST)

            request_data['parent_VIN'] = 'none'
            update_response = AssetHandler.handle_update_asset(request_data, user)
            if update_response.status_code != status.HTTP_200_OK:
                return update_response

            # Asset record is created inside handle_update_asset()

            return Response(status=status.HTTP_200_OK)

        except Exception as e:
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.G_0, e))
            return Response(CustomError.get_full_error_json(CustomError.G_0, e), status=status.HTTP_400_BAD_REQUEST)

    # -----------------------------------------------------------------------------------------------------------------
    
    @staticmethod
    def handle_remove_asset_children(request_data, user):
        try:
            # Check if child VIN(s) exist
            if not AssetHelper.assets_exist(request_data.get('child_VINs'), user.db_access):
                Logger.getLogger().error(CustomError.get_error_dev(CustomError.VDNE_0, "One or more of the child VINs DNE."))
                return Response(CustomError.get_full_error_json(CustomError.VDNE_0, "One or more of the child VINs DNE."), status=status.HTTP_400_BAD_REQUEST)

            for child_vin in request_data.get('child_VINs'):
                if not AssetHelper.check_asset_status_active(child_vin, user.db_access):
                    Logger.getLogger().error(CustomError.get_error_dev(CustomError.TUF_16,
                                                                       CustomError.get_error_user(CustomError.TUF_16)))
                    return Response(CustomError.get_full_error_json(CustomError.TUF_16,
                                                                    CustomError.get_error_user(CustomError.TUF_16)),
                                    status=status.HTTP_400_BAD_REQUEST)

            # Remove children from parent
            detailed_user = UserHelper.get_detailed_user_obj(user.email, user.db_access)
            AssetModel.objects.using(user.db_access).filter(VIN__in=request_data.get('child_VINs')).update(parent=None, modified_by=detailed_user)

            # Create asset record
            if(not AssetHistory.create_bulk_asset_records_by_VINs(request_data.get('child_VINs'), user.db_access)):
                Logger.getLogger().error(CustomError.MHF_0)
                return Response(CustomError.get_full_error_json(CustomError.MHF_0), status=status.HTTP_400_BAD_REQUEST)

            return Response(status=status.HTTP_200_OK)

        except Exception as e:
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.G_0, e))
            return Response(CustomError.get_full_error_json(CustomError.G_0, e), status=status.HTTP_400_BAD_REQUEST)

    # -----------------------------------------------------------------------------------------------------------------

    @staticmethod
    def handle_get_asset_children(vin, user):
        try:
            children = AssetHelper.get_assets_by_parent(vin, user.db_access)
            all_assets = AssetHelper.get_all_assets(user.db_access)
            context = AssetHelper.get_serializer_context_2(all_assets,user)
            ser = LightAssetModelSerializer(children, many=True, context=context)

            return Response(ser.data, status=status.HTTP_200_OK)

        except Exception as e:
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.G_0, e))
            return Response(CustomError.get_full_error_json(CustomError.G_0, e), status=status.HTTP_400_BAD_REQUEST)

    # -----------------------------------------------------------------------------------------------------------------
    
    @staticmethod
    def handle_set_asset_status(request_data, user):
        try:
            # Check if VIN exists
            if not AssetHelper.asset_exists(request_data.get('VIN'), user.db_access):
                Logger.getLogger().error(CustomError.get_error_dev(CustomError.VDNE_0))
                return Response(CustomError.get_full_error_json(CustomError.VDNE_0), status=status.HTTP_400_BAD_REQUEST)

            # Check if status is valid
            request_data['status'] = str(request_data.get('status')).capitalize()
            if not AssetHelper.validate_asset_status(request_data.get('status')):
                Logger.getLogger().error(CustomError.get_error_dev(CustomError.IS_0))
                return Response(CustomError.get_full_error_json(CustomError.IS_0), status=status.HTTP_400_BAD_REQUEST)

            if not AssetHelper.check_asset_status_active(request_data.get("VIN"), user.db_access):
                Logger.getLogger().error(CustomError.get_error_dev(CustomError.TUF_16,
                                                                   CustomError.get_error_user(CustomError.TUF_16)))
                return Response(CustomError.get_full_error_json(CustomError.TUF_16,
                                                                CustomError.get_error_user(CustomError.TUF_16)),
                                status=status.HTTP_400_BAD_REQUEST)

            # Check if status is different
            asset = AssetHelper.get_asset_by_VIN(request_data.get('VIN'), user.db_access)
            if asset.status == request_data.get('status'):
                return Response(CustomError.get_full_error_json(CustomError.SNN_0), status=status.HTTP_202_ACCEPTED)

            # Update asset status
            update_response = AssetHandler.handle_update_asset(request_data, user)
            if update_response.status_code != status.HTTP_200_OK:
                return update_response

            return Response(status=status.HTTP_202_ACCEPTED)

        except Exception as e:
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.G_0, e))
            return Response(CustomError.get_full_error_json(CustomError.G_0, e), status=status.HTTP_400_BAD_REQUEST)
          
    # ----------------------------------------------------------------------------------------------------------------- 

    @staticmethod
    def handle_get_average_maintenance_cost(user):
        try:
            db_name = user.db_access

            maintenance_ids = MaintenanceRequestModel.objects.using(db_name).values_list('pk', flat=True)
            repair_ids = RepairsModel.objects.using(db_name).values_list('pk', flat=True)

            parts_costs = PartsHelper.get_parts_by_maintenance_and_repair_ids(maintenance_ids, repair_ids, db_name)
            parts_costs_list = list(parts_costs.values('maintenance', 'total_cost'))

            labor_costs = LaborHelper.get_labor_cost_by_maintenance_and_repair_ids(maintenance_ids, repair_ids, db_name)
            labor_costs_list = list(labor_costs.values('maintenance', 'total_cost'))

            total_cost = 0
            num_maintenance_records = 0

            for cost in parts_costs_list:
                maintenance_id = cost['maintenance']
                parts_cost = cost['total_cost']
                total_cost += parts_cost
                num_maintenance_records += 1

            for cost in labor_costs_list:
                maintenance_id = cost['maintenance']
                labor_cost = cost['total_cost']
                total_cost += labor_cost
                num_maintenance_records += 1

            average_cost = total_cost / num_maintenance_records if num_maintenance_records != 0 else 0

            response_data = {
                "total_cost": total_cost,
                "num_maintenance_records": num_maintenance_records,
                "average_cost": average_cost
            }
            
            return Response(response_data, status=status.HTTP_200_OK)

        except Exception as e:
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.G_0, e))
            return Response(CustomError.get_full_error_json(CustomError.G_0, e), status=status.HTTP_400_BAD_REQUEST)
        
    # -----------------------------------------------------------------------------------------------------------------

    @staticmethod
    def handle_get_mean_time_between_failure(user, start_date, end_date):
        try:
            start_date_obj = timezone.make_aware(datetime.strptime(start_date, '%m-%d-%Y'))
            end_date_obj = timezone.make_aware(datetime.strptime(end_date, '%m-%d-%Y'))
            num_days_repairs = (end_date_obj - start_date_obj).days

            repairs_vins = RepairsModel.objects.filter(date_created__range=[start_date_obj, end_date_obj]).values_list('VIN_id', flat=True).distinct()
            accidents_vins = AccidentModel.objects.filter(date_created__range=[start_date_obj, end_date_obj]).values_list('VIN_id', flat=True).distinct()

            total_repair_count = 0
            for vin in repairs_vins:
                repairs_count = RepairsModel.objects.filter(VIN_id=vin, date_created__range=[start_date_obj, end_date_obj]).count()
                total_repair_count += repairs_count

            total_incidence_count = 0
            for vin in accidents_vins:
                accidents_count = AccidentModel.objects.filter(VIN_id=vin, date_created__range=[start_date_obj, end_date_obj]).count()
                total_incidence_count += accidents_count

            total_count = total_repair_count + total_incidence_count

            mean_days_between_failures = num_days_repairs / total_count if total_count > 0 else 0

            response_data = {
                'num_days': num_days_repairs,
                'total_repair_count': total_repair_count,
                'total_incidence_count': total_incidence_count,
                'mean_days_between_failures': mean_days_between_failures
            }

            return Response(response_data, status=status.HTTP_200_OK)
        except Exception as e:
            logging.getLogger().error(CustomError.get_error_dev(CustomError.G_0, e))
            error_response = CustomError.get_full_error_json(CustomError.G_0, e)
            return Response(error_response, status=status.HTTP_400_BAD_REQUEST)
            
    # -----------------------------------------------------------------------------------------------------------------

    @staticmethod        
    def handle_get_average_maintenance_cost_per_mileage(start_date, end_date, user):
        try:
            db_name = user.db_access

            # Convert start_date and end_date to datetime objects
            start_date = datetime.strptime(start_date, "%Y-%m-%d")
            end_date = datetime.strptime(end_date, "%Y-%m-%d")

            # Convert start_date and end_date to aware datetime objects
            start_date = timezone.make_aware(start_date, timezone.get_default_timezone())
            end_date = timezone.make_aware(end_date, timezone.get_default_timezone())

            # Retrieve VINs based on maintenance requests created within the specified date range
            maintenance_vins = MaintenanceRequestModel.objects.using(db_name).filter(
                date_created__gte=start_date, date_created__lte=end_date
            ).values_list('VIN_id', flat=True)

            # Retrieve VINs based on repairs created within the specified date range
            repair_vins = RepairsModel.objects.using(db_name).filter(
                date_created__gte=start_date, date_created__lte=end_date
            ).values_list('VIN_id', flat=True)

            # Get the intersection of VINs from maintenance requests and repairs
            vins = set(maintenance_vins) & set(repair_vins)

            # Convert the set to a list
            vins = list(vins)

            total_cost = 0
            total_mileage = 0

            for vin in vins:
                # Retrieve maintenance IDs created within the specified date range based on VIN ID
                maintenance_ids = MaintenanceRequestModel.objects.using(db_name).filter(
                    VIN_id=vin, date_created__gte=start_date, date_created__lte=end_date
                ).values_list('pk', flat=True)

                # Retrieve repair IDs created within the specified date range based on VIN ID
                repair_ids = RepairsModel.objects.using(db_name).filter(
                    VIN_id=vin, date_created__gte=start_date, date_created__lte=end_date
                ).values_list('pk', flat=True)

                # Convert the querysets to lists
                maintenance_ids = list(maintenance_ids)
                repair_ids = list(repair_ids)

                parts_costs = PartsHelper.get_parts_by_maintenance_and_repair_ids(maintenance_ids, repair_ids, db_name)
                parts_costs_list = list(parts_costs.values('issue__repair_id', 'maintenance', 'total_cost', 'taxes'))

                labor_costs = LaborHelper.get_labor_cost_by_maintenance_and_repair_ids(maintenance_ids, repair_ids, db_name)
                labor_costs_list = list(labor_costs.values('issue__repair_id', 'maintenance', 'total_cost', 'taxes'))

                for cost in parts_costs_list:
                    maintenance_id = cost['maintenance']
                    parts_cost = cost['total_cost']
                    total_cost += parts_cost

                for cost in labor_costs_list:
                    maintenance_id = cost['maintenance']
                    labor_cost = cost['total_cost']
                    total_cost += labor_cost

                # Calculate the total mileage based on the maintenance IDs
                maintenance_records = MaintenanceRequestModel.objects.using(db_name).filter(
                    pk__in=maintenance_ids, date_created__gte=start_date, date_created__lte=end_date
                )
                for record in maintenance_records:
                    total_mileage += record.mileage

            average_cost_per_mileage = total_cost / total_mileage if total_mileage != 0 else 0

            response_data = {
                "start_date": start_date.strftime("%Y-%m-%d"),
                "end_date": end_date.strftime("%Y-%m-%d"),
                "total_cost": total_cost,
                "total_mileage": total_mileage,
                "average_cost_per_mileage": average_cost_per_mileage
            }

            return Response(response_data, status=status.HTTP_200_OK)

        except Exception as e:
            logging.exception("Exception occurred: %s", e)
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.G_0, e))
            return Response(CustomError.get_full_error_json(CustomError.G_0, e), status=status.HTTP_400_BAD_REQUEST)
          
    # -----------------------------------------------------------------------------------------------------------------

    @staticmethod
    def handle_get_average_cost_per_unit(start_date, end_date, user):
        try:
            start_date = timezone.make_aware(datetime.strptime(start_date, "%Y-%m-%d"), timezone.get_current_timezone())
            end_date = timezone.make_aware(datetime.strptime(end_date, "%Y-%m-%d"), timezone.get_current_timezone())
            asset_histories = AssetModelHistory.objects.using(user.db_access).filter(date__range=[start_date, end_date])

            total_cost = sum(asset_history.total_cost for asset_history in asset_histories)
            total_mileage = sum(asset_history.mileage for asset_history in asset_histories)

            average_cost_per_unit = 0

            if total_mileage != 0:
                average_cost_per_unit = total_cost / total_mileage

            # Calculate daily, weekly, monthly, and yearly costs
            duration = (end_date - start_date).days

            daily_start_date = start_date
            daily_costs = []
            daily_data = []

            while daily_start_date <= end_date:
                daily_cost = sum(asset_history.total_cost for asset_history in asset_histories.filter(date__date=daily_start_date.date()))
                if daily_cost != 0:
                    daily_costs.append(daily_cost)
                    daily_data.append({
                        "date": daily_start_date.strftime("%Y-%m-%d"),
                        "cost": daily_cost
                    })
                daily_start_date += timedelta(days=1)

            weekly_start_date = start_date
            weekly_end_date = start_date + timedelta(days=6)
            weekly_costs = []
            weekly_data = []

            while weekly_end_date <= end_date:
                weekly_cost = sum(asset_history.total_cost for asset_history in asset_histories.filter(date__range=[weekly_start_date, weekly_end_date]))
                if weekly_cost != 0:
                    weekly_costs.append(weekly_cost)
                    weekly_data.append({
                        "start_date": weekly_start_date.strftime("%Y-%m-%d"),
                        "end_date": weekly_end_date.strftime("%Y-%m-%d"),
                        "cost": weekly_cost
                    })
                weekly_start_date += timedelta(days=7)
                weekly_end_date += timedelta(days=7)

            monthly_start_date = start_date.replace(day=1)
            monthly_end_date = (monthly_start_date + timedelta(days=32)).replace(day=1) - timedelta(days=1)
            monthly_costs = []
            monthly_data = []

            while monthly_end_date <= end_date:
                monthly_cost = sum(asset_history.total_cost for asset_history in asset_histories.filter(date__range=[monthly_start_date, monthly_end_date]))
                if monthly_cost != 0:
                    monthly_costs.append(monthly_cost)
                    monthly_data.append({
                        "start_date": monthly_start_date.strftime("%Y-%m-%d"),
                        "end_date": monthly_end_date.strftime("%Y-%m-%d"),
                        "cost": monthly_cost
                    })
                monthly_start_date = monthly_end_date + timedelta(days=1)
                monthly_end_date = (monthly_start_date + timedelta(days=32)).replace(day=1) - timedelta(days=1)

            yearly_start_date = start_date.replace(month=1, day=1)
            yearly_end_date = yearly_start_date.replace(month=12, day=31)
            yearly_costs = []
            yearly_data = []

            while yearly_end_date <= end_date:
                yearly_cost = sum(asset_history.total_cost for asset_history in asset_histories.filter(date__range=[yearly_start_date, yearly_end_date]))
                if yearly_cost != 0:
                    yearly_costs.append(yearly_cost)
                    yearly_data.append({
                        "start_date": yearly_start_date.strftime("%Y-%m-%d"),
                        "end_date": yearly_end_date.strftime("%Y-%m-%d"),
                        "cost": yearly_cost
                    })
                yearly_start_date = yearly_end_date + timedelta(days=1)
                yearly_end_date = yearly_start_date.replace(month=12, day=31)

            return Response({
                "average_cost_per_unit": average_cost_per_unit,
                "daily_costs": daily_data,
                "weekly_costs": weekly_data,
                "monthly_costs": monthly_data,
                "yearly_costs": yearly_data
            }, status=status.HTTP_200_OK)
        except Exception as e:
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.IT_0))
            return Response(CustomError.get_full_error_json(CustomError.IT_0), status=status.HTTP_400_BAD_REQUEST)

    # -----------------------------------------------------------------------------------------------------------------

    @staticmethod
    def handle_get_annual_report(vin, user):
        try:
            all_files = AssetHelper.get_annual_report_by_vin(vin, user.db_access).order_by('-file_id')
            
            context={
                "report_items":AnnualReport.objects.using(user.db_access).filter(VIN=vin)
            }
            
            ser = AssetFileWithReportsSerializer(all_files, many=True, context=context)
            return Response(AssetHelper.secure_asset_file_ser_urls(ser.data, user.db_access), status=status.HTTP_200_OK)

        except Exception as e:

            Logger.getLogger().error(CustomError.get_error_dev(CustomError.G_0, e))
            return Response(CustomError.get_full_error_json(CustomError.G_0, e), status=status.HTTP_400_BAD_REQUEST)  

    '''
    input:
        request: {
            year: int
        }
    
    '''
    @staticmethod
    def handle_get_annual_report_kpi(year, user):
        try:
            if int(year) < 1900 or int(year) > int(datetime.today().strftime("%Y")):
                raise Exception("Year is invalid.")
            date_format = "%Y-%m-%d"
            year_start = datetime.strptime(year + "-01-01", date_format).date()
            year_end = datetime.strptime(year + "-12-31", date_format).date()
            db_name = user.db_access
            all_vessel_vins = AssetHelper.select_related_to_asset(AssetModel.objects.using(db_name).filter(status="Active").all())
            total_expected_annual_report_count = len(all_vessel_vins)
            unfinished_annual_report_count = total_expected_annual_report_count
            annual_report_finished_vin_list = []
            annual_report_unfinished_vin_list = []
            for vin in all_vessel_vins:
                annual_reports = AssetHelper.get_annual_report_by_vin(vin, db_name).order_by('-file_id')
                annual_report_submitted = False
                for report in annual_reports:
                    if year_start < report.date_created < year_end:
                        annual_report_submitted = True
                        unfinished_annual_report_count -= 1
                        break
                if annual_report_submitted:
                    annual_report_finished_vin_list.append(vin)
                else:
                    annual_report_unfinished_vin_list.append(vin)

            submitted_annual_report_count = total_expected_annual_report_count - unfinished_annual_report_count
            annual_report_unfinished_vins = AssetHelper.select_related_to_asset(
                AssetHelper.get_assets_not_in_VIN_list_and_active(annual_report_finished_vin_list, db_name))
            annual_report_finished_vin_list = AssetHelper.select_related_to_asset(
                AssetHelper.get_assets_not_in_VIN_list_and_active(annual_report_unfinished_vin_list, db_name))
            unfinished_serializer = LightAssetModelSerializer(annual_report_unfinished_vins, many=True)
            finished_serializer = LightAssetModelSerializer(annual_report_finished_vin_list, many=True)
            response_data = {
                "total_expected_annual_report_count": total_expected_annual_report_count,
                "submitted_annual_report_count": submitted_annual_report_count,
                "unfinished_annual_report_count": unfinished_annual_report_count,
                "list_of_annual_report_unfinished_vins": unfinished_serializer.data,
                "list_of_annual_report_finished_vins": finished_serializer.data,
            }

            return Response(response_data, status=status.HTTP_200_OK)
        except Exception as e:
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.G_0, e))
            return Response(CustomError.get_full_error_json(CustomError.G_0, e), status=status.HTTP_400_BAD_REQUEST)

    @staticmethod
    def handle_add_annual_report(request, vin):
        try:
            if not AssetHelper.check_asset_status_active(vin, request.user.db_access):
                Logger.getLogger().error(CustomError.get_error_dev(CustomError.TUF_16,
                                                                   CustomError.get_error_user(CustomError.TUF_16)))
                return Response(CustomError.get_full_error_json(CustomError.TUF_16,
                                                                CustomError.get_error_user(CustomError.TUF_16)),
                                status=status.HTTP_400_BAD_REQUEST)

            data = request.POST.get('data')
            if data:
                data = HelperMethods.json_str_to_dict(data)
            
            expiration_date = data.get("expiration_date") if data else None
            files = request.FILES.getlist('files')
            if len(files)!=1:
                print("violating assumption of precisely one file")
                return Response(CustomError.I_0,status.HTTP_400_BAD_REQUEST)

            valid_issue_file_types = ["application/pdf"]
            if not FileHelper.verify_files_are_accepted_types(files, valid_issue_file_types):
                Logger.getLogger().error(CustomError.get_error_dev(CustomError.FUF_1, "File(s) not pdf."))
                return Response(CustomError.get_full_error_json(CustomError.FUF_1, "File(s) not pdf."), status=status.HTTP_400_BAD_REQUEST)

            # ------------ Upload files to blob --------------
            detailed_user = UserHelper.get_detailed_user_obj(request.user.email, request.user.db_access)
            company_name = detailed_user.company.company_name
            file_prefix = str(AssetFile.annual_report) + "_" + str(vin) + "_"
            file_status, file_infos = BlobStorageHelper.write_files_to_blob(files, "asset/annual_report", file_prefix, company_name, request.user.db_access)
            if(not file_status):
                Logger.getLogger().error(CustomError.get_error_dev(CustomError.FUF_0))
                return Response(CustomError.get_full_error_json(CustomError.FUF_0), status=status.HTTP_400_BAD_REQUEST)

            # ----------- Upload file urls to DB --------------
            asset_obj = AssetHelper.get_asset_by_VIN(vin, request.user.db_access)
            
            file_record=AssetUpdater.construct_asset_file_instance(asset_obj,file_infos[0],AssetFile.annual_report,expiration_date,detailed_user)
            file_record.save()
            
            report_data=data.get("annual_report") if data else None
            
            if not report_data:
                # TODO: disabled to not break FE, but this should be mandatory once FE is updated
                # return Response(CustomError.I_0,status.HTTP_400_BAD_REQUEST)
                print("no data.annual_report given, this will be an error soon")
                pass
            else:
                report_data["VIN"]=asset_obj.VIN
                report_data["file"]=file_record.file_id
                
                report_serializer=AnnualReportSerializer(data=report_data)
                if not report_serializer.is_valid():
                    print(report_serializer.errors)
                    return Response(CustomError.I_0,status.HTTP_400_BAD_REQUEST)
                
                report_serializer.save()
            
            # Apply to similar assets
            apply_to_similar_type = request.POST.get('apply_to_similar_type')
            if apply_to_similar_type:
                similar_assets = AssetHelper.get_similar_assets_make_model(vin, request.user.db_access)
                for similar_asset in similar_assets:
                    file_record_response = AssetUpdater.create_asset_file_records(similar_asset, file_infos, AssetFile.annual_report, expiration_date, detailed_user, request.user.db_access)
                    if file_record_response.status_code != status.HTTP_201_CREATED:
                        return file_record_response

        except Exception as e:
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.G_0, e))
            return Response(CustomError.get_full_error_json(CustomError.G_0, e), status=status.HTTP_400_BAD_REQUEST)

        return Response(status=status.HTTP_200_OK)

    # -----------------------------------------------------------------------------------------------------------------

    @staticmethod
    def handle_get_assets_for_clients(client_names):
        try:
            client_db_access_dict = VendorOpsHelper.get_client_db_access_dict()
            client_assets_output = {}

            for client_name in client_names:
                db_access = client_db_access_dict.get(client_name)
                asset_qs = AssetHelper.get_all_assets(db_access)
                client_assets_output[client_name] = asset_qs.values()

            return Response(client_assets_output, status=status.HTTP_200_OK)

        except Exception as e:
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.G_0, e))
            return Response(CustomError.get_full_error_json(CustomError.G_0, e), status=status.HTTP_400_BAD_REQUEST)

    # -----------------------------------------------------------------------------------------------------------------

    @staticmethod
    def handle_get_upcomming_end_of_life(user): 
        try:
            vins = []
            qs = AssetModel.objects.using(user.db_access).exclude(date_in_service__isnull=True)
            for asset in qs: 
                if asset.is_near_end_of_life(): 
                    vins.append(asset.VIN)

            qs = AssetHelper.get_assets_from_VIN_list(vins, user.db_access)
            ser = AssetModelSerializer(qs, many=True)
            return Response(ser.data, status=status.HTTP_200_OK)
        except Exception as e:
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.G_0, e))
            return Response(CustomError.get_full_error_json(CustomError.G_0, e), status=status.HTTP_400_BAD_REQUEST)   
    
    @staticmethod
    def handle_get_lifecycle_disposal_schedule_kpi(user):
        try:
            db_name = user.db_access
            current_date = timezone.now().date()
            asset_qs = AssetHelper.get_all_assets(db_name)
            all_remaining_lifespan_years = {}
            still_useful_vins = []
            for asset in asset_qs:
                # Check if the asset has a date of manufacture
                if asset.date_of_manufacture:
                    asset_lifespan = asset.lifespan_years
                    manufacture_year = asset.date_of_manufacture.year
                    end_of_life_date = asset.date_of_manufacture.replace(year=manufacture_year + asset_lifespan)

                    # Check if the asset still have years of useful life.
                    # 365.2425 => average amount of days in a year.
                    if end_of_life_date > current_date:
                        remaining_lifespan_days = (end_of_life_date - current_date).days
                        all_remaining_lifespan_years[asset.VIN] = ceil(remaining_lifespan_days / 365.2425)
                        still_useful_vins.append(asset.VIN)

            ser = AssetModelSerializer(AssetHelper.get_assets_from_VIN_list(still_useful_vins, db_name),
                                       many=True)

            return Response({'assets': ser.data, 'remaining_years': all_remaining_lifespan_years}, status=status.HTTP_200_OK)
        except Exception as e:
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.G_0, e))
            return Response(CustomError.get_full_error_json(CustomError.G_0, e), status=status.HTTP_400_BAD_REQUEST)

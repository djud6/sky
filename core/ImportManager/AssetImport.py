from rest_framework.response import Response
from rest_framework import status
from django.core.exceptions import ObjectDoesNotExist
import csv
from api.Models.asset_model import AssetModel
from api.Models.asset_model_history import AssetModelHistory
from api.Models.equipment_type import EquipmentTypeModel
from api.Models.locations import LocationModel
from api.Models.business_unit import BusinessUnitModel
from django.db.utils import IntegrityError
from core.Helper import HelperMethods
from ..FileManager.FileHelper import FileHelper
from ..AssetManager.AssetUpdater import AssetUpdater
from ..UserManager.UserHelper import UserHelper
from ..HistoryManager.AssetHistory import AssetHistory
import zipfile
import io
import logging
from datetime import datetime
from GSE_Backend.errors.ErrorDictionary import CustomError

# This class has the methods required to import asset data into the database

class Logger():
    @staticmethod
    def getLogger():
        return logging.getLogger(__name__)

class AssetImport():

    db_name = ""
    VinsInDB = None
    EquipmentTypeQS = None
    EquipmentTypeIDs = None
    LocationQS = None
    LocationCodes = None
    LocationIDs = None
    BusinessUnitQS = None
    BusinessUnitNames = None
    BusinessUnitIDs = None

    # Required fields
    assetModelRequired = {
        "VIN": 0,
        "equipment_type_id": 0,
        "company": 0,
        "department": 0,
        "location": 0,
        "fuel": 0
    }

    # Optional fields
    assetModelOptional = {
        "date_of_manufacture": 0,
        "date_in_service": 0,
        "total_cost": 0,
        "currency": 0,
        "hours": 0,
        "mileage": 0,
        "hours_or_mileage": 0,
        "company": 0,
        "jde_department": 0,
        "aircraft_compatability": 0,
        "unit_number": 0,
        "license_plate": 0,
        "fuel_tag_number": 0,
        "fire_extinguisher_quantity": 0,
        "fire_extinguisher_inspection_date": 0,
        "path": 0,
        "replacement_hours": 0,
        "replacement_mileage": 0,
        "load_capacity": 0,
        "load_capacity_unit": 0,
        "insurance_renewal": 0,
        "registration_renewal": 0,
        "engine": 0
    }


    @staticmethod
    def import_asset_csv(parsed_data, user):
        try:
            asset_entries = []
            asset_history_entries = []
            detailed_user = UserHelper.get_detailed_user_obj(user.email, user.db_access)
            count = 1

            for asset_row in parsed_data:
                asset_row["VIN"] = asset_row.get("VIN").strip()
                if not AssetModel.objects.using(user.db_access).filter(VIN=asset_row.get("VIN")).exists():
                    print(str(count) + " Creating asset entry (VIN: " + str(asset_row.get("VIN")) + ")")
                    entry, entry_response = AssetUpdater.create_asset_entry(asset_row, detailed_user, user.db_access)
                    if entry_response.status_code != status.HTTP_201_CREATED:
                        if entry_response.status_code == status.HTTP_100_CONTINUE:
                            break
                        return entry_response
                    entry, update_reponse = AssetUpdater.update_asset_optional_fields(entry, asset_row, user)
                    if update_reponse.status_code != status.HTTP_200_OK:
                        return update_reponse
                    asset_entries.append(entry)
                    asset_history_entries.append(AssetHistory.generate_asset_history_entry(entry))
                    print("done...")

                count += 1

            print("Attempting bulk-create")
            AssetModel.objects.using(user.db_access).bulk_create(asset_entries)
            AssetModelHistory.objects.using(user.db_access).bulk_create(asset_history_entries)
            print("done...")
            return Response(status=status.HTTP_201_CREATED)

        except Exception as e:
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.CSVUF_0, e))
            return Response(CustomError.get_full_error_json(CustomError.CSVUF_0, "Line " + str(count) + " " + str(e)), status=status.HTTP_400_BAD_REQUEST)



    @staticmethod
    def import_asset_csv_old(parsed_data, file_name, user):    

        # ====================== Update Globals =====================
        global db_name
        global AssetQS
        global VinsInDB
        global EquipmentTypeQS
        global EquipmentTypeIDs
        global LocationQS
        global LocationCodes
        global LocationIDs
        global BusinessUnitQS
        global BusinessUnitNames
        global BusinessUnitIDs
        db_name = user.db_access
        VinsInDB = list(AssetModel.objects.using(db_name).values_list('VIN', flat=True))
        EquipmentTypeQS = list(EquipmentTypeModel.objects.using(db_name).all())
        EquipmentTypeIDs = list(EquipmentTypeModel.objects.using(db_name).values_list('equipment_type_id', flat=True))
        LocationQS = list(LocationModel.objects.using(db_name).all())
        LocationCodes = list(LocationModel.objects.using(db_name).values_list('location_code', flat=True))
        LocationIDs = list(LocationModel.objects.using(db_name).values_list('location_id', flat=True))
        BusinessUnitQS = list(BusinessUnitModel.objects.using(db_name).all())
        BusinessUnitNames = list(BusinessUnitModel.objects.using(db_name).values_list('name', flat=True))
        BusinessUnitIDs = list(BusinessUnitModel.objects.using(db_name).values_list('business_unit_id', flat=True))
        # ============================================================

        # ===================== Set up file names ====================
        invalidFileName = file_name.replace(".csv", "(invalid).csv")
        duplicateFileName = file_name.replace(".csv", "(duplicate).csv")
        zipName = file_name.replace("csv", "zip")
        # ============================================================

        # ================= Creating main loop lists =================
        validEntries = list() # Will contain all valid entries which will be inserted into DB
        invalidRows = list() # Will contain all invalid rows and will be used to construct the invalid rows CSV
        duplicateRows = list() # Will contain all duplicate rows and will be used to construct the duplicate rows CSV
        duplicateVINS = list() # Will contain one of each duplicate VIN and will be used to make DB deletions
        dbDuplicatesList = list() # Will hold all rows from DB for which duplicates were found in the insert CSV
        filesToZip = list() # Will hold any files that need to be returned to user
        prospectVINs = list() # Will hold VINs for rows that are valid and might be inserted into db
        prospectRows = list() # Will hold rows that are valid and might be inserted into db
        # ============================================================

        # Add header row to invalid rows so its CSV has them
        headerRowList = parsed_data.header
        invalidRows.append(headerRowList)

        print(str(len(AssetImport.assetModelRequired)))
        # Synchronise the order of dictionary values to match order of input file's headers (This is only used for printing test functions)
        try:
            AssetImport.assetModelRequired = HelperMethods.MapCSVHeaders(AssetImport.assetModelRequired, headerRowList)
            AssetImport.assetModelOptional = HelperMethods.MapCSVHeaders(AssetImport.assetModelOptional, headerRowList)
        except Exception as e:
            print("Dictionary synchronization has failed due to: " + str(e))
        print(str(len(AssetImport.assetModelRequired)))

        # Get DetailedUser
        detailed_user = UserHelper.get_detailed_user_obj(user.email, db_name)

        # ============================================== Main Logic Loop ==============================================        
        for row in parsed_data:
                    
            vin  = row.get('VIN').strip()
            # If row has all required fields
            if(AssetImport.ValidateRow(row)):
                print("******ROW IS VALID******")
                #AssetImport.TestImportAssetRow(HelperMethods.GenCSVRowFromOrderedRow(parsed_data.header, row))
                print("VIN: " + vin)

                if(vin.lower() in (string.lower().strip() for string in VinsInDB) or vin.lower() in (string.lower().strip() for string in prospectVINs)):
                    print("DUPLICATE")
                    duplicateRows.append(HelperMethods.GenCSVRowFromOrderedRow(parsed_data.header, row))
                    if(vin not in duplicateVINS):
                        duplicateVINS.append(vin)
                else:
                    print("UNIQUE")
                    prospectVINs.append(vin)
                    prospectRows.append(row)

                #print("----------------------------------------------------------------")
                
            # If row does not have all required fields
            else:
                print("******ROW IS NOT VALID******")
                print("VIN: " + vin)
                print("----------------------------------------------------------------")
                invalidRows.append(HelperMethods.GenCSVRowFromOrderedRow(parsed_data.header, row))

        # =============================================================================================================

        # ================= Extracting duplicates from db =================
        try:
            print("-----------------------")
            print("Starting duplicate extraction from DB (Items: " + str(len(duplicateVINS)) + ")...")
            start = datetime.now()
            dbDuplicatesQS = AssetModel.objects.using(db_name).filter(pk__in=[vin for vin in duplicateVINS]).values_list(*headerRowList)
            duplicateRows += AssetImport.EditDuplicatesFromDB(dbDuplicatesQS)
            duplicateRows = sorted(duplicateRows, key=lambda x: str(x[0]))
            duplicateRows.insert(0, headerRowList)
            finish = datetime.now()
            print("DB extraction took: " + str(finish - start))
        except Exception as e:
            print("Duplicate extraction from DB has failed due to: " + str(e))
            Logger.getLogger().error(e)
        #==================================================================

        #============== Extracting duplicates from prospects ==============
        try:
            print("-----------------------")
            print("Starting duplicate extraction from prospects operations (Items: " + str(len(duplicateRows)) + ")...")
            start = datetime.now()
            duplicateRows, prospectRows = AssetImport.ExtractDuplicatesFromProspects(duplicateVINS, duplicateRows, prospectVINs, prospectRows, parsed_data)
            finish = datetime.now()
            print("Prospects extraction took: " + str(finish - start))
        except Exception as e:
            print("Duplicate extraction from prospects has failed due to: " + str(e))
            Logger.getLogger().error(e)
        #==================================================================

        #====================== Generating entries ========================
        try:
            print("-----------------------")
            print("Starting entries generation operations (Items: " + str(len(prospectRows)) + ")...")
            start = datetime.now()
            validEntries, invalidEntries = AssetImport.create_asset_model_entries(parsed_data, prospectRows, detailed_user)
            invalidRows += invalidEntries
            finish = datetime.now()
            print("Entries took: " + str(finish - start))
        except Exception as e:
            print("Entry generation has failed due to: " + str(e))
            Logger.getLogger().error(e)
        #==================================================================

        print("-----------------------")
        print("LISTING DUPLICATE VINS:")
        for vin in duplicateVINS:
            print(vin)
        print("-----------------------")

        print("LISTING NON VALID ROWS' VINS:")
        for row in invalidRows:
            print(row[AssetImport.assetModelRequired["VIN"]])

        #======================== DB Insertion ============================
        try:
            insertionSuccess = True
            print("-----------------------")
            print("Starting db insertion operations (Items: " + str(len(validEntries)) + ")...")
            start = datetime.now()
            #AssetModel.objects.using(db_name).bulk_create(validEntries)
            finish = datetime.now()
            print("Insertion took: " + str(finish - start))
        except Exception as e:
            insertionSuccess = False
            print("Insertion has failed due to: " + str(e))
            Logger.getLogger().error(e)
        #==================================================================

        # If invalid/duplicate rows are found in insertion then send back appropriate CSVs to client
        if(len(invalidRows) > 1 or len(duplicateRows) > 1):
            print("-----------------------------------")
            print("Starting zip operations (Items: " + str(len(invalidRows) + len(duplicateRows)) + ")...")
            start = datetime.now()

            invalidCSVFile, invalidCSVFileStatus = FileHelper.GenCSVFile(invalidRows, invalidFileName)
            duplicateCSVFile, duplicateCSVFileStatus = FileHelper.GenCSVFile(duplicateRows, duplicateFileName)
            filesToZip.append(invalidCSVFile)
            filesToZip.append(duplicateCSVFile)

            zipFile, zipStatus = FileHelper.GenZipFile(filesToZip, zipName)

            finish = datetime.now()
            print("Zip took: " + str(finish - start))

            # If invalid csv, duplicate csv, and zip are created successfully: make db deletions.
            if(invalidCSVFileStatus and duplicateCSVFileStatus and zipStatus):
                print("-----------------------------------")
                print("Starting db duplicate deletion operations (Items: " + str(len(duplicateVINS)) + ")...")
                start = datetime.now()

                AssetImport.MakeDBDeletions(duplicateVINS)

                finish = datetime.now()
                print("Deletions took: " + str(finish - start))
                print("-----------------------------------")

            return zipFile, insertionSuccess

        # If DB insertion went perfectly then we have nothing to send back
        else:
            return None, insertionSuccess

    # --------------------------------- ImportAssetCSV helper methods ---------------------------------

    # Extracts rows from prospectRows that were later found to be duplicates, and appends them to the duplicateRows lsit
    @staticmethod
    def ExtractDuplicatesFromProspects(duplicateVINS, duplicateRows, prospectVINs, prospectRows, parsed_data):
        for duplicateVIN in duplicateVINS:
            if(duplicateVIN.lower() in (string.lower() for string in prospectVINs)):
                try:
                    # Since prospectVINs and prospectRows are synchronised, we can get the right index for the latter by checking the former.
                    index = prospectVINs.index(duplicateVIN)
                    # We pop the duplicate row and also convert it to the string list format we use for duplicate rows
                    extractedRow = HelperMethods.GenCSVRowFromOrderedRow(parsed_data.header, prospectRows.pop(index))
                    # Pop from prospectVINs aswell to keep it synchronized with prospectRows
                    prospectVINs.pop(index)
                    # Add the extracted row to duplicates
                    duplicateRows.append(extractedRow)
                except Exception:
                    # This will execute if input csv contains more than 2 of the same VIN
                    pass

        return duplicateRows, prospectRows

    # This method takes all extracted rows from DB which were found to have duplicates in the input CSV
    # and substitutes location_id for location_code & business_id for business_name.
    @staticmethod
    def EditDuplicatesFromDB(dbDuplicatesQS):
        dbDuplicatesList = list()
        for tupleRow in dbDuplicatesQS:
            listRow = list(tupleRow)
            # assetModelRequired/Optional's values are synchronised to headerRowList 
            # so we can use them here as headerRowList is also used to get dbDuplicatesQS
            locationCodeIndex = LocationIDs.index(listRow[AssetImport.assetModelRequired["location"]])
            businessUnitNameIndex = BusinessUnitIDs.index(listRow[AssetImport.assetModelRequired["department"]])
            listRow[AssetImport.assetModelRequired["location"]] = LocationCodes[locationCodeIndex]
            listRow[AssetImport.assetModelRequired["department"]] = BusinessUnitNames[businessUnitNameIndex]
            dbDuplicatesList.append(listRow)
        return dbDuplicatesList

    @staticmethod
    def ValidateRow(row):
        for key, value in AssetImport.assetModelRequired.items():
            if not row.get(key):
                return False
        return True

    @staticmethod
    def MakeDBDeletions(vins):
        objectsToDelete = AssetModel.objects.using(db_name).filter(pk__in=[vin for vin in vins])
        objectsToDelete.delete()

    @staticmethod
    def GetEquipmentModelInstance(equipment_type):
        index = EquipmentTypeIDs.index(int(equipment_type))
        print(EquipmentTypeQS[index])
        return EquipmentTypeQS[index]

    @staticmethod
    def GetLocationInstance(_location_code):
        index = LocationCodes.index(_location_code)
        print(LocationQS[index])
        return LocationQS[index]

    @staticmethod
    def GetBusinessModelInstance(business_unit_name):
        index = BusinessUnitNames.index(business_unit_name)
        print(BusinessUnitQS[index])
        return BusinessUnitQS[index]

    # Creates db entries based a list of rows
    @staticmethod
    def create_asset_model_entries(parsed_data, prospectRows, detailed_user):
        validEntries = list()
        invalidEntries = list()
        for prospectRow in prospectRows:
            entry = AssetUpdater.create_asset_entry(prospectRow, detailed_user, db_name)
            entryStatus = True
            if(entryStatus):
                print("Entry was valid")
                validEntries.append(entry)
            else:
                print("Entry was no valid")
                invalidEntries.append(HelperMethods.GenCSVRowFromOrderedRow(parsed_data.header, prospectRow))
        return validEntries, invalidEntries

    #str(AssetImport.GetEquipmentModelInstance(row.get("equipment_type"))).strip()

    # ---------------------------------------- TESTING METHODS ---------------------------------------

    @staticmethod
    def TestImportAssetRows(rows):
        for row in rows:
            try:
                AssetImport.TestImportAssetRow(row)
                print("")
            except Exception as e:
                print("-----------------")
                print(e)
                print("-----------------")

    @staticmethod
    def TestImportAssetRow(row):
        print("VIN: " + row[AssetImport.assetModelRequired.get("VIN")])
        print("date_of_manufacture: " + row[AssetImport.assetModelRequired.get("date_of_manufacture")])
        print("department: " + row[AssetImport.assetModelRequired.get("department")])
        print("Location: " + row[AssetImport.assetModelRequired.get("Location_id")])
        print("mileage: " + row[AssetImport.assetModelRequired.get("mileage")])
        print("date_in_service: " + row[AssetImport.assetModelRequired.get("date_in_service")])
        print("equipment_type: " + row[AssetImport.assetModelOptional.get("equipment_type")])
        print("company: " + row[AssetImport.assetModelOptional.get("company")])
        print("jde_department: " + row[AssetImport.assetModelOptional.get("jde_department")])
        print("aircraft_compatability: " + row[AssetImport.assetModelOptional.get("aircraft_compatability")])
        print("unit_number: " + row[AssetImport.assetModelOptional.get("unit_number")])
        print("license_plate: " + row[AssetImport.assetModelOptional.get("license_plate")])
        print("fire_extinguisher_quantity: " + row[AssetImport.assetModelOptional.get("fire_extinguisher_quantity")])
        print("fire_extinguisher_inspection_date: " + row[AssetImport.assetModelOptional.get("fire_extinguisher_inspection_date")])
        print("Item_Type: " + row[AssetImport.assetModelOptional.get("Item_Type")])
        print("path: " + row[AssetImport.assetModelOptional.get("path")])
        print("status: " + row[AssetImport.assetModelOptional.get("status")])
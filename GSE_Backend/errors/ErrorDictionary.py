from .Error import Error

class CustomError:

    G_0 = "G-0" # Something went wrong.
    S_0 = "S-0" # Serializer error.
    I_0 = "I-0" # Input error.
    I_1 = "I-1" # Missing/invalid inputs for user creation.
    IL_0 = "IL-0" # Invalid Login.
    IL_1 = "IL-1" # Wrong email for login.
    IL_2 = "IL-2" # User has been deactivated.
    IE_0 = "IE-0" # Invalid email address.
    IE_1 = "IE-1" # The email address is already in use.
    IP_0 = "IP-0" # Invalid password (shorter than 8 chars)
    IP_1 = "IP-1" # Invalid password (no numbers used)
    IP_2 = "IP-2" # Invalid password (no capitals used)
    IP_3 = "IP-3" # Invalid password (longer than 32 chars)
    AS_0 = "AS-0" # Agreement status has not changed.
    IT_0 = "IT-0" # Invalid token
    IS_0 = "IS-0" # Invalid status
    MEV_0 = "MEV-0" # Missing environamental variable.
    WFF_0 = "WFF-0" # Writing file to disc failed.
    CSVF_0 = "CSVF-0" # Failed to generate in memory CSV.
    MTOA_0 = "MTOA-0" # More than one asset was found.
    AUET_0 = "AUET-0" # Asset unknown equipment type.
    ACF_0 = "ACF-0" # Asset creation failed.
    ACF_2 = "ACF-2" # Asset with that VIN already exists in the system.
    TUF_0 = "TUF-0" # Parts update failed
    TUF_1 = "TUF-1" # Labor Cost update failed
    TUF_2 = "TUF-2" # Asset update failed
    TUF_3 = "TUF-3" # Repair update failed
    TUF_4 = "TUF-4" # Maintenance update failed
    TUF_5 = "TUF-5" # Accident update failed
    TUF_6 = "TUF-6" # Disposal Cost update failed
    TUF_7 = "TUF-7" # Asset request update failed
    TUF_8 = "TUF-8" # Issue update failed
    TUF_9 = "TUF-9" # Transfer update failed
    TUF_10 = "TUF-10" # Daily Operator Check update failed
    TUF_11 = "TUF-11" # Equipment type update failed
    TUF_12 = "TUF-12" # Asset type update failed
    TUF_13 = "TUF-13" # Asset type checks update failed
    TUF_14 = "TUF-14" # Pricing rates update failed
    TUF_15 = "TUF-15" # Notification config update failed
    TUF_16 = "TUF-16" # Asset update failed due to inoperativeness or disposal
    AUMF_0 = "AUMF-0" # Asset update has failed due to invalid mileage. Mileage value too low.
    AUMF_1 = "AUMF-1" # Asset update has failed due to invalid mileage. Mileage value too high.
    AUHF_0 = "AUHF-0" # Asset update has failed due to invalid hours. Hours value too low.
    AUHF_1 = "AUHF-1" # Asset update has failed due to invalid hours. Hours value too high.
    AUHF_2 = "AUHF-2" # Asset update has failed due to invalid lifespan years. The value must be a positive integer.
    EUHF_0 = "EUHF-0" # Engine update has failed due to invalid hours. Hours value too low.
    EUHF_1 = "EUHF-1" # Engine update has failed due to invalid hours. Hours value too high.
    UFN_0 = "UFN-0" # Unexpected file name.
    CSVUF_0 = "CSVUF-0" # CSV upload failed (asset)
    CSVUF_1 = "CSVUF-1" # CSV upload failed (location)
    CSVUF_2 = "CSVUF-2" # CSV upload failed (equipment_type)
    CSVUF_3 = "CSVUF-3" # CSV upload failed (manufacturer)
    CSVUF_4 = "CSVUF-4" # CSV upload failed (asset_type)
    CSVUF_5 = "CSVUF-5" # CSV upload failed (business_unit)
    CSVUF_6 = "CSVUF-6" # CSV upload failed (fuel_type)
    CSVUF_7 = "CSVUF-7" # CSV upload failed (role_permissions)
    CSVUF_8 = "CSVUF-8" # CSV upload failed (manufacturer_asset_type)
    CSVUF_9 = "CSVUF-9" # CSV upload failed (asset_request_justification)
    CSVUF_10 = "CSVUF-10" # CSV upload failed (company)
    CSVUF_11 = "CSVUF-11" # CSV upload failed (user)
    CSVUF_12 = "CSVUF-12" # CSV upload failed (vendor)
    CSVUF_13 = "CSVUF-13" # CSV upload failed (job_specification)
    CSVUF_14 = "CSVUF-14" # CSV upload failed (currency)
    CSVUF_15 = "CSVUF-15" # CSV upload failed (maintenance_rule)
    CSVUF_16 = "CSVUF-16" # CSV upload failed (maintenance)
    UUF_0 = "UUF-0" # User update failed.
    UUF_1 = "UUF-1" # User config update failed.
    IDR_0 = "IDR-0" # Invalid date range.
    UDNE_0 = "UDNE-0" # User DNE.
    UDNE_1 = "UDNE-1" # User config DNE.
    SNN_0 = "SNN-0" # Status is not new.
    DR_0 = "DR-0" # Repair already requested for issue.
    IIR_0 = "IIR-0" # Issues in repair are both from accidents and non-accidents.
    IDNE_0 = "IDNE-0" # Issue ID DNE.
    IDNE_1 = "IDNE-1" # Issue VIN DNE.
    IDNE_2 = "IDNE-2" # Issue Category ID DNE.
    IDNE_3 = "IDNE-3" # Issue custom ID DNE.
    IDNM_0 = "IDNM-0" # Issue VIN does not match repair VIN.
    UP_0 = "UP-0" # Wrong parameter.
    EF_0 = "EF-0" # Email has failed to send.
    EF_1 = "EF-1" # Email attachment has failed.
    ADNE_0 = "ADNE-0" # Accident ID DNE.
    ADNE_1 = "ADNE-1" # Accident custom ID DNE.
    DIF_0 = "DIF-0" # Data insertion error.
    VDNE_0 = "VDNE-0" # VIN DNE.
    VDF_0 = "VDF-0" # VIN Decoding failed.
    VL_0 = "VL-0" # VIN length wrong.
    VL_1 = "VL-1" # Assets VIN must have a length greter than 5
    DDNE_0 = "DDNE-0" # Disposal ID DNE.
    DDNE_1 = "DDNE-1" # Disposal custom ID DNE.
    OCDNE_0 = "OCDNE-0" # Op Check ID DNE.
    OCDNE_1 = "OCDNE-1" # Op Check custom ID DNE.
    OCDNE_2 = "OCDNE-2" # Op Check VIN DNE.
    MDNE_0 = "MDNE-0" # Manufacturer ID DNE.
    EDNE_0 = "EDNE-0" # Equipment Type DNE.
    MRDNE_0 = "MRDNE-0" # Maintenance ID DNE.
    MRDNE_1 = "MRDNE-1" # Maintenance work order ID DNE.
    MRDNE_2 = "MRDNE-2" # Maintenance forecast rule ID DNE.
    MRDNE_3 = "MRDNE-3" # Maintenance forecast rule custom ID DNE.
    MRVTC_0 = "MRVTC-0" # Maintenance Forecast rule asset tracks neither by hours or mileage.
    MRVTC_1 = "MRVTC-1" # Maintenance Forecast rule asset tracks by hours.
    MRVTC_2 = "MRVTC-2" # Maintenance Forecast rule asset tracks by mileage.
    MRVLU_0 = "MRVLU-0" # Maintenance Forecast rule values are less than 0.
    MRE_0 = "MRE-0" # Maintenance Forecast rule already exists for this inspection type.
    MSS_0 = "MSS-0" # Maintenance status is already what it's being set to.
    RDNE_0 = "RDNE-0" # Repair ID DNE.
    RDNE_1 = "RDNE-1" # Repair work order DNE.
    RDNE_2 = "RDNE-1" # Repair disposal ID DNE.
    RCDNE_0 = "RCDNE-0" # Repair cost DNE.
    IUF_0 = "IUF-0" # Image upload failure.
    IUF_1 = "IUF-1" # Image upload failed because files provided are wrong type.
    IDF_0 = "IDF-0" # Image deletion failure.
    FUF_0 = "FUF-0" # File upload failure.
    FUF_1 = "FUF-1" # File upload failed because files provided are wrong type.
    FUF_2 = "FUF-2" # File upload failed because files provided have unknown purpose.
    FUF_3 = "FUF-3" # File upload failed because of multiple file upload.
    FDF_0 = "FDF-0" # File deletion failure.
    ARDNE_0 = "ARDNE-0" # Asset request does not exist in the DB.
    MFE_0 = "MFE-0" # Maintenance forecasting error.
    MFE_1 = "MFE-1" # Maintenance forecast api found nothing related to this rule.
    ITDNE_0 = "ITDNE-0" # Inspection type does not exist.
    ADE_0 = "ADE-0" # A disposal request for this asset has been completed.
    ADE_1 = "ADE-1" # A disposal request for this asset is already in progress.
    MHF_0 = "MHF-0" # Model history failed. (asset)
    MHF_1 = "MHF-1" # Model history failed. (repair)
    MHF_2 = "MHF-2" # Model history failed. (maintenance)
    MHF_3 = "MHF-3" # Model history failed. (accident)
    MHF_4 = "MHF-4" # Model history failed. (issue)
    MHF_5 = "MHF-5" # Model history failed. (user)
    MHF_6 = "MHF-6" # Model history failed. (asset request)
    MHF_7 = "MHF-7" # Model history failed. (disposal)
    MHF_8 = "MHF-8" # Model history failed. (approval)
    MHF_9 = "MHF-9" # Model history failed. (asset transfer)
    MHF_10 = "MHF-10" # Model history failed. (parts)
    MHF_11 = "MHF-11" # Model history failed. (labor cost)
    MHF_12 = "MHF-12" # Model history failed. (daily check)
    MHF_13 = "MHF-13" # Model history failed. (fuel cost)
    MHF_14 = "MHF-14" # Model history failed. (insurance cost)
    MHF_15 = "MHF-15" # Model history failed. (license cost)
    MHF_16 = "MHF-16" # Model history failed. (rental cost)
    MHF_17 = "MHF-17" # Model history failed. (acquisition cost)
    MHF_18 = "MHF-18" # Model history failed. (asset type checks)
    MHF_19 = "MHF-19" # Model history failed. (pricing rate)
    MHF_20 = "MHF-20" # Model history failed. (invoice log)
    ALF_0 = "ALF-1" # Asset log failed. (asset)
    ALF_1 = "ALF-1" # Asset log failed. (repair)
    ALF_2 = "ALF-2" # Asset log failed. (maintenance)
    ALF_3 = "ALF-3" # Asset log failed. (accident)
    ALF_4 = "ALF-4" # Asset log failed. (issue)
    ALF_6 = "ALF-6" # Asset log failed. (asset request)
    ALF_7 = "ALF-7" # Asset log failed. (disposal)
    ALF_9 = "ALF-9" # Asset log failed. (transfer)
    ALF_10 = "ALF-10" # Asset log fialed. (op-check)
    FG_DNE = "FGDNE-0" # Fleet Guru process does not exist
    IADS_0 = "IDS-0" # Invalid asset disposal status
    ADUF_0 = "ADUF-0" # Asset Disposal failed because the disposal type does not match the api
    ADUF_1 = "ADUF-1" # Asset Disposal update failed because the provided file info does not match the provided files.
    ADUF_2 = "ADUF-2" # Asset Disposal update failed because the required file types were not all provided.
    ADUF_3 = "ADUF-3" # Asset Disposal update failed because the refurbishment repair is not complete.
    BUDNE_0 = "BUDNE-0" # Business unit does not exist for the provided filter
    CDNE_0 = "CDNE-0" # Company does not exist for the provided filter
    FCDNE_0 = "FCDNE_0" # Fuel cost id does not exist or marked as deleted
    RPDNE_0 = "RPDNE-0" # Role permissions do not exist for the provided filter
    AMFK_0 = "AMFK-0" # Approval missing foreign key to a request.
    APRDNE_0 = "APRDNE-0" # Approval request DNE.
    ASUF_0 = "ASUF_0" # Approval authorization failed. User is not allowed to set/update the approval status.
    FSU_0 = "FSU-0" # Failed to set user as FK to created_by or modified_by. (AccidentView)
    FSU_1 = "FSU-1" # Failed to set user as FK to created_by or modified_by. (DailyOperationalView)
    FSU_2 = "FSU-2" # Failed to set user as FK to created_by or modified_by. (DisposalView)
    FSU_3 = "FSU-3" # Failed to set user as FK to created_by or modified_by. (IssueView)
    FSU_4 = "FSU-4" # Failed to set user as FK to created_by or modified_by. (MaintenanceView)
    FSU_5 = "FSU-5" # Failed to set user as FK to created_by or modified_by. (RepairsView)
    FSU_6 = "FSU-6" # Failed to set user as FK to created_by or modified_by. (TransferView)
    FSU_7 = "FSU-7" # Failed to set user as FK to created_by or modified_by. (FuelCostView)
    FSU_8 = "FSU-8" # Failed to set user as FK to created_by or modified_by. (LicenseCostView)
    FSU_9 = "FSU-9" # Failed to set user as FK to created_by or modified_by. (RentalCostView)
    FSU_10 = "FSU-10" # Failed to set user as FK to created_by or modified_by. (LaborCostView)
    FSU_11 = "FSU-11" # Failed to set user as FK to created_by or modified_by. (PartsCostView)
    FSU_12 = "FSU-12" # Failed to set user as FK to created_by or modified_by. (InsuranceView)
    FSU_13 = "FSU-13" # Failed to set user as FK to created_by or modified_by. (EquipmentTypeView)
    FSU_14 = "FSU-14" # Failed to set user as FK to created_by or modified_by. (AssetTypeView)
    FSU_15 = "FSU-15" # Failed to set user as FK to created_by or modified_by. (ManufacturerView)
    IAT_0 = "IAT-0" # Invalid asset transfer. (Asset is inoperative)
    IAT_1 = "IAT-1" # Invalid asset transfer. (Provided status is invalid)
    IAT_2 = "IAT-2" # Invalid asset transfer. (Provided status is not new)
    IAT_3 = "IAT-3" # Invalid asset transfer. (Invalid condition value(s))
    IAT_4 = "IAT-4" # Invalid asset transfer. (Invalid condition details)
    IAT_5 = "IAT-5" # Invalid asset transfer. (Invalid usage)
    ATDNE_0 = "ATDNE-0" # Asset transfer ID DNE.
    ATDNE_1 = "ATDNE-1" # Asset transfer custom ID DNE.
    IER_0 = "IER-0" # Invalid error report. (Provided issue type is not valid)
    DOCI_0 = "DOCI-0" # Asset needs mileage but daily operational check does not have it.
    DOCI_1 = "DOCI-1" # Asset needs hours but daily operational check does not have them.
    DOCI_2 = "DOCI-2" # Asset needs mileage and hours but daily operational check does not have them.
    DOCI_3 = "DOCI-3" # One or more of the comments added to this daily check have invalid check field.
    DOCI_4 = "DOCI-4" # Failed to add comment(s) for asset daily operator check.
    RRI_0 = "RRI-0" # Asset needs mileage but repair request does not have it.
    RRI_1 = "RRI-1" # Asset needs hours but repair request does not have it.
    RRI_2 = "RRI-2" # Asset needs mileage and hours but repai request does not have them.
    MRI_0 = "MRI-0" # Asset needs mileage but maintenance request does not have it.
    MRI_1 = "MRI-1" # Asset needs hours but maintenance request does not have it.
    MRI_2 = "MRI-2" # Asset needs mileage and hours but maintenance request does not have them.
    UNSU_0 = "UNSU-0" # Requesting user needs to be a superuser
    LDE_0 = "LDE-0" # Requested location does not exist 
    LDNM_0 = "LDNM-0" # Requested assets have different locations
    PNDNE_0 = "PNDNE-0" # Parts number does not exist
    RAD_0 = "RAD-0" # Repurpose disposal needs purpose but asset disposal does not have it
    RAD_1 = "RAD-1" # Scrap disposal needs will_strip asset disposal does not have it
    RAD_2 = "RAD-2" # Disposal is not of the correct type
    JSDNE_0 = "JSDNE-0" # No job specification under that id
    JSDNE_1 = "JSDNE-1" # No job specification under that name
    SSF_0 = "SSF-0" # Snapshot failed - daily fleet
    SSF_1 = "SSF-1" # Snapshot failed - daily cost
    SSF_2 = "SSF-2" # Snapshot failed - daily assets and checks
    SSF_3 = "SSF-3" # Snapshot failed - daily currency exchange
    NF_0 = "NF-0" # Notification failed - maintenance
    NF_1 = "NF-1" # Notification failed - expiry
    VIDDNE_0 = "VIDDNE-0" # Vendor ID DNE.
    JDNE_0 = "JDNE-0" # Justification ID DNE.
    ATNDNE_0 = "ATNDNE-0" #Asset type DNE
    ATNDNE_1 = "ATNDNE-1" #Asset type checks DNE
    MNDNE_0 = "MNDNE-0" #Manufacturer DNE
    FTDNE_0 = "FTDNE-0" #Fuel type DNE
    ETCF_0 = "ETCF-0" #Equipment type creation failed
    FTCF_0 = "FTCF-0" #Fuel type creation failed
    ATCF_0 = "ATCF-0" #Asset type creation failed
    AMCF_0 = "AMCF-0" #Asset manufacturer creation failed
    RFNP_0 = "RFNP-0" #Required fields not provided (add equipment type)
    RFNP_1 = "RFNP-1" #Required field is not provided (update equipment type)
    ETEAE_0 = "ETEAE-0" #Equipemnt type entry already exists
    CEE_0 = "CEE_0" #Currency exchange API failed
    CDNE_0 = "CDNE-0" #Currency ID does not exist
    PSHR_0 = "PSHR_0" # Pusher authentication failed
    PSHRFNP_0 = "PSHRFNP_0" # Required fields not present (pusher authentication)
    NATPA_0 = "NATPA_0" # Not authorized to perform action
    PCF_0 = "PCF-0" # One or more of the child assets are the parent asset
    PCF_1 = "PCF-1" # Circular relationship
    PRDNE_0 = "PRDNE-0" # Pricing rate entry does not exist for the given company ID
    NCDNE_0 = "NCDNE-0" # Notification config does not exist for the given name

    # Error(dev_message, user_message)
    error_dictionary = {
        G_0: Error("An exception occured.", "Something went wrong. Please send homing pigeon to support for more information."),
        S_0: Error("Serializer error.", "Something went wrong. Please send homing pigeon to support for more information."),
        I_0: Error("Input error.", "Something went wrong. Please send homing pigeon to support for more information."),
        I_1: Error("Missing/invalid inputs for user creation.", "Inputs for user creation are invalid or missing. Please send homing pigeon to support for more information."),
        IL_0: Error("Invalid Login.", "Invalid login information."),
        IL_1: Error("Invalid email.", "There is no account under that email."),
        IL_2: Error("This account has been deactivated.", "This account has been deactivated."),
        IE_0: Error("Invalid email address.", "You must enter a valid email address."),
        IE_1: Error("The email address is already in use.", "The email address is already in use."),
        IP_0: Error("Invalid password (less than 8 chars).", "Your password has to be atleast 8 characters long."),
        IP_1: Error("Invalid password (no numbers used).", "Your password has to have atleast 1 numeric character."),
        IP_2: Error("Invalid password (no capitals used).", "Your password has to have atleast 1 capital letter."),
        IP_3: Error("Invalid password (more than 32 chars).", "Your password has to be 32 characters or less."),
        AS_0: Error("Agreement status has not changed.", "Agreement status has not changed."),
        IT_0: Error("Invalid token.", "This token is already expired."),
        IS_0: Error("Invalid status.", "The provided status is not valid."),
        MEV_0: Error("Missing environmental variable.", "Something went wrong. Please send homing pigeon to support for more information."),
        WFF_0: Error("Writing file to disc failed.", "Writing file to disc failed. Please send homing pigeon to support for more information."),
        CSVF_0: Error("Failed to generate in memory CSV.", "Failed to generate CSV. Please send homing pigeon to support for more information."),
        MTOA_0: Error("More than one asset was found by this query.", "More than one asset was found."),
        AUET_0: Error("Asset unknown equipment type.", "The equipment type for this asset is missing."),
        ACF_0: Error("Asset creation failed.", "Failed to insert the asset into the database. Please send homing pigeon to support for more information."),
        ACF_2: Error("Asset with that VIN already exists in the system.", "Asset with that VIN already exists in the system. Please send homing pigeon to support for more information."),
        TUF_0: Error("Parts update has failed.", "Failed to update part fields. Please send homing pigeon to support for more information."),
        TUF_1: Error("Labor Cost update has failed.", "Failed to update labor cost fields. Please send homing pigeon to support for more information."),
        TUF_2: Error("Asset update has failed.", "Failed to update asset fields. Please send homing pigeon to support for more information."),
        TUF_3: Error("Repair update has failed.", "Failed to update repair fields. Please send homing pigeon to support for more information."),
        TUF_4: Error("Maintenance update has failed.", "Failed to update maintenance fields. Please send homing pigeon to support for more information."),
        TUF_5: Error("Accident update has failed.", "Failed to update accident fields. Please send homing pigeon to support for more information."),
        TUF_6: Error("Disposal update has failed.", "Failed to update disposal fields. Please send homing pigeon to support for more information."),
        TUF_7: Error("Asset request update has failed.", "Failed to update asset request fields. Please send homing pigeon to support for more information."),
        TUF_8: Error("Issue update has failed.", "Failed to update issue fields. Please send homing pigeon to support for more information."),
        TUF_9: Error("Transfer update has failed.", "Failed to update transfer fields. Please send homing pigeon to support for more information."),
        TUF_10: Error("Daily operator check update has failed.", "Failed to update daily operator check fields. Please send homing pigeon to support for more information."),
        TUF_11: Error("Equipment type update has failed.", "Failed to update equipment type fields. Please send homing pigeon to support for more information."),
        TUF_12: Error("Asset type update has failed.", "Failed to update asset type fields. Please send homing pigeon to support for more information."),
        TUF_13: Error("Asset type checks update has failed.", "Failed to update asset type checks fields. Please send homing pigeon to support for more information."),
        TUF_14: Error("Pricing rates update has failed.", "Failed to update pricing rates fields."),
        TUF_15: Error("Notification configuration update has failed.", "Failed to update notification configuration fields."),
        TUF_16: Error("Asset update has failed. Asset is inoperative or disposed of.", "Failed to update asset fields. Asset is inoperative or disposed of. Please send homing pigeon to support for more information."),
        AUMF_0: Error("Mileage value too low.", "The provided mileage value is lower than the current value for this asset."),
        AUMF_1: Error("Mileage value too high.", "The provided mileage value appears to be too high in comparison to the last record for this asset."),
        AUHF_0: Error("Hours value too low.", "The provided hours value is lower than the current value for this asset."),
        AUHF_1: Error("Hours value too high.", "The provided hours value appears to be too high in comparison to the last record for this asset."),
        AUHF_2: Error("Invalid lifespan years.", "Asset update has failed due to invalid lifespan years. The value must be a positive integer."),
        EUHF_0: Error("Hours value too low.", "The provided hours value is lower than the current value for this engine."),
        EUHF_1: Error("Hours value too high.", "The provided hours value appears to be too high in comparison to the last record for this engine."),
        UFN_0: Error("Unexpected file name.", "Unexpected file name."),
        CSVUF_0: Error("CSV upload failed (asset).", "The asset csv spreadsheet has failed to upload. Please send homing pigeon to support for more information."),
        CSVUF_1: Error("CSV upload failed (location).", "The location csv spreadsheet has failed to upload. Please send homing pigeon to support for more information."),
        CSVUF_2: Error("CSV upload failed (equipment_type).", "The equipment csv spreadsheet has failed to upload. Please send homing pigeon to support for more information."),
        CSVUF_3: Error("CSV upload failed (manufacturer).", "The manufacturer csv spreadsheet has failed to upload. Please send homing pigeon to support for more information."),
        CSVUF_4: Error("CSV upload failed (asset_type).", "The asset type csv spreadsheet has failed to upload. Please send homing pigeon to support for more information."),
        CSVUF_5: Error("CSV upload failed (business_unit).", "The business unit csv spreadsheet has failed to upload. Please send homing pigeon to support for more information."),
        CSVUF_6: Error("CSV upload failed (fuel_type).", "The fuel type csv spreadsheet has failed to upload. Please send homing pigeon to support for more information."),
        CSVUF_7: Error("CSV upload failed (role_permissions).", "The role permissions csv spreadsheet has failed to upload. Please send homing pigeon to support for more information."),
        CSVUF_8: Error("CSV upload failed (manufacturer_asset_type).", "The manufacturer and asset type csv spreadsheet has failed to upload. Please send homing pigeon to support for more information."),
        CSVUF_9: Error("CSV upload failed (asset_request_justification).", "The asset request justification spreadsheet has failed to upload. Please send homing pigeon to support for more information."),
        CSVUF_10: Error("CSV upload failed (company).", "The company spreadsheet has failed to upload. Please send homing pigeon to support for more information."),
        CSVUF_11: Error("CSV upload failed (user).", "The user spreadsheet has failed to upload. Please send homing pigeon to support for more information."),
        CSVUF_12: Error("CSV upload failed (vendor).", "The vendor spreadsheet has failed to upload. Please send homing pigeon to support for more information."),
        CSVUF_13: Error("CSV upload failed (job specification).", "The job specification spreadsheet has failed to upload. Please send homing pigeon to support for more information."),
        CSVUF_14: Error("CSV upload failed (currency).", "The currency spreadsheet has failed to upload. Please send homing pigeon to support for more information."),
        CSVUF_15: Error("CSV upload failed (maintenance rule).", "The maintenance rule spreadsheet has failed to upload. Please send homing pigeon to support for more information."),
        CSVUF_16: Error("CSV upload failed (maintenance).", "The maintenance spreadsheet has failed to upload. Please send homing pigeon to support for more information."),
        UUF_0: Error("User update failed.", "User account has failed to update. Please send homing pigeon to support for more information."),
        UUF_0: Error("User config update failed.", "User configuration has failed to update. Please send homing pigeon to support for more information."),
        IDR_0: Error("Invalid date range.", "The date range provided is invalid."),
        UDNE_0: Error("User DNE.", "User does not exist."),
        UDNE_0: Error("User config DNE.", "User configuration does not exist."),
        SNN_0: Error("Status has not changed.", "Status has not changed."),
        DR_0: Error("Repair already requested for issue.", "Repair order for one or more of the added issues already exists. Please select different issue(s)."),
        IIR_0: Error("Issues in repair are from both accidents and non-accidents.", "Some issues in the repair are caused by accidents while others are not. Please include only accident related issues or issues not linked to an accident."),
        IDNE_0: Error("Issue ID DNE.", "This issue report does not exist in the database. Please check your entry and try again"),
        IDNE_1: Error("Issue VIN DNE.", "An Issue for that VIN does not exist."),
        IDNE_2: Error("Issue Category ID DNE.", "This issue category does not exist in the database. Please check your entry and try again"),
        IDNE_3: Error("Issue custom ID DNE.", "This issue report does not exist in the database. Please check your entry and try again"),
        IDNM_0: Error("Issue VIN does not match repair VIN.", "One or more of the issues entered has a VIN that does not match the VIN of the Repair Request."),
        UP_0: Error("Unknown parameter used in URL.", "Something went wrong. Please send homing pigeon to support for more information."),
        EF_0: Error("Email has failed to send.", "Email has failed to send. Please contant support for more information."),
        EF_1: Error("Email attachment has failed.", "Email has failed to send. Please contant support for more information."),
        ADNE_0: Error("Accident ID DNE.", "The accident report does not exist."),
        ADNE_1: Error("Accident custom ID DNE.", "The accident report does not exist."),
        DIF_0: Error("Data insertion has failed.", "Data has failed to insert into the system. Please make sure that the input spreadsheet matches the specified standard."),
        VDNE_0: Error("VIN DNE.", "The VIN you have entered does not exist."),
        VL_0: Error("Not enough characters to search VIN (min 6).", "Must enter atleast 6 characters to search VIN."),
        VL_1: Error("Assets VIN must have a length greater than 5.", "Must enter atleast 6 characters for the VIN to create an asset."),        
        DDNE_0: Error("Disposal ID DNE.", "This disposal request does not exist in the database. Please check your entry and try again."),
        DDNE_1: Error("Disposal custom ID DNE.", "This disposal request does not exist in the database. Please check your entry and try again."),
        OCDNE_0: Error("Operational ID DNE.", "An Operational Check for this ID does not exist."),
        OCDNE_1: Error("Operational custom ID DNE.", "An Operational Check for this custom ID does not exist."),
        OCDNE_2: Error("Operational Check VIN DNE.", "An Operational Check for this VIN does not exist."),
        MDNE_0: Error("Manufacturer ID DNE.", "Manufacturers for the selected asset type do not exist."),
        EDNE_0: Error("Equipment Type DNE.", "This equipment type does not exist in the database. Please check your entry and try again."),
        MRDNE_0: Error("Maintenance ID DNE.", "This maintenance request does not exist in the database. Please check your entry and try again."),
        MRDNE_1: Error("Maintenance work order ID DNE.", "This maintenance request does not exist in the database. Please check your entry and try again."),
        MRDNE_2: Error("Maintenance forecast rule ID DNE.", "This maintenance forecast rule does not exist in the database. Please check your entry and try again."),
        MRDNE_3: Error("Maintenance forecast rule custom ID DNE.", "This maintenance forecast rule does not exist in the database. Please check your entry and try again."),
        MRVTC_0: Error("Asset neither tracks hour_cycle nor mileage_cycle.", "This asset only supports maintenance cycles based on time."),
        MRVTC_1: Error("Asset tracks time_cycle and hour_cycle only.", "This asset only supports maintenance cycles based on time and hours."),
        MRVTC_2: Error("Asset tracks time_cycle and mileage_cycle only.", "This asset only supports maintenance cycles based on time and mileage."),
        MRVLU_0: Error("Maintenance forecast values are less than 0.", "Maintenance cycle values can't be less than 0. Wouldn't it be funny if that was the case!"),
        MRE_0: Error("Maintenance forecast rule already exists.", "Maintenance Forecast Rule already exists for this inspection type. Try editing the existing rule instead."),
        MSS_0: Error("Maintenance status is already what it's being set to.", "The maintenance status has not changed."),
        RDNE_0: Error("Repair ID DNE.", "This repair request does not exist in the database. Please check your entry and try again."),
        RDNE_1: Error("Repair work order DNE.", "This repair request does not exist in the database. Please check your entry and try again."),
        RDNE_2: Error("Repair disposal ID DNE.", "This repair request does not exist in the database. Please check your entry and try again."),
        RCDNE_0: Error("Repair cost DNE.", "This repair request does not have any cost inputs. Please enter all costs associated with the repair before marking it as delivered."),
        IUF_0: Error("Image upload failure.", "One or more of the selected images have failed to upload. Please send homing pigeon to support for more information."),
        IUF_1: Error("Image upload failed due to wrong file type(s).", "One or more of the selected images are of an unsupported format."),
        IDF_0: Error("Image has failed to delete from blob storage.", "Something went wrong. Please send homing pigeon to support for more information."),
        FUF_0: Error("File upload failure.", "One or more of the selected files have failed to upload. Please send homing pigeon to support for more information."),
        FUF_1: Error("File upload failed due to wrong file type(s).", "One or more of the selected files are of an unsupported format."),
        FUF_2: Error("File upload failed due to unknown file purpose.", "File upload was unable to identify the file's purpose. Please send homing pigeon to support for more information."),
        FUF_3: Error("File upload failed due to no or multiple files.", "Please upload one file at a time! Please send homing pigeon to support for more information."),
        FDF_0: Error("File has failed to delete from blob storage.", "Something went wrong. Please send homing pigeon to support for more information."),
        ARDNE_0: Error("Asset Request ID does not exist in the DB", "This asset request order does not exist in the database. Please check your entry and try again."),
        MFE_0: Error("Forecasting algorithm has encountered an error (check logs).", "Something went wrong. Please send homing pigeon to support for more information."),
        MFE_1: Error("Maintenance forecast api found nothing related to this rule.", "There is not enough data at this time to forecast maintenance for this inspection type."),
        ITDNE_0: Error("Inspection type provided does not exist.", "Something went wrong. Please send homing pigeon to support for more information."),
        ADE_0: Error("A disposal request for this asset has been completed.", "Asset already disposed of."),
        ADE_1: Error("A disposal request for this asset is already in progress.", "Asset is already in the process of being disposed of."),
        MHF_0: Error("Failed to create historical record for model (asset).", "System has failed to save previous data. Please send homing pigeon to support for more information."),
        MHF_1: Error("Failed to create historical record for model (repair).", "System has failed to save previous data. Please send homing pigeon to support for more information."),
        MHF_2: Error("Failed to create historical record for model (maintenance).", "System has failed to save previous data. Please send homing pigeon to support for more information."),
        MHF_3: Error("Failed to create historical record for model (accident).", "System has failed to save previous data. Please send homing pigeon to support for more information."),
        MHF_4: Error("Failed to create historical record for model (issue).", "System has failed to save previous data. Please send homing pigeon to support for more information."),
        MHF_5: Error("Failed to create historical record for model (user).", "System has failed to save previous data. Please send homing pigeon to support for more information."),
        MHF_6: Error("Failed to create historical record for model (asset request).", "System has failed to save previous data. Please send homing pigeon to support for more information."),
        MHF_7: Error("Failed to create historical record for model (disposal).", "System has failed to save previous data. Please send homing pigeon to support for more information."),
        MHF_8: Error("Failed to create historical record for model (approval).", "System has failed to save previous data. Please send homing pigeon to support for more information."),
        MHF_9: Error("Failed to create historical record for model (asset transfer).", "System has failed to save previous data. Please send homing pigeon to support for more information."),
        MHF_10: Error("Failed to create historical record for model (parts).", "System has failed to save previous data. Please send homing pigeon to support for more information."),
        MHF_11: Error("Failed to create historical record for model (labor cost).", "System has failed to save previous data. Please send homing pigeon to support for more information."),
        MHF_12: Error("Failed to create historical record for model (daily check).", "System has failed to save previous data. Please send homing pigeon to support for more information."),
        MHF_13: Error("Failed to create historical record for model (fuel cost).", "System has failed to save previous data. Please send homing pigeon to support for more information."),
        MHF_14: Error("Failed to create historical record for model (insurance cost).", "System has failed to save previous data. Please send homing pigeon to support for more information."),
        MHF_15: Error("Failed to create historical record for model (license cost).", "System has failed to save previous data. Please send homing pigeon to support for more information."),
        MHF_16: Error("Failed to create historical record for model (rental cost).", "System has failed to save previous data. Please send homing pigeon to support for more information."),
        MHF_17: Error("Failed to create historical record for model (acquisition cost).", "System has failed to save previous data. Please send homing pigeon to support for more information."),
        MHF_18: Error("Failed to create historical record for model (asset type checks).", "System has failed to save previous data. Please send homing pigeon to support for more information."),
        MHF_19: Error("Failed to create historical record for model (pricing rates).", "System has failed to save previous data. Please send homing pigeon to support for more information."),
        MHF_20: Error("Failed to create historical record for model (invoice log).", "System has failed to save previous data. Please send homing pigeon to support for more information."),
        ALF_0: Error("Asset log failed (asset).", "System has failed to log actions. Please send homing pigeon to support for more information."),
        ALF_1: Error("Asset log failed (repair).", "System has failed to log actions. Please send homing pigeon to support for more information."),
        ALF_2: Error("Asset log failed (maintenance).", "System has failed to log actions. Please send homing pigeon to support for more information."),
        ALF_3: Error("Asset log failed (accident).", "System has failed to log actions. Please send homing pigeon to support for more information."),
        ALF_4: Error("Asset log failed (issue).", "System has failed to log actions. Please send homing pigeon to support for more information."),
        ALF_6: Error("Asset log failed (request).", "System has failed to log actions. Please send homing pigeon to support for more information."),
        ALF_7: Error("Asset log failed (disposal).", "System has failed to log actions. Please send homing pigeon to support for more information."),
        ALF_9: Error("Asset log failed (transfer).", "System has failed to log actions. Please send homing pigeon to support for more information."),
        ALF_10: Error("Asset log failed (op-check).", "System has failed to log actions. Please send homing pigeon to support for more information."),
        FG_DNE: Error("Fleet guru url argument was invlaid (Fleet Guru).", "FleetGuru could not find any tips :("),
        IADS_0: Error("The status provided is not valid for the AssetDisposalModel.", "The status provided is invalid."),
        ADUF_0: Error("Asset disposal failed because the disposal type does not match the api.", "The asset disposal is of the wrong type. Please send homing pigeon to support for more information."),
        ADUF_1: Error("Asset disposal update failed because the provided file info does not match the provided files.", "Asset disposal update failed because the provided file info does not match the provided files. Please send homing pigeon to support for more information."),
        ADUF_2: Error("Asset Disposal update failed because the required file types were not all provided.", "Asset disposal update failed because the required file types were not all provided. Please send homing pigeon to support for more information."),
        ADUF_3: Error("Asset Disposal update failed because the refurbishment repair is not complete.", "Asset disposal update failed because the refurbishment repair is not complete. Please send homing pigeon to support for more information."),
        BUDNE_0: Error("Business Unit entry for the provided filter DNE.", "A Business Unit does not exist for this search criteria. Please send homing pigeon to support for more information."),
        CDNE_0: Error("Company entry for the provided filter DNE.", "A Company does not exist for this search criteria. Please send homing pigeon to support for more information."),
        FCDNE_0: Error("Fuel cost entry for the provided id DNE or marked as deleted.", "The fuel cost entry with this id does not exist or marked as deleted. Please send homing pigeon to support for more information."),
        RPDNE_0: Error("Role Permissions entry for the provided filter DNE.", "Could not establish permissions. Please send homing pigeon to support for more information."),
        AMFK_0: Error("Approval missing foreign key to a request object.", "You must select a request to attach this approval to."),
        APRDNE_0: Error("Approval ID does not exist in the DB.", "The approval request does not exist in the database. Please check your entry and try again."),
        ASUF_0: Error("Approval authorization failed. User is not allowed to set/update the approval status.", "You are not authorized to update this approval request."),
        FSU_0: Error("Failed to set user as FK to created_by or modified_by. (AccidentView)", "Something went wrong. Please send homing pigeon to support for more information."),
        FSU_1: Error("Failed to set user as FK to created_by or modified_by. (DailyOperationalView)", "Something went wrong. Please send homing pigeon to support for more information."),
        FSU_2: Error("Failed to set user as FK to created_by or modified_by. (DisposalView)", "Something went wrong. Please send homing pigeon to support for more information."),
        FSU_3: Error("Failed to set user as FK to created_by or modified_by. (IssueView)", "Something went wrong. Please send homing pigeon to support for more information."),
        FSU_4: Error("Failed to set user as FK to created_by or modified_by. (MaintenanceView)", "Something went wrong. Please send homing pigeon to support for more information."),
        FSU_5: Error("Failed to set user as FK to created_by or modified_by. (RepairsView)", "Something went wrong. Please send homing pigeon to support for more information."),
        FSU_6: Error("Failed to set user as FK to created_by or modified_by. (TransferView)", "Something went wrong. Please send homing pigeon to support for more information."),
        FSU_7: Error("Failed to set user as FK to created_by or modified_by. (FuelCostView)", "Something went wrong. Please send homing pigeon to support for more information."),
        FSU_8: Error("Failed to set user as FK to created_by or modified_by. (LicenseCostView)", "Something went wrong. Please send homing pigeon to support for more information."),
        FSU_9: Error("Failed to set user as FK to created_by or modified_by. (RentalCostView)", "Something went wrong. Please send homing pigeon to support for more information."),
        FSU_10: Error("Failed to set user as FK to created_by or modified_by. (LaborCostView)", "Something went wrong. Please send homing pigeon to support for more information."),
        FSU_11: Error("Failed to set user as FK to created_by or modified_by. (PartsCostView)", "Something went wrong. Please send homing pigeon to support for more information."),
        FSU_12: Error("Failed to set user as FK to created_by or modified_by. (InsuranceView)", "Something went wrong. Please send homing pigeon to support for more information."),
        FSU_13: Error("Failed to set user as FK to created_by or modified_by. (EquipmentTypeView)", "Something went wrong. Please send homing pigeon to support for more information."),
        FSU_14: Error("Failed to set user as FK to created_by or modified_by. (AssetTypeView)", "Something went wrong. Please send homing pigeon to support for more information."),
        FSU_15: Error("Failed to set user as FK to created_by or modified_by. (ManufacturerView)", "Something went wrong. Please send homing pigeon to support for more information."),
        IAT_0: Error("Invalid asset transfer. (Asset is inoperative)", "The asset you want to transfer is inoperative and can not be transferred."),
        IAT_1: Error("Invalid asset transfer. (Provided status is invalid)", "The status you have provided is invalid."),
        IAT_2: Error("Invalid asset transfer. (Provided status is not new)", "The status you have provided is not new."),
        IAT_3: Error("Invalid asset transfer. (Invalid condition value(s))", "The condition value(s) provided is not valid. Expected 'poor', 'average', or 'good'."),
        IAT_4: Error("Invalid asset transfer. (Invalid condition details)", "Condition details for the asset were not valid."),
        IAT_5: Error("Invalid asset transfer. (Invalid usage)", "The usage provided (mileage/hours) was not valid."),
        ATDNE_0: Error("Asset transfer ID does not exist in the DB.", "The asset transfer does not exist in the database. Please check your entry and try again."),
        ATDNE_1: Error("Asset transfer custom ID does not exist in the DB.", "The asset transfer does not exist in the database. Please check your entry and try again."),
        IER_0: Error("Invalid error report. (Provided issue type is not valid)", "The issue type you have provided is not valid."),
        DOCI_0: Error("Asset needs mileage but daily operational check does not have it.", "Must include mileage for this asset."),
        DOCI_1: Error("Asset needs hours but daily operational check does not have them.", "Must include hours for this asset."),
        DOCI_2: Error("Asset needs mileage and hours but daily operational check does not have them.", "Must include both mileage and hours for this asset."),
        DOCI_3: Error("One or more of the comments added to this daily check have invalid check field.", "Ran into a problem while adding this daily check. Please send homing pigeon to support for more information."),
        DOCI_4: Error("Failed to add comment(s) for asset daily operator check.", "Ran into a problem while adding this daily check. Please send homing pigeon to support for more information."),
        RRI_0: Error("Asset needs mileage but repair request does not have it.", "Must include mileage for this asset."),
        RRI_1: Error ("Asset needs hours but repair request does not have it.", "Must include hours for this asset."),
        RRI_2: Error("Asset needs mileage and hours but repair request does not have them.", "Must include both mileage and hours for this asset."),
        MRI_0: Error("Asset needs mileage but maintenance request does not have it.", "Must include mileage for this asset."),
        MRI_1: Error ("Asset needs hours but maintenance request does not have it.", "Must include hours for this asset."),
        MRI_2: Error("Asset needs mileage and hours but maintenance request does not have them.", "Must include both mileage and hours for this asset."),
        UNSU_0: Error("You must be a superuser to update any user account information.", "You must be a superuser to update any user account information."),
        LDE_0: Error("Provided location does not exist.", "Provided location does not exist"),
        PNDNE_0: Error("Provided part number does not match any part.", "Provided part number does not match any part."),
        RAD_0: Error("Repurpose disposal needs purpose but asset disposal does not have it.", "Repurpose disposal needs purpose but asset disposal does not have it."),
        RAD_1: Error("Scrap disposal needs indication whether it will be stripped but asset disposal does not have it.", "Scrap disposal needs indication whether it will be stripped but asset disposal does not have it."),
        RAD_2: Error("Asset disposal is not the correct type.", "Asset disposal is not the correct type."),
        LDNM_0: Error("Provided assets have different locations.", "You must provide assets from the same location"),
        PNDNE_0: Error("Provided part number does not match any part.", "Provided part number does not match any part."), # Parts number does not exist
        JSDNE_0: Error("No job specification under that id.", "No job specification under that id. Please send homing pigeon to support for more information."),
        JSDNE_1: Error("No job specification under that name.", "No job specification under that name. Please send homing pigeon to support for more information."),
        SSF_0: Error("Snapshot failed - daily fleet.", "Snapshot failed - daily fleet."),
        SSF_1: Error("Snapshot failed - daily cost.", "Snapshot failed - daily cost."),
        SSF_2: Error("Snapshot failed - daily assets and checks.", "Snapshot failed - daily assets and checks."),
        SSF_3: Error("Snapshot failed - daily currency snapshot." , "Snapshot failed - daily currency snapshot."),
        NF_0: Error("Notification failed - maintenance." , "Notification failed - maintenance."),
        NF_1: Error("Notification failed - expiry." , "Notification failed - expiry."),
        VIDDNE_0: Error("Vendor ID DNE.", "This vendor does not exist in the database. Please check your entry and try again"),
        JDNE_0: Error("Justification ID DNE.", "This asset request justification does not exist in the database. Please check your entry and try again"),
        ATNDNE_0: Error("Asset type does not exist in the DB.", "This asset type does not exist in the database. Please check your entry and try again"),
        ATNDNE_1: Error("Asset type checks do not exist in the DB.", "This asset type does not have configured checks in the database. Please check your entry and try again"),
        MNDNE_0: Error("Manufacturer does not exist in the DB.", "This manufacturer does not exist in the database. Please check your entry and try again"),
        FTDNE_0: Error("Fuel Type does not exist in the DB.", "This fuel type does not exist in the database. Please check your entry and try again"),
        ETCF_0: Error("Failed to create equipment type entry.", "Equipment type could not be added to the database. Please send homing pigeon to support for more information."),
        FTCF_0: Error("Failed to create fuel type entry.", "Fuel type could not be added to the database. Please send homing pigeon to support for more information."),
        ATCF_0: Error("Failed to create asset type entry.", "Asset type could not be added to the database. Please send homing pigeon to support for more information."),
        AMCF_0: Error("Failed to create asset manufacturer entry.", "Asset manufacturer could not be added to the database. Please send homing pigeon to support for more information."),
        RFNP_0: Error("Required fields are not provided!", "Asset manufacturer, asset type and model number are required fields. Please send homing pigeon to support for more information."),
        RFNP_1: Error("Required field is not provided!", "Equipemnt type ID is a required field! Please send homing pigeon to support for more information."),
        ETEAE_0: Error("Equipment type entry already exists!", "Provided equipment type already exists in the database. Please send homing pigeon to support for more information."),
        CEE_0: Error("Currency exchange API call failed." "Failed to make the currency exchange API call. Please send homing pigeon to support for more information."),
        CDNE_0: Error("Currency ID does not exist in the DB", "This currency does not exist in the database. Please check your entry and try again."),
        PSHR_0: Error("Pusher authentication failed", "Something went wrong. Please send homing pigeon to support for more information."),
        PSHRFNP_0: Error("Required fields were not provided in the request to authenticate with pusher.", "Something went wrong. Please send homing pigeon to support for more information."),
        NATPA_0: Error("The user's current role does not allow this operation to be performed.", "Sorry, you are not authorized to perform this action. Please send homing pigeon to support for more information."),
        PCF_0: Error("One or more of the provided child assets are the parent asset.", "One or more of the provided child assets are the parent asset."),
        PCF_1: Error("Circular relationship found.", "Circular relationships are not supported. Please send homing pigeon to support for more information."),
        PRDNE_0: Error("Pricing rates entry does not exist for the given company id.", "Pricing rates entry does not exist for the given company id."),
        NCDNE_0: Error("Notification config does not exist for the given name.", "Notification config does not exist for the given name.")
    }

    @staticmethod
    def get_error_user(code):
        return CustomError.error_dictionary[code].error_message_user

    @staticmethod
    def get_error_dev(code, exception_str=""):
        if exception_str == "":
            return str(code) + " " + str(CustomError.error_dictionary[code].error_message_dev)
        else:
            return str(code) + " " + str(CustomError.error_dictionary[code].error_message_dev) + " (Extra info: " + str(exception_str) + ")"

    @staticmethod
    def get_full_error_json(code, exception_str=""):
        return {"error_code":code, "error_message_dev":CustomError.get_error_dev(code, exception_str), "error_message_user":CustomError.get_error_user(code)}


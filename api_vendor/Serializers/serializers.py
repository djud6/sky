from rest_framework import serializers
from ..Models.vendor import VendorModel
from ..Models.vendor_departments import VendorDepartments
from ..Models.vendor_tasks import VendorTasks
from api.Models.repairs import RepairsModel
from api.Models.maintenance_request import MaintenanceRequestModel
from api.Models.asset_disposal import AssetDisposalModel
from api.Models.asset_request import AssetRequestModel
from api.Models.asset_transfer import AssetTransfer
from api.Serializers.serializers import MaintenanceFileSerializer
from api.Serializers.serializers import RepairFileSerializer
from api.Serializers.serializers import AssetDisposalFileSerializer
from api.Serializers.serializers import IssueSerializer

class VendorModelSerializer(serializers.ModelSerializer):
    department_name = serializers.SlugRelatedField(read_only=True, source='vendor_department', slug_field='name')
    class Meta:
        model = VendorModel
        fields = "__all__"

# --------------------------------------------------------------------------------------------------------

class VendorDepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = VendorDepartments
        fields = "__all__"

# --------------------------------------------------------------------------------------------------------

class VendorTaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = VendorTasks
        fields = "__all__"

# --------------------------------------------------------------------------------------------------------

class VendorAssetRequestSerializer(serializers.ModelSerializer):
    asset_type = serializers.SlugRelatedField(read_only=True, source='equipment.asset_type', slug_field='name')
    manufacturer = serializers.SlugRelatedField(read_only=True, source='equipment.manufacturer', slug_field='name')
    model_number = serializers.SlugRelatedField(read_only=True, source='equipment', slug_field='model_number')
    engine = serializers.SlugRelatedField(read_only=True, source='equipment', slug_field='engine')
    created_by = serializers.SlugRelatedField(read_only=True, slug_field='email')
    modified_by = serializers.SlugRelatedField(read_only=True, slug_field='email')
    business_unit = serializers.SlugRelatedField(read_only=True, slug_field='name')
    justification = serializers.SlugRelatedField(read_only=True, slug_field='name')
    location = serializers.SlugRelatedField(read_only=True, slug_field='location_name')
    vendor_name = serializers.SlugRelatedField(read_only=True, source='vendor', slug_field='vendor_name')
    disposal_custom_id = serializers.SlugRelatedField(read_only=True, source='disposal', slug_field='custom_id')
    files = serializers.SerializerMethodField()
    quotes = serializers.SerializerMethodField()
    
    def get_files(self, asset_request_obj):
        all_files = self.context.get('asset_request_files')
        if all_files:
            relevant_files = []
            for f in all_files:
                if f.get('asset_request_id') == asset_request_obj.id:
                    relevant_files.append(f)
            return relevant_files
        return []

    def get_quotes(self, asset_request_obj):
        all_quotes = self.context.get('request_quotes')
        if all_quotes:
            relevant_quotes = []
            for quote in all_quotes:
                if quote.get('asset_request_id') == asset_request_obj.id:
                    relevant_quotes.append(quote)
            return relevant_quotes
        return []

    class Meta:
        model = AssetRequestModel
        fields = "__all__"

# --------------------------------------------------------------------------------------------------------

class VendorRepairsSerializer(serializers.ModelSerializer):
    asset_type = serializers.SlugRelatedField(read_only=True, source='VIN.equipment_type.asset_type', slug_field='name')
    business_unit = serializers.SlugRelatedField(read_only=True, source='VIN.department', slug_field='name')
    created_by = serializers.SlugRelatedField(read_only=True, slug_field='email')
    modified_by = serializers.SlugRelatedField(read_only=True, slug_field='email')
    current_location = serializers.SlugRelatedField(read_only=True, source='VIN.current_location', slug_field='location_name')
    repair_location = serializers.SlugRelatedField(read_only=True, source='location', slug_field='location_name')
    issues = serializers.SerializerMethodField()
    files = serializers.SerializerMethodField()
    quotes = serializers.SerializerMethodField()
    
    def get_issues(self, repair_obj):
        all_issues = self.context.get('all_issues')
        if all_issues:
            relevant_issues = []
            for item in all_issues:
                if item.repair_id == repair_obj:
                    relevant_issues.append(item)

            return IssueSerializer(relevant_issues, many=True, context=self.context).data
        return []

    def get_files(self, repair_obj):
        all_files = self.context.get('all_repair_files')
        if all_files:
            relevant_files = []
            for f in all_files:
                if f.get('repair_id') == repair_obj.repair_id:
                    relevant_files.append(f)

            return relevant_files
        return []

    def get_quotes(self, repair_obj):
        all_quotes = self.context.get('request_quotes')
        if all_quotes:
            relevant_quotes = []
            for quote in all_quotes:
                if quote.get('repair_request_id') == repair_obj.repair_id:
                    relevant_quotes.append(quote)
            return relevant_quotes
        return []

    class Meta:
        model = RepairsModel
        fields = "__all__"

# --------------------------------------------------------------------------------------------------------

class VendorMaintenanceSerializer(serializers.ModelSerializer):
    inspection_type = serializers.SlugRelatedField(read_only=True, slug_field='inspection_name')
    asset_type = serializers.SlugRelatedField(read_only=True, source='VIN.equipment_type.asset_type', slug_field='name')
    current_location = serializers.SlugRelatedField(read_only=True, source='VIN.current_location', slug_field='location_name')
    maintenance_location = serializers.SlugRelatedField(read_only=True, source='location', slug_field='location_name')
    created_by = serializers.SlugRelatedField(read_only=True, slug_field='email')
    modified_by = serializers.SlugRelatedField(read_only=True, slug_field='email')
    files = serializers.SerializerMethodField()
    quotes = serializers.SerializerMethodField()

    def get_files(self, maintenance_obj):
        all_files = self.context.get('maintenance_files')
        if all_files:
            relevant_files = []
            for f in all_files:
                if f.get('maintenance_request_id') == maintenance_obj.maintenance_id:
                    relevant_files.append(f)

            return relevant_files
        return []

    def get_quotes(self, maintenance_obj):
        all_quotes = self.context.get('request_quotes')
        if all_quotes:
            relevant_quotes = []
            for quote in all_quotes:
                if quote.get('maintenance_request_id') == maintenance_obj.maintenance_id:
                    relevant_quotes.append(quote)
            return relevant_quotes
        return []
        
    class Meta:
        model = MaintenanceRequestModel
        fields = "__all__"

# --------------------------------------------------------------------------------------------------------

class VendorDisposalSerializer(serializers.ModelSerializer):
    asset_type = serializers.SlugRelatedField(read_only=True, source='VIN.equipment_type.asset_type', slug_field='name')
    manufacturer = serializers.SlugRelatedField(read_only=True, source='VIN.equipment_type.manufacturer', slug_field='name')
    model_number = serializers.SlugRelatedField(read_only=True, source='VIN.equipment_type', slug_field='model_number')
    current_location = serializers.SlugRelatedField(read_only=True, source='VIN.current_location', slug_field='location_name')
    created_by = serializers.SlugRelatedField(read_only=True, slug_field='email')
    modified_by = serializers.SlugRelatedField(read_only=True, slug_field='email')
    files = serializers.SerializerMethodField()
    quotes = serializers.SerializerMethodField()

    def get_files(self, disposal_obj):
        all_files = self.context.get('disposal_files')
        if all_files:
            relevant_files = []
            for f in all_files:
                if f.get('disposal_id') == disposal_obj.id:
                    relevant_files.append(f)
            return relevant_files
        return []

    def get_quotes(self, disposal_obj):
        all_quotes = self.context.get('request_quotes')
        if all_quotes:
            relevant_quotes = []
            for quote in all_quotes:
                if quote.get('disposal_request_id') == disposal_obj.id:
                    relevant_quotes.append(quote)
            return relevant_quotes
        return []

    class Meta:
        model = AssetDisposalModel
        fields = "__all__"

# --------------------------------------------------------------------------------------------------------

class VendorAssetTransferSerializer(serializers.ModelSerializer):
    business_unit = serializers.SlugRelatedField(read_only=True, source='VIN.department', slug_field='name')
    destination_location = serializers.SlugRelatedField(read_only=True, slug_field='location_name')
    transfer_original_location = serializers.SlugRelatedField(read_only=True, source='original_location', slug_field='location_name')
    original_location = serializers.SlugRelatedField(read_only=True, source='VIN.original_location', slug_field='location_name')
    current_location = serializers.SlugRelatedField(read_only=True, source='VIN.current_location', slug_field='location_name')
    created_by = serializers.SlugRelatedField(read_only=True, slug_field='email')
    modified_by = serializers.SlugRelatedField(read_only=True, slug_field='email')
    vendor_name = serializers.SlugRelatedField(read_only=True, source='vendor', slug_field='vendor_name')
    files = serializers.SerializerMethodField('get_files')
    quotes = serializers.SerializerMethodField('get_quotes')
    
    def get_files(self, transfer_obj):
        all_files = self.context.get('transfer_files')
        if all_files:
            relevant_files = []
            for f in all_files:
                if f.get('transfer_id') == transfer_obj.asset_transfer_id:
                    relevant_files.append(f)

            return relevant_files
        return []

    def get_quotes(self, transfer_obj):
        all_quotes = self.context.get('request_quotes')
        if all_quotes:
            relevant_quotes = []
            for quote in all_quotes:
                if quote.get('transfer_request_id') == transfer_obj.asset_transfer_id:
                    relevant_quotes.append(quote)
            return relevant_quotes
        return []
        
    class Meta:
        model = AssetTransfer
        fields = "__all__"
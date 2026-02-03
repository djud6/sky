from django.http import HttpResponse
from rest_framework.response import Response
from rest_framework import status
from api.Models.Cost.parts import Parts
from core.CostManager.CostHelper import PartsHelper, LaborHelper, DeliveryHelper, RentalHelper
from core.RepairManager.RepairHelper import RepairHelper
from core.MaintenanceManager.MaintenanceHelper import MaintenanceHelper
from core.FileManager.FileHelper import FileHelper
from core.UserManager.UserHelper import UserHelper
from core.CompanyManager.CompanyHelper import CompanyHelper
from api.Serializers.serializers import RepairCostExportSerializer, MaintenanceCostExportSerializer
from GSE_Backend.errors.ErrorDictionary import CustomError
import logging

class Logger():
    @staticmethod
    def getLogger():
        return logging.getLogger(__name__)


class CostExport():

    @staticmethod
    def handle_export_work_order_costs(request_data, user):
        try:
            db_name = user.db_access
            detailed_user = UserHelper.get_detailed_user_obj(user.email, db_name)
            repair_ids = request_data.get('repair_ids')
            maintenance_ids = request_data.get('maintenance_ids')
            if repair_ids is None:
                repair_ids = []
            if maintenance_ids is None:
                maintenance_ids = []

            parts_costs = PartsHelper.get_parts_by_maintenance_and_repair_ids(maintenance_ids, repair_ids, db_name)
            parts_costs_list = list(parts_costs.values('issue__repair_id', 'maintenance', 'total_cost', 'taxes'))
            labor_costs = LaborHelper.get_labor_cost_by_maintenance_and_repair_ids(maintenance_ids, repair_ids, db_name)
            labor_costs_list = list(labor_costs.values('issue__repair_id', 'maintenance', 'total_cost', 'taxes'))

            context = {
                'part_costs': parts_costs_list,
                'labor_costs': labor_costs_list,
                'currency_code': CompanyHelper.get_standard_currency_code_by_company_obj(detailed_user.company, db_name)
            }

            repairs_qs = RepairHelper.get_repairs_by_ids(repair_ids, db_name).select_related('VIN', 'VIN__department', 'VIN__equipment_type',
            'VIN__equipment_type__asset_type', 'VIN__equipment_type__manufacturer', 'location', 'created_by')
            repairs_ser = RepairCostExportSerializer(repairs_qs, many=True, context=context)

            maintenance_qs = MaintenanceHelper.get_maintenance_by_ids(maintenance_ids, db_name).select_related('VIN', 'VIN__department', 'VIN__equipment_type',
            'VIN__equipment_type__asset_type', 'VIN__equipment_type__manufacturer', 'location', 'created_by', 'inspection_type')
            maintenance_ser = MaintenanceCostExportSerializer(maintenance_qs, many=True, context=context)

            repair_cost_list = list(repairs_ser.data)
            maintenance_cost_list = list(maintenance_ser.data)
            work_order_cost_list = repair_cost_list + maintenance_cost_list

            return FileHelper.gen_csv_response_from_list_of_dicts(work_order_cost_list, 'work_order_costs.csv')

        except Exception as e:
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.G_0, e))
            return Response(CustomError.get_full_error_json(CustomError.G_0, e), status=status.HTTP_400_BAD_REQUEST)
        
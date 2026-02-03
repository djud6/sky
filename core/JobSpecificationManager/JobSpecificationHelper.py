from rest_framework.response import Response
from rest_framework import status
from api.Models.job_specification import JobSpecification
from GSE_Backend.errors.ErrorDictionary import CustomError
import logging

class Logger():
    @staticmethod
    def getLogger():
        return logging.getLogger(__name__)


class JobSpecificationHelper:

    @staticmethod
    def get_all_job_specification(db_name):
        return JobSpecification.objects.using(db_name).all()

    @staticmethod
    def get_job_specification_by_id(job_spec_id, db_name):
        try:
            return JobSpecification.objects.using(db_name).get(job_specification_id=job_spec_id), Response(status=status.HTTP_302_FOUND)
        except Exception as e:
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.JSDNE_1))
            return None, Response(CustomError.get_full_error_json(CustomError.JSDNE_1), status=status.HTTP_400_BAD_REQUEST)

    @staticmethod
    def get_job_specification_by_name(name, db_name):
        try:
            return JobSpecification.objects.using(db_name).get(name=name), Response(status=status.HTTP_200_OK)
        except Exception as e:
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.JSDNE_1))
            return None, Response(CustomError.get_full_error_json(CustomError.JSDNE_1), status=status.HTTP_400_BAD_REQUEST)
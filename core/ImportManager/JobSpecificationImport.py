from rest_framework.response import Response
from rest_framework import status
from api.Models.job_specification import JobSpecification
from core.JobSpecificationManager.JobSpecificationUpdater import JobSpecificationUpdater
from GSE_Backend.errors.ErrorDictionary import CustomError
import logging

class Logger():
    @staticmethod
    def getLogger():
        return logging.getLogger(__name__)


class JobSpecificationImport():

    @staticmethod
    def import_job_specification_csv(parsed_data, db_name):
        try:
            job_specification_entries = []
            for job_specification_row in parsed_data:
                if not JobSpecification.objects.using(db_name).filter(name=job_specification_row.get("job_specification")).exists():
                    entry = JobSpecificationUpdater.create_job_specification_entry(job_specification_row)
                    job_specification_entries.append(entry)
            JobSpecification.objects.using(db_name).bulk_create(job_specification_entries)
            return Response(status=status.HTTP_201_CREATED)
            
        except Exception as e:
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.CSVUF_13, e))
            return Response(CustomError.get_full_error_json(CustomError.CSVUF_13, e), status=status.HTTP_400_BAD_REQUEST)
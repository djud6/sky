from rest_framework.response import Response
from rest_framework import status
from api.Models.job_specification import JobSpecification
from GSE_Backend.errors.ErrorDictionary import CustomError
import logging

class Logger():
    @staticmethod
    def getLogger():
        return logging.getLogger(__name__)


class JobSpecificationUpdater:

    @staticmethod
    def create_job_specification_entry(job_specification_data):
        return JobSpecification(
            name=job_specification_data.get("job_specification").strip().lower()
        )
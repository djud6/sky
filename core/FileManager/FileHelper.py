from django.http import HttpResponse
from rest_framework.response import Response
from rest_framework import status
import io
import base64
import csv
import zipfile
from io import BytesIO
from django.http import HttpResponse
from django.template.loader import get_template
from xhtml2pdf import pisa
from ..Helper import HelperMethods
from GSE_Backend.errors.ErrorDictionary import CustomError
import logging

class Logger():
    @staticmethod
    def getLogger():
        return logging.getLogger(__name__)

class FileHelper():

        
    # Returns True on success
    @staticmethod
    def write_files_to_disk(files, location):
        try:
            for _file in files:
                with open(location + "\\" + _file.name, 'wb+') as destination:
                    for chunk in _file.chunks():
                        destination.write(chunk)
            return True
        except Exception as e:
            Logger.getLogger().error(e)
            return False

    # -----------------------------------------------------------------------

    # Returns True on success
    @staticmethod
    def write_files_to_server_temp(files):
        try:
            temp_location = str(HelperMethods.GetProjectRoot()) + '\\temp'
            for _file in files:
                with open(temp_location + "\\" + _file.name, 'wb+') as destination:
                    for chunk in _file.chunks():
                        destination.write(chunk)
            return Response(status=status.HTTP_201_CREATED)
        except Exception as e:
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.WFF_0, e))
            return Response(CustomError.get_full_error_json(CustomError.WFF_0, e), status=status.HTTP_400_BAD_REQUEST)

    # -----------------------------------------------------------------------

    @staticmethod
    def file_to_base64(_file):
        try:
            return base64.b64encode(_file).decode('ascii')
        except Exception as e:
            Logger.getLogger().error(e)
            string = base64.b64encode(_file.read()).decode('ascii')
            if(string is not None):
                return string
            return None

    # -----------------------------------------------------------------------
    
    @staticmethod
    def verify_files_are_accepted_types(files, accepted_types):
        for _file in files:
            if(not FileHelper.verify_file_is_accepted_type(_file, accepted_types)):
                return False
        return True    

    @staticmethod
    def verify_file_is_accepted_type(_file, accepted_types):
        if(str(_file.content_type) in accepted_types):
            return True
        else:
            return False

    # -----------------------------------------------------------------------

    @staticmethod
    def GenCSVFile(rows, name): # In memory only
        csvFileByteIO = io.BytesIO()

        try:
            csvFileStrIO = io.StringIO()
            csv.writer(csvFileStrIO).writerows(rows)
            csvFileByteIO.write(csvFileStrIO.getvalue().encode())
            csvFileByteIO.name = name
            return csvFileByteIO, True # OKAY

        except Exception as e:
            Logger.getLogger().error(e)
            return csvFileByteIO, False # SERVER ERROR

    # -----------------------------------------------------------------------

    @staticmethod
    def gen_csv_response_from_list_of_dicts(dict_list, file_name):
        '''
        Expects a list of dictionaries with identical keys. Will use keys as headers.
        Will return csv file http response (make sure that name includes .csv).
        '''
        try:
            rows = [(dict_list[0].keys())] # Adding header row
            for dict in dict_list:
                rows.append(dict.values()) # Adding value rows

            csv_response = HttpResponse(content_type='text/csv', status=status.HTTP_201_CREATED)
            csv_response['Content-Disposition'] = 'attachment; filename="' + file_name + '"'
            writer = csv.writer(csv_response)
            writer.writerows(rows)
            return csv_response

        except Exception as e:
            Logger.getLogger().error(CustomError.get_error_dev(CustomError.CSVF_0, e))
            return Response(CustomError.get_full_error_json(CustomError.CSVF_0, e), status=status.HTTP_400_BAD_REQUEST)

    # -----------------------------------------------------------------------

    @staticmethod
    def GenZipFile(files, name): # In memory only
        zippedFile = io.BytesIO()
        zippedFile.name = name

        try:
            with zipfile.ZipFile(zippedFile, 'w') as zipObj:        
                for f in files:
                    zipObj.writestr(f.name, f.getvalue())
            return zippedFile, True # OKAY

        except Exception as e:
            Logger.getLogger().error(e)
            return zippedFile, False # SERVER ERROR

    # -----------------------------------------------------------------------

    @staticmethod
    def GenCSVResponse(rows, file_name): # Generate a csv HttpResponse
        csv_response = HttpResponse(content_type='text/csv')
        csv_response['Content-Disposition'] = 'attachment; filename="' + file_name + '"'
        writer = csv.writer(csv_response)
        writer.writerows(rows)
        return csv_response

    # -----------------------------------------------------------------------

    @staticmethod
    def GenCSVFileOnDisk(rows, path, file_name): # Generate a csv file on disk
        path = path + file_name
        with open(path, 'w', newline='') as csvFile:
            writer = csv.writer(csvFile)
            writer.writerows(rows) 
            return csvFile

    # -----------------------------------------------------------------------
    
    def render_to_pdf(template_src, context_dict={}):
        template = get_template(template_src)
        html  = template.render(context_dict)
        result = BytesIO()
        pdf = pisa.pisaDocument(BytesIO(html.encode("ISO-8859-1")), result)
        if not pdf.err:
            return HttpResponse(result.getvalue(), content_type='application/pdf')
        return None
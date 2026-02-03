import logging
import tempfile
import os
from os import path
from pathlib import Path
from datetime import date, datetime, timedelta
import calendar
from dateutil.parser import parse
import random
import json
import pytz
import numpy as np
from email_validator import validate_email, EmailNotValidError
from itertools import chain
from math import log10, floor

class Logger():
    @staticmethod
    def getLogger():
        return logging.getLogger(__name__)

class HelperMethods():
    @staticmethod
    # Cover for case sensitivity boolean conversion from URL variable
    def validate_bool(bool_input):
        # if Int type
        if(type(bool_input) == type(1)):
            if bool_input == 1:
                return True
            elif bool_input == 0:
                return False

        # if Bool type
        if(type(bool_input) == type(True)):
            return bool_input

        # if String type
        if(type(bool_input) == type("string")):
            true_strings = ["true", "yes", "1"]
            false_strings = ["false", "no", "0"]
            bool_input = bool_input.lower()      
            if(bool_input in true_strings):
                return True
            elif(bool_input in false_strings):
                return False

        return None

    # -----------------------------------------------------------------------
    @staticmethod
    def check_none_type_obj(obj,*keys):
        try:
            for key in keys:
                if getattr(obj,key) == None:
                    return "NA"
                obj = getattr(obj,key)
            return obj
        except:
            return "NA"

        

    @staticmethod
    def MapCSVHeaders(unmappedDict, headerRow): # Maps column int of header into the header dictionary
        mappedDict = unmappedDict
        count = 0
        for header in headerRow:
            if(header in unmappedDict.keys()):
                mappedDict[header] = count
            count += 1

        return mappedDict

    # -----------------------------------------------------------------------

    @staticmethod
    def WriteUploadFile(uploadedFile): # Writes a file into the SkyIT folder in the windows temp folder
        destinationPath = HelperMethods.GetTempDir() + "\\" + uploadedFile.name
        with open(destinationPath, 'wb+') as destination:
            for chunk in uploadedFile.chunks():
                destination.write(chunk)
        return destinationPath

    # -----------------------------------------------------------------------

    @staticmethod
    def GetTempDir():
        tempDir = tempfile.gettempdir() + "\\SkyIT"
        if(not path.isdir(tempDir)):
            try:
                os.mkdir(tempDir)
            except Exception as e:
                Logger.getLogger().error(e)
            
        return tempDir

    # -----------------------------------------------------------------------

    # Generate CSV row (list) from rest_framework_csv.orderedrows.OrderedRows row
    @staticmethod
    def GenCSVRowFromOrderedRow(headers, row):
        csvRow = list()
        for header in headers:
            csvRow.append(row.get(header))

        return csvRow

    # -----------------------------------------------------------------------

    @staticmethod
    def GetProjectRoot() -> Path:
        return Path(__file__).parent.parent

    # -----------------------------------------------------------------------

    @staticmethod
    def GetCurModuleDir():
        return os.path.dirname(os.path.realpath(__file__))

    # -----------------------------------------------------------------------
    
    @staticmethod
    def ParseDateToDateField(dateString): # Parses an assortment of date formats to YYYY-MM-DD
        candidate = parse(dateString) # YYYY-MM-DD
        candidateString = candidate.strftime('%Y-%m-%d')
        if(HelperMethods.validateDateString(candidateString)):
            return candidateString

        candidate = parse(dateString, yearfirst=True) #YY-MM-DD
        candidateString = candidate.strftime('%Y-%m-%d')
        if(HelperMethods.validateDateString(candidateString)):
            return candidateString

        candidate = parse(dateString, yearfirst=False, dayfirst=False) #MM-DD-YYYY
        candidateString = candidate.strftime('%Y-%m-%d')
        if(HelperMethods.validateDateString(candidateString)):
            return candidateString

        candidate = parse(dateString, dayfirst=True) #DD-MM-YYYY
        candidateString = candidate.strftime('%Y-%m-%d')
        if(HelperMethods.validateDateString(candidateString)):
            return candidateString

        candidate = parse(dateString) #Human-intelligible date
        candidateString = candidate.strftime('%Y-%m-%d')
        if(HelperMethods.validateDateString(candidateString)):
            return candidateString

    # -----------------------------------------------------------------------

    @staticmethod
    def validateDateString(dateString): # Returns true if string conforms to YYYY-MM-DD format
        try:
            datetime.strptime(dateString, '%Y-%m-%d')
            return True
        except Exception:
            return False

    # -----------------------------------------------------------------------

    @staticmethod
    def datetime_string_to_datetime(date_time_str):
        if 'T' in date_time_str and 'Z' in date_time_str:
            return HelperMethods.naive_to_aware_utc_datetime(datetime.strptime(date_time_str, '%Y-%m-%dT%H:%M:%S.%fZ'))
        else:
            return HelperMethods.naive_to_aware_utc_datetime(datetime.strptime(date_time_str, '%Y-%m-%d %H:%M:%S.%f'))

    # ------------------------------------------------------------------------

    @staticmethod
    def date_string_to_datetime(date_string):
        date_string = str(date_string).replace("/", "-")
        return HelperMethods.naive_to_aware_utc_datetime(datetime.strptime(date_string, '%Y-%m-%d'))

    # -----------------------------------------------------------------------
    
    # Converts other date formats to datetime
    @staticmethod
    def to_datetime(input):
        if not isinstance(input, datetime):
            if isinstance(input, str):
                return HelperMethods.date_string_to_datetime(input)
            if isinstance(input, date):
                return HelperMethods.naive_to_aware_utc_datetime(datetime(input.year, input.month, input.day, 0, 0, 0))
        return input

    # -----------------------------------------------------------------------

    # This assumes that input_datetime is UTC
    @staticmethod
    def datetime_is_today(input_datetime):
        return input_datetime.date() == datetime.utcnow().date()

    # -----------------------------------------------------------------------

    # This assumes that datetimes are UTC
    @staticmethod
    def get_datetime_delta(start, end, delta_format="hours"):

        datetime_start = start.replace(tzinfo=None)
        datetime_end = end.replace(tzinfo=None)

        delta = datetime_end - datetime_start
        delta_in_seconds = delta.total_seconds()

        if delta_format == "minutes":
            return divmod(delta_in_seconds, 60)[0]
        if delta_format == "hours":
            return divmod(delta_in_seconds, 3600)[0]
        if delta_format == "days":
            return divmod(delta_in_seconds, 86400)[0]
        
        return delta_in_seconds

    # -----------------------------------------------------------------------
    
    # compare datetime a to datetime b
    @staticmethod
    def datetime_a_later_than_datetime_b(a, b):
        datetime_a = a.replace(tzinfo=None)
        datetime_b = b.replace(tzinfo=None)
        return datetime_a > datetime_b

    # -----------------------------------------------------------------------
    
    @staticmethod
    def date_in_range(date, range_start, range_end):
        date = HelperMethods.to_datetime(date)
        range_start = HelperMethods.to_datetime(range_start)
        range_end = HelperMethods.to_datetime(range_end)

        if date >= range_start and date <= range_end:
            return True
        return False

    # -----------------------------------------------------------------------

    @staticmethod
    def add_time_to_datetime(original_date, time, time_unit="hours"):
        if time_unit == "minutes":
            return original_date + timedelta(minutes=time)
        if time_unit == "hours":
            return original_date + timedelta(hours=time)
        if time_unit == "days":
            return original_date + timedelta(days=time)
        
        return original_date

    # -----------------------------------------------------------------------
    #This method will shift the current due date by a specific integer
    @staticmethod
    def shift_overdue_date(current_due_date, shift_value_in_days):
        
        if(shift_value_in_days is None):
            return current_due_date
        if(shift_value_in_days>=0): #shift is (+)
            
            return current_due_date + timedelta(days=shift_value_in_days)
        else: #shift is (-)
            
            return current_due_date- timedelta(days=shift_value_in_days*-1)
    # -----------------------------------------------------------------------

    @staticmethod
    def subtract_time_from_datetime(original_date, time, time_unit="hours"):
        if time_unit == "minutes":
            return original_date - timedelta(minutes=time)
        if time_unit == "hours":
            return original_date - timedelta(hours=time)
        if time_unit == "days":
            return original_date - timedelta(days=time)
        
        return original_date

    # -----------------------------------------------------------------------

    @staticmethod
    def get_datetime_range_for_today():
        today = datetime.utcnow()
        start_datetime = datetime(today.year, today.month, today.day, 0, 0, 0)
        end_datetime = datetime(today.year, today.month, today.day, 23, 59, 59)
        return HelperMethods.naive_to_aware_utc_datetime(start_datetime), HelperMethods.naive_to_aware_utc_datetime(end_datetime)

    # -----------------------------------------------------------------------

    @staticmethod
    def get_datetime_range_for_yesterday():
        today = datetime.utcnow()
        start_datetime = datetime(today.year, today.month, today.day, 0, 0, 0) - timedelta(days = 1)
        end_datetime = datetime(today.year, today.month, today.day, 23, 59, 59) - timedelta(days = 1)
        return HelperMethods.naive_to_aware_utc_datetime(start_datetime), HelperMethods.naive_to_aware_utc_datetime(end_datetime)

    # -----------------------------------------------------------------------

    @staticmethod
    def get_datetime_range_for_this_week():
        today = datetime.utcnow()
        start_datetime = today - timedelta(days=today.weekday())
        start_datetime = datetime(start_datetime.year, start_datetime.month, start_datetime.day, 0, 0, 0)
        end_datetime = start_datetime + timedelta(days=6)
        end_datetime = datetime(end_datetime.year, end_datetime.month, end_datetime.day, 23, 59, 59)
        return HelperMethods.naive_to_aware_utc_datetime(start_datetime), HelperMethods.naive_to_aware_utc_datetime(end_datetime)
 
    # -----------------------------------------------------------------------

    @staticmethod
    def get_datetime_range_for_this_month():
       today = datetime.utcnow()
       start_datetime = datetime(today.year, today.month, 1, 0, 0, 0)
       last_day_this_month = calendar.monthrange(today.year, today.month)[1]
       end_datetime = datetime(today.year, today.month, last_day_this_month, 23, 59, 59)   
       return HelperMethods.naive_to_aware_utc_datetime(start_datetime), HelperMethods.naive_to_aware_utc_datetime(end_datetime)
        
    # -----------------------------------------------------------------------

    # Expects datetime object
    @staticmethod
    def naive_to_aware_utc_datetime(naive_datetime):
        aware_datetime = naive_datetime.replace(tzinfo=None)
        aware_datetime = pytz.utc.localize(aware_datetime)
        return aware_datetime

    # -----------------------------------------------------------------------

    @staticmethod
    def aware_utc_to_naive_datetime(aware_datetime):
        return aware_datetime.replace(tzinfo=None)

    # -----------------------------------------------------------------------

    # Generates random number within a specified percentage of a value
    @staticmethod
    def random_num_around_val(value, percentage):
        lower_bound = value - (value * (percentage/100))
        upper_bound = value + (value * (percentage/100))
        return random.randint(lower_bound, upper_bound)

    # -----------------------------------------------------------------------

    def round_to_sig_digs(number, significant):
        '''
        Input a number and the significant digits you want to round to.
        '''
        return round(number, significant - int(floor(log10(abs(number)))) - 1)

    # -----------------------------------------------------------------------
    
    # Converts JSON string to a Dictionary
    @staticmethod
    def json_str_to_dict(json_string):
        return json.loads(json_string)

    # -----------------------------------------------------------------------

    # Django model object to Dictionary
    # FROM: https://stackoverflow.com/questions/21925671/convert-django-model-object-to-dict-with-all-of-the-fields-intact
    @staticmethod
    def django_model_obj_to_dict(obj):
        opts = obj._meta
        data = {}
        for f in chain(opts.concrete_fields, opts.private_fields):
            data[f.name] = f.value_from_object(obj)
        for f in opts.many_to_many:
            data[f.name] = [i.id for i in f.value_from_object(obj)]
        return data

    # -----------------------------------------------------------------------

    @staticmethod
    def replace_substring(original_string, start_substring, end_substring, replacement_substring):
        '''
        Replaces the start-end substrings including everything in between
        with the replacement substring.
        '''
        if start_substring not in original_string or end_substring not in original_string:
            return original_string
    
        start_index = original_string.find(start_substring)
        end_index = original_string.find(end_substring, start_index + len(start_substring))

        if start_index != -1 and end_index != -1:
            new_string = original_string[:start_index] + replacement_substring + original_string[end_index:]
            while start_index != -1:
                start_index = new_string.find(start_substring, start_index + len(replacement_substring))
                if start_index != -1:
                    end_index = new_string.find(end_substring, start_index + len(start_substring)) + len(end_substring)
                    new_string = new_string[:start_index] + replacement_substring + new_string[end_index:]
            return new_string
        else:
            return original_string

    # -----------------------------------------------------------------------
    
    # Create string with delimiter from native elements list
    @staticmethod
    def list_to_delimited_string(native_list, delimiter):
        final_string = ""
        for element in native_list:
            final_string = final_string + str(delimiter) + str(element)
        return HelperMethods.remove_prefix(final_string, delimiter)

    # -----------------------------------------------------------------------

    # Create string list from delimited string
    @staticmethod
    def delimited_string_to_list(string, delimiter):
        return string.split(delimiter)

    # -----------------------------------------------------------------------

    # Remove prefix from string
    @staticmethod
    def remove_prefix(text, prefix):
        if text.startswith(prefix):
            return text[len(prefix):]
        return text

    # -----------------------------------------------------------------------

    @staticmethod
    def is_valid_date_range(start, end):
        start_date = HelperMethods.ParseDateToDateField(start)
        end_date = HelperMethods.ParseDateToDateField(end)

        if start_date <= end_date:
            return True
        else:
            return False

    # -----------------------------------------------------------------------
 
    @staticmethod
    def name_from_end_of_url(url, delimiter):
        name = url.split(delimiter)[-1]
        name = name.replace(delimiter, "")
        name = name.replace("\\", "")
        name = name.replace("/", "")
        return name

    # -----------------------------------------------------------------------
    
    @staticmethod
    def verify_email_address(email):
        try:
            # Validate.
            valid = validate_email(email)
            # Update with the normalized form.
            email = valid.email
            return True, ""

        except EmailNotValidError as e:
            # email is not valid, exception message is human-readable
            return False, str(e)

    # ------------------------------------------------------------------------
        
    # Turn list of tuples into list of comma delimited strings
    @staticmethod
    def tuple_list_to_string_list(tuple_list):
        string_list = []
        for tpl in tuple_list:
            string = str(tpl)
            string = string.replace("'", "").replace(")", "").replace("(", "")
            string_list.append(string)
        return string_list

    # ------------------------------------------------------------------------

    @staticmethod
    def combine_lists_and_elim_duplicates(lists):
        final_list = []
        for cur_list in lists:

            if len(final_list) < 1:
                final_list = cur_list
                continue

            in_first = set(final_list)
            in_second = set(cur_list)
            in_second_but_not_in_first = in_second - in_first
            final_list = final_list + list(in_second_but_not_in_first)

        return final_list

    # ------------------------------------------------------------------------

    # Returns true if num_a is within x percent of num_b
    @staticmethod
    def a_within_x_percent_of_b(num_a, num_b, percent_tolerance):
        tolerance = percent_tolerance / 100
        lower_bound = num_b - (num_b * tolerance)
        upper_bound = num_b + (num_b * tolerance)
        if lower_bound <= num_a <= upper_bound:
            return True
        return False

    # ------------------------------------------------------------------------
    
     # Returns true if num_a is x percent greater than num_b
    @staticmethod
    def a_within_x_percent_greater_than_b(num_a, num_b, percent_tolerance):
        tolerance = percent_tolerance / 100
        upper_bound = num_b + (num_b * tolerance)
        if num_a <= upper_bound:
            return True
        return False

    # ------------------------------------------------------------------------

    @staticmethod
    def extract_tuple_list_from_tuple_list(tuple_list, desired_indices):
        extracted_list = []
        for element in tuple_list:
            temp_list = []
            for index in desired_indices:
                temp_list.append(element[index])
            extracted_list.append(tuple(temp_list))
        return extracted_list

    # ------------------------------------------------------------------------

    @staticmethod
    def delete_list_from_list(list_a, list_b):
        '''
        Remove list b from list a.
        '''
        return [elem for elem in list_a if elem not in list_b]

    # ------------------------------------------------------------------------

    @staticmethod
    def string_to_integer_with_default(input_string):
        if input_string.isnumeric():
            return int(input_string)
        return -1

    # ------------------------------------------------------------------------

    @staticmethod
    def get_unique_values_from_list(original_list):
        return np.unique(np.array(original_list))

    # ------------------------------------------------------------------------

    @staticmethod
    def extract_dict_from_multidim_list(source_list, key_index, value_index):
        result_dict = {}
        for row in source_list:
            result_dict[row[key_index]] = row[value_index]
        return result_dict

    # ------------------------------------------------------------------------

    @staticmethod
    def verify_obj_types(objects, types):
        '''
        Returns True if all objects are of a type inside types (a, b, c).
        '''
        for obj in objects:
            if isinstance(obj, types):
                continue
            return False
        return True

    # ------------------------------------------------------------------------

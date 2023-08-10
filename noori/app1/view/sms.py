from django.shortcuts                         import render
from rest_framework.views                     import APIView
from rest_framework                           import status
from rest_framework.response                  import Response
from django.contrib.auth                      import authenticate
from django.contrib.auth.models               import update_last_login
from rest_framework.authtoken.models          import Token
import json
from rest_framework.exceptions                import APIException
from django.db.models                         import Q
from rest_framework.parsers                   import FileUploadParser
from ..utils.response                         import permission_response, error_response, result_response
from ..utils.utilities                        import remove_from_list, get_param_filter
import os
from django.core.files.storage                import default_storage
from django.core.files.base                   import ContentFile
from django.conf                              import settings
import pandas                                 as pd 
import requests 
import json 
import numpy                                  as np
from ..utils.link                             import BASE_URL
from django.core.files.storage                import FileSystemStorage
import uuid
from ..models                                 import Product
import                                        pandas as pd
import                                        datetime
from                                          tabulate import tabulate
from sklearn.cluster                          import KMeans
from persiantools.jdatetime                   import JalaliDate
import                                        requests
from .sms_info                                import sms_line, sms_username, sms_password

class GetCredit(APIView):

    def post(self, request): 
        owner        = self.request.user  
        if not 1:
            response_data = permission_response()
            return Response(response_data, status = status.HTTP_200_OK)
        else:
            ver = 0
            seq = 1
            url = "https://rest.payamak-panel.com/api/SendSMS/GetCredit"
            try:
                
                message = "GetCredit information"
                data  = {"username": sms_username, "password": sms_password}
                response = requests.post(url, json=data)
                # convert datafram to json
                results= response.json()
                response_data = result_response(ver, seq, message, results)
                data_status = status.HTTP_200_OK    
                return Response(response_data, status = data_status)
            except Exception as e:
                response_data = error_response(ver,seq,e)
                data_status = status.HTTP_200_OK    


class GetBasePrice(APIView):

    def post(self, request): 
        owner        = self.request.user  
        if not 1:
            response_data = permission_response()
            return Response(response_data, status = status.HTTP_200_OK)
        else:
            ver = 0
            seq = 1
            url = "https://rest.payamak-panel.com/api/SendSMS/GetBasePrice"
            try:
                
                message = "GetBasePrice information"
                data  = {"username": sms_username, "password": sms_password}
                response = requests.post(url, json=data)
                # convert datafram to json
                results= response.json()
                response_data = result_response(ver, seq, message, results)
                data_status = status.HTTP_200_OK    
                return Response(response_data, status = data_status)
            except Exception as e:
                response_data = error_response(ver,seq,e)
                data_status = status.HTTP_200_OK  


class GetMessages(APIView):

    def post(self, request): 
        owner        = self.request.user  
        if not 1:
            response_data = permission_response()
            return Response(response_data, status = status.HTTP_200_OK)
        else:
            ver = 0
            seq = 1
            url = "https://rest.payamak-panel.com/api/SendSMS/GetMessages"
            try:
                json_data     = json.loads(request.body)
                count = int(json_data['params'].get('count', 10)) # max is 100
                location = int(json_data['params'].get('type', 1)) # if 1 recived sms and if 2 sent sms
                index    = int(json_data['params'].get('index', 0))

                message = "Get Messages"
                data  = {"username": sms_username, "password": sms_password, "location": location,
                        "count": count, "index":index
                            }
                response = requests.post(url, json=data)
                # convert datafram to json
                results= response.json()
                response_data = result_response(ver, seq, message, results)
                data_status = status.HTTP_200_OK    
                return Response(response_data, status = data_status)
            except Exception as e:
                response_data = error_response(ver,seq,e)
                data_status = status.HTTP_200_OK  


class SendSMS(APIView):

    def post(self, request): 
        owner        = self.request.user  
        if not 1:
            response_data = permission_response()
            return Response(response_data, status = status.HTTP_200_OK)
        else:
            ver = 0
            seq = 1
            url = "https://rest.payamak-panel.com/api/SendSMS/SendSMS"
            try:
                json_data     = json.loads(request.body)
                to = str(json_data['params'].get('to', "09907423017")) # you can seperate by ,
                text    = str(json_data['params'].get('text', "my text"))


                message = "send A Message"
                data  = {"username": sms_username, "password": sms_password, "to": to,
                        "from": sms_line, "text":text
                            }
                print(data)
                response = requests.post(url, json=data)
                # convert datafram to json
                results= response.json()
                response_data = result_response(ver, seq, message, results)
                data_status = status.HTTP_200_OK    
                return Response(response_data, status = data_status)
            except Exception as e:
                response_data = error_response(ver,seq,e)
                data_status = status.HTTP_200_OK  

# curl   -F "userid=1"   -F "filecomment=This is an image file"   -F "file=@/mnt/c/Users/mohammad/Desktop/vpn.txt"   http://127.0.0.1:8000/api/import_excel/


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
from ..models                                 import Product, Customer
import                                        datetime
from persiantools.jdatetime                   import JalaliDate
from django.db.models import Avg, Count
import math


def convert(obj):
    if isinstance(obj, (np.int_, np.intc, np.intp, np.int8,
                            np.int16, np.int32, np.int64, np.uint8,
                            np.uint16, np.uint32, np.uint64, int)):
        return int(obj)

    elif isinstance(obj, (np.float_, np.float16, np.float32, np.float64, float)):
        return float(obj)
    else:
        return obj

def get_value(obj):
    try:
        if obj:
            print("test")
            return obj
    except:
        return None

class ImportExcelView(APIView):

    def post(self, request): 
        owner        = self.request.user  
        if not 1:
            response_data = permission_response()
            return Response(response_data, status = status.HTTP_200_OK)
        else:
            ver = 0
            seq = 6
            try:
                param_dict = {
                    "owner":owner
                }
                if not os.path.exists('media'):
                    os.makedirs('media')
                if not os.path.exists(f'media/userFiles/{owner}'):
                    os.makedirs(f'media/userFiles/{owner}')

                
                excel_file              = request.FILES.get('file', 0)
                excel_id                = str(uuid.uuid4())
                param_dict['excel_id'] = excel_id
                if excel_file:
                    fs = FileSystemStorage()
                    ext      = excel_file.name.split('.')[-1]              # Seprate the file ext.
                    filename = "%s.%s" % (str(uuid.uuid4()), ext) 
                    filename = os.path.join(f"userFiles/{owner}/{filename}")
                    filename = fs.save(filename, excel_file)
                    excel_file = os.path.join(settings.MEDIA_ROOT, filename)
                    param_dict['excel_path']  =excel_file
                


                try:
                    data = pd.read_excel(open(excel_file, 'rb'))
                except: 
                    data = pd.read_csv(open(excel_file, 'rb'))
                data = data.where(pd.notnull(data), None)          

                # for i in Product.objects.all():
                #     obj = Product.objects.get(id=i.id)
                #     obj.delete()
                count_of_data = 0
                for i in range(len(data)):
                    date_jalali = data['date_jalali'][i].split('T')[0].split('-')
                    invoice_id              = data['invoice_id'][i]
                    param_dict['invoice_id']  = invoice_id
                    item_id                 = data['item_id'][i]
                    param_dict['item_id']  = item_id
                    customer_id             = data['customer_id'][i]
                    param_dict['customer_id']  = customer_id
                    try:
                        date_jalali             = datetime.datetime.fromisoformat(
                            str(JalaliDate(int(date_jalali[0]), int(date_jalali[1]), int(date_jalali[2])).to_gregorian())
                            ) 
                        param_dict['date_jalali']  = date_jalali
                    except Exception as e:
                        print(data['date_jalali'][i])
                        print(e)
                        date_jalali = None
                    
                    unit_price              = int(convert(data['unit_price'][i]))
                    param_dict['unit_price']  = unit_price
                    quantity                = int(convert(data['quantity'][i]))
                    param_dict['quantity']  = quantity
                    customer_name           = data['customer_name'][i]
                    param_dict['customer_name']  = customer_name
                    customer_gender         = data['customer_gender'][i]
                    param_dict['customer_gender']  = customer_gender
                    customer_birthday       = data['customer_birthday'][i]
                    param_dict['customer_birthday']  = customer_birthday

                    try:
                        customer_birthday = customer_birthday.split('T')[0].split('-')
                        customer_birthday             = datetime.datetime.fromisoformat(
                            str(JalaliDate(int(customer_birthday[0]), int(customer_birthday[1]),
                             int(customer_birthday[2])).to_gregorian())
                            )  
                        days_in_year = 365.2425
                        age = int((datetime.date.today() - customer_birthday).days / days_in_year)
                    except:
                        age = 0

                    param_dict['age']  = age
         
                    customer_phone_number   = data['customer_phone_number'][i]
                    param_dict['customer_phone_number']  = customer_phone_number
                    try:
                        date                    = data['date'][i]
                    except:
                        date                    = None
                    try:
                        sales_channel           = data['sales_channel'][i]
                        param_dict['sales_channel']  = sales_channel
                    except:
                        sales_channel           = None
                    try: 
                        region                  = data['region'][i]
                        param_dict['region']  = region
                    except:
                        region                  = None
                    try:
                        city                    = data['city'][i]
                        param_dict['city']  = city
                    except:
                        city                    = None
                    try:
                        country                 = data['country'][i]
                        param_dict['country']  = country
                    except:
                        country                 = None
                    try:
                        sku_id                  = data['sku_id'][i]
                        param_dict['sku_id']  = sku_id
                    except:
                        sku_id = None
                    try:
                        product_name            = data['product_name'][i]
                        param_dict['product_name']  = product_name
                    except:
                        product_name = None
                    try:
                        product_brand           = data['product_brand'][i]
                        param_dict['product_brand']  = product_brand
                    except:
                        product_brand = None
                    try:
                        product_category        = data['product_category'][i]
                        param_dict['product_category']  = product_category
                    except:
                        product_category = None
                    try:
                        invoice_type            = data['invoice_type'][i]
                        param_dict['invoice_type']  = invoice_type
                    except:
                        invoice_type = None
                    try:
                        product_type            = data['product_type'][i]
                        param_dict['product_type']  = product_type
                    except:
                        product_type = None
                
                    try:
                        email            = data['email'][i]
                        param_dict['email']  = email
                    except:
                        email = ""

                    if data['commission'][i] and not math.isnan(data['commission'][i]):
                        commission              = convert(data['commission'][i])
                        param_dict['commission']  = commission
                    else:
                        commission = 0
                        param_dict['commission']  = 0
                        
                    if data['discount'][i] and not math.isnan(data['discount'][i]):
                        discount                = convert(data['discount'][i])
                        param_dict['discount']  = discount
                    else:
                        discount = 0
                        param_dict['discount']  = 0

                    if data['weight'][i] and not math.isnan(data['weight'][i]):
                        weight                  = convert(data['weight'][i])
                        param_dict['weight']  = weight
                    else:
                        weight = 0
                        param_dict['weight']  = 0

                    if data['credit_payment_amount'][i] and not math.isnan(data['credit_payment_amount'][i]):
                        credit_payment_amount   = convert(data['credit_payment_amount'][i])
                        param_dict['credit_payment_amount']  = credit_payment_amount
                    else:
                        credit_payment_amount = 0
                        param_dict['credit_payment_amount']  = 0

                    product_obj = Product(**param_dict)
                    product_obj.save()
                    # print(param_dict)
                    count_of_data += 1

                    if not Customer.objects.filter(owner=owner, customer_id=customer_id).exists(): 
                        customer_obj = Customer(owner=owner, customer_id=customer_id)
                        customer_obj.save()
                message = f"all rows saved in file with id {excel_id} and count of data is: {count_of_data}"
                print(message) 
                response_data = result_response(ver, seq, message)
                data_status = status.HTTP_200_OK    
                return Response(response_data, status = data_status)
            except Exception as e:
                response_data = error_response(ver,seq,e)
                data_status = status.HTTP_200_OK    
                return Response(response_data, status = data_status)


class SampleFileView(APIView):

    def post(self, request): 
        owner        = self.request.user  
        if not 1:
            response_data = permission_response()
            return Response(response_data, status = status.HTTP_200_OK)
        else:
            ver = 0
            seq = 6
            try:
                if not os.path.exists('media'):
                    os.makedirs('media')
                

                message = f"a sample file" 
                results = {
                    "link": os.path.join("media", "sample", "sample.xlsx")
                }
                response_data = result_response(ver, seq, message, results)
                data_status = status.HTTP_200_OK    
                return Response(response_data, status = data_status)
            except Exception as e:
                response_data = error_response(ver,seq,e)
                data_status = status.HTTP_200_OK    
                return Response(response_data, status = data_status)
            


class ListImportExcelView(APIView):

    def post(self, request): 
        owner        = self.request.user 
        ver = 0
        seq = 6
        try:
            product_obj = Product.objects.filter(owner=owner).values('excel_id').annotate(Count('id')).order_by()
            results = {}
            for product in product_obj:
                time = Product.objects.filter(owner=owner, excel_id=product['excel_id'])
                results[product['excel_id']] = {
                    "count": product['id__count'], 
                    "time": time[0].created_at
                }
                
            print(results)
            message = f"list of excel files"
            response_data = result_response(ver, seq, message, results)
            data_status = status.HTTP_200_OK    
            return Response(response_data, status = data_status)
        except Exception as e:
            response_data = error_response(ver,seq,e)
            data_status = status.HTTP_200_OK    
            return Response(response_data, status = data_status)



class RemoveExcelView(APIView):

    def post(self, request): 
        owner        = self.request.user 
        ver = 0
        seq = 6
        try:
            excel_id = request.data.get('excel_id', '0')
            product_obj = Product.objects.filter(owner=owner, excel_id=excel_id)
        
            for product in product_obj:
                product.delete()

            message = f"all data with excel_id {excel_id} is removed"
            response_data = result_response(ver, seq, message)
            data_status = status.HTTP_200_OK    
            return Response(response_data, status = data_status)
        except Exception as e:
            response_data = error_response(ver,seq,e)
            data_status = status.HTTP_200_OK    
            return Response(response_data, status = data_status)


class DownloadExcelView(APIView):

    def post(self, request): 
        owner        = self.request.user 
        ver = 0
        seq = 6
        try:
            excel_id = request.data.get('excel_id', '0')
            product_obj = Product.objects.filter(owner=owner, excel_id=excel_id)
            csv_name = product_obj[0].excel_path.split('/')[-1]

            results = {
                    "csv_path": os.path.join("media", "userFiles", owner.username , csv_name)
                }
            
            print(results)

            message = f"Excel file path"

            response_data = result_response(ver, seq, message, results)
            data_status = status.HTTP_200_OK    
            return Response(response_data, status = data_status)
        except Exception as e:
            response_data = error_response(ver,seq,e)
            data_status = status.HTTP_200_OK    
            return Response(response_data, status = data_status)

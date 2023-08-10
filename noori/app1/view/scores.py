# curl   -F "userid=1"   -F "filecomment=This is an image file"   -F "file=@/mnt/c/Users/mohammad/Desktop/vpn.txt"   http://127.0.0.1:8000/api/import_excel/
# https://guillaume-martin.github.io/rfm-segmentation-with-python.html

from urllib3 import Retry
from numpy import interp

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
import                                        lifetimes
from datetime                                 import timedelta, datetime
from .utils                                   import convert_date, get_result, convert_to_list_per_keys
from .score_utils                             import get_rfm_score
from .utils                                   import rejected_factor_count, average_customer_liftime
from .utils                                   import factor_amount_average, retention, handle_none_value
from .utils                                   import share_shoping, retention_seperation, average_purchase_count, pure_sale
from django.db.models                         import Avg, Count, Sum, F
from django.db.models.functions               import Cast
from django.db.models                         import IntegerField, CharField
from django.db.models import Value
from django.db.models.functions import Concat
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from sklearn.preprocessing import LabelEncoder
from surprise import Dataset
from surprise import Reader
from operator import itemgetter
from .utils   import users_count, sale_factor_count, gross_sale
from ..models import Config, DisplayConfig
import ast
import json
import statistics





class UserTableView(APIView):

    def post(self, request): 
        owner        = self.request.user  
        if not 1:
            response_data = permission_response()
            return Response(response_data, status = status.HTTP_200_OK)
        else:
            json_data     = json.loads(request.body)
            ver = 0
            seq = 6
            segment = int(json_data['params'].get('segments', 11)) 
            start_date1 = json_data['params'].get('start_date1', 0)
            end_date1   = json_data['params'].get('end_date1', 0)
            start_date_miladi1 = convert_date(start_date1)
            end_date_miladi1   = convert_date(end_date1)

            try:
                products = Product.objects.filter(owner=owner,
                        date_jalali__lte= end_date_miladi1, date_jalali__gt=start_date_miladi1)

                results = {}
                index = f"type_{segment}"
                value_lists = list(set(products.values_list(index, flat=True)))
                for value in value_lists:
                    my_filter = Q()
                    my_or_filters = {index:value}
                    for item in my_or_filters:
                        my_filter |= Q(**{item:my_or_filters[item]})
                    results[value] = products.filter(my_filter).values_list('customer_id', flat=True).distinct().count()


                df = pd.DataFrame(list(products.values()))
                rfm_df = get_rfm_score(df, segment)
                message = "table scores  "  
                 
                all_users = len(set(rfm_df['customer_id']))
     
                out_results = [
                        {
                            "label": "all customers",
                            "user_count": all_users,
                            "index_frequency": sum(rfm_df['F'])/all_users,
                            "index_recency": sum(rfm_df['R'])/all_users,
                            "index_monetary": sum(rfm_df['M'])/all_users
                        }
                ]

                for u_type in set(rfm_df['Customer_segment']):
                    filter_df  = rfm_df[(rfm_df.Customer_segment == u_type)]
                    user_count = len(set(filter_df['customer_id']))
                    out_results.append(
                        {
                            "label": u_type,
                            "user_count":user_count ,
                            "index_frequency": sum(filter_df['F'])/user_count,
                            "index_recency": sum(filter_df['R'])/user_count,
                            "index_monetary": sum(filter_df['M'])/user_count   
                        }
                    )

                                                    
                response_data = result_response(ver, seq, message, out_results)
                data_status = status.HTTP_200_OK    
                return Response(response_data, status = data_status)
            except Exception as e:
                response_data = error_response(ver,seq,e)
                data_status = status.HTTP_200_OK    
                return Response(response_data, status = data_status)




class RFMView(APIView):

    def post(self, request): 
        owner        = self.request.user  
        if not 1:
            response_data = permission_response()
            return Response(response_data, status = status.HTTP_200_OK)
        else:
            json_data     = json.loads(request.body)
            ver = 0
            seq = 6
            segment = int(json_data['params'].get('segments', 11)) 
            start_date1 = json_data['params'].get('start_date1', 0)
            end_date1   = json_data['params'].get('end_date1', 0)
            start_date_miladi1 = convert_date(start_date1)
            end_date_miladi1   = convert_date(end_date1)

            try:
                products = Product.objects.filter(owner=owner,
                        date_jalali__lte= end_date_miladi1, date_jalali__gt=start_date_miladi1)

                results = {}
                index = f"type_{segment}"
                value_lists = list(set(products.values_list(index, flat=True)))
                for value in value_lists:
                    my_filter = Q()
                    my_or_filters = {index:value}
                    for item in my_or_filters:
                        my_filter |= Q(**{item:my_or_filters[item]})
                    results[value] = products.filter(my_filter).values_list('customer_id', flat=True).distinct().count()

                message = "rfm scores  "  
                out_results = [] 
                count_of_users = sum(list(results.values()))
                
                all_factor_count = sale_factor_count(products)['sale_factor_count']
                segmet_sale_factor_count = sale_factor_count(products, f"type_{segment}")
                all_income = gross_sale(products)['gross_sale']
                segment_income = gross_sale(products, f"type_{segment}")
                for k,v in results.items():
                    out_results.append({"label":k,
                                        "user_count": v,
                                        "user_percentage":float(v/count_of_users),
                                        "factor_count": segmet_sale_factor_count.get(k, 0),
                                        "factor_percentage": segmet_sale_factor_count.get(k, 0)/all_factor_count,
                                        "income": segment_income.get(k, 0),
                                        "income_percentage": segment_income.get(k, 0)/all_income
                                        }) 

                                                    
                response_data = result_response(ver, seq, message, out_results)
                data_status = status.HTTP_200_OK    
                return Response(response_data, status = data_status)
            except Exception as e:
                response_data = error_response(ver,seq,e)
                data_status = status.HTTP_200_OK    
                return Response(response_data, status = data_status)



def get_graph_table_segment_data(products, segment):

    if len(products) == 0:
        out_results = [[], []]    
        return out_results
    results = {}
    index = f"type_{segment}"
    value_lists = list(set(products.values_list(index, flat=True)))
    for value in value_lists:
        my_filter = Q()
        my_or_filters = {index:value}
        for item in my_or_filters:
            my_filter |= Q(**{item:my_or_filters[item]})
        results[value] = products.filter(my_filter).values_list('customer_id', flat=True).distinct().count()

    out_results = [] 
    count_of_users = sum(list(results.values()))
    
    all_factor_count = sale_factor_count(products)['sale_factor_count']
    segmet_sale_factor_count = sale_factor_count(products, f"type_{segment}")
    all_income = gross_sale(products)['gross_sale']
    segment_income = gross_sale(products, f"type_{segment}")
    for k,v in results.items():
        out_results.append({"label":k,
                            "user_count": v,
                            "user_percentage":round(float(v/count_of_users), 2),
                            "factor_count": handle_none_value(segmet_sale_factor_count.get(k, 0)),
                            "factor_percentage": round(handle_none_value(segmet_sale_factor_count.get(k, 0))/all_factor_count, 2),
                            "income": handle_none_value(segment_income.get(k, 0)),
                            "income_percentage": round(handle_none_value(segment_income.get(k, 0))/all_income, 2)
                            }) 
        
    summery_result = [
        {"label":"کل مشتریان",
            "user_count": sum([item['user_count'] for item in out_results]),
            "factor_count": round(sum([item['factor_count'] for item in out_results])/len(out_results), 2),
            "income": round(sum([item['income'] for item in out_results])/len(out_results), 2),
        }
    ]
        
    out_results = [out_results, summery_result]    
    return out_results


class RFMVSegmentsView(APIView):


    def post(self, request): 
        owner        = self.request.user  
        if not 1:
            response_data = permission_response()
            return Response(response_data, status = status.HTTP_200_OK)
        else:
            ver = 0
            seq = 6
            display_conf = DisplayConfig.objects.get_or_create(owner=owner)
            seg_conf = Config.objects.get_or_create(owner=owner)
            segment = seg_conf[0].segment
            day_ebfor = display_conf[0].period_time if display_conf[0].period_time else 1000

            start_date_miladi1 = datetime.now() - timedelta(days=day_ebfor)
            
            end_date_miladi1   = datetime.now()

            try:
                products = Product.objects.filter(owner=owner, invoice_type='SALES',
                        date_jalali__lte= end_date_miladi1, date_jalali__gt=start_date_miladi1)
                
                out_results = get_graph_table_segment_data(products, segment)  
                message = "rfm scores  "  
                response_data = result_response(ver, seq, message, out_results)
                data_status = status.HTTP_200_OK    
                return Response(response_data, status = data_status)
            except Exception as e:
                response_data = error_response(ver,seq,e)
                data_status = status.HTTP_200_OK    
                return Response(response_data, status = data_status)



class RFMVSegmentsDownloadView(APIView):

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

                if not os.path.exists( os.path.join("media", "temp")):
                    os.makedirs(os.path.join("media", "temp"))

                # creating file
                out_path = os.path.join("media", "temp", str(uuid.uuid4())+'.csv')
                
                display_conf = DisplayConfig.objects.get_or_create(owner=owner)
                seg_conf = Config.objects.get_or_create(owner=owner)
                segment = seg_conf[0].segment
                day_ebfor = display_conf[0].period_time if display_conf[0].period_time else 1000

                start_date_miladi1 = datetime.now() - timedelta(days=day_ebfor)
                
                end_date_miladi1   = datetime.now()
                products = Product.objects.filter(owner=owner, invoice_type='SALES',
                        date_jalali__lte= end_date_miladi1, date_jalali__gt=start_date_miladi1)

                download_type = request.data.get('download_type', 'data')
                
                if download_type == 'data':

                    df = pd.DataFrame(list(products.values()))
                    df.to_csv(out_path)
                elif download_type == 'table':
                    out_results = get_graph_table_segment_data(products, segment)
                    df = pd.DataFrame(out_results[1] + out_results[0])
                    df.to_csv(out_path)
                elif download_type == 'graph':
                    out_results = get_graph_table_segment_data(products, segment)
                    df = pd.DataFrame(out_results[0])
                    df.to_csv(out_path)
                elif download_type == "کل مشتریان":
                    df = pd.DataFrame(list(products.values()))
                    df.to_csv(out_path)
                else:
                    index = f"type_{segment}"
                    my_filter = Q()
                    my_or_filters = {index:download_type}
                    for item in my_or_filters:
                        my_filter |= Q(**{item:my_or_filters[item]})
                    products = products.filter(my_filter)
                    df = pd.DataFrame(list(products.values()))
                    df.to_csv(out_path)

                message = f"downlod file" 
                results = {
                    "link": out_path
                }
                response_data = result_response(ver, seq, message, results)
                data_status = status.HTTP_200_OK    
                return Response(response_data, status = data_status)
            except Exception as e:
                response_data = error_response(ver,seq,e)
                data_status = status.HTTP_200_OK    
                return Response(response_data, status = data_status)

class GetItemProducts(APIView):
    def post(self, request): 
        owner        = self.request.user  
        if not 1:
            response_data = permission_response()
            return Response(response_data, status = status.HTTP_200_OK)
        else:
            ver = 0
            seq = 6

            try:
                name = request.data.get('name') 
                products = Product.objects.filter(owner=owner).values(name).distinct()
                products = ["انتخاب کنید"] + [item[name]  for item in products if item[name] != "nan" and item[name]]
                # convert datafram to json
                message = "configs infos "
                response_data = result_response(ver, seq, message, products)
                data_status = status.HTTP_200_OK    
                return Response(response_data, status = data_status)
            except Exception as e:
                response_data = error_response(ver,seq,e)
                data_status = status.HTTP_200_OK    
                return Response(response_data, status = data_status)
            
        

class GetConfigView(APIView):
    def post(self, request): 
        owner        = self.request.user  
        if not 1:
            response_data = permission_response()
            return Response(response_data, status = status.HTTP_200_OK)
        else:
            ver = 0
            seq = 6

            try:
                
                config = Config.objects.filter(owner=owner)
                if len(config) == 0:
                    config_param = {}
                    config_param['segment'] =  11
                    config_param['outlayer'] =  0  
                    config_param['recency1'] =  20 
                    config_param['recency2'] = 40  
                    config_param['recency3'] = 60  
                    config_param['recency4'] =80 
                    config_param['frequency1'] = 20 
                    config_param['frequency2'] = 40  
                    config_param['frequency3'] =  60  
                    config_param['frequency4'] =  80
                    config_param['monetary1'] =  20 
                    config_param['monetary2'] =  40 
                    config_param['monetary3'] = 60 
                    config_param['monetary4'] = 80  
                    config_param['frequncy_type'] = 'factor_count'
                    config_param['recency_type'] = 'pure_sale'  


                else:
                    config_param = {}
                    config_param['segment'] = int(config[0].segment)
                    config_param['outlayer'] =  int(config[0].outlayer)
                    config_param['recency1'] = int(config[0].recency1)
                    config_param['recency2'] =  int(config[0].recency2)  
                    config_param['recency3'] = int(config[0].recency3)   
                    config_param['recency4'] = int(config[0].recency4)  
                    config_param['frequency1'] = int(config[0].frequency1)  
                    config_param['frequency2'] = int(config[0].frequency2)
                    config_param['frequency3'] =  int(config[0].frequency3)
                    config_param['frequency4'] =  int(config[0].frequency4)
                    config_param['monetary1'] = int(config[0].monetary1)  
                    config_param['monetary2'] =  int(config[0].monetary2)  
                    config_param['monetary3'] =  int(config[0].monetary3)  
                    config_param['monetary4'] = int(config[0].monetary4)  
                    config_param['frequncy_type'] = str(config[0].frequncy_type) 
                    config_param['recency_type'] = str(config[0].recency_type) 
                


                # convert datafram to json
                message = "configs infos "
                response_data = result_response(ver, seq, message, config_param)
                data_status = status.HTTP_200_OK    
                return Response(response_data, status = data_status)
            except Exception as e:
                response_data = error_response(ver,seq,e)
                data_status = status.HTTP_200_OK    
                return Response(response_data, status = data_status)



class GetDisplayConfigView(APIView):
    def post(self, request): 
        owner        = self.request.user  
        if not 1:
            response_data = permission_response()
            return Response(response_data, status = status.HTTP_200_OK)
        else:
            ver = 0
            seq = 6

            try:
                
                config = DisplayConfig.objects.filter(owner=owner)
                if len(config) == 0:
                    config_param = {}
                    config_param['compare_period_time'] = 0
                    config_param['period_time'] = 90

                    config_param['product_category_equal'] = ''
                    config_param['product_category'] = ''
                    config_param['product_brand_equal'] =''
                    config_param['product_brand'] = '' 
                    config_param['product_name_equal'] = ''
                    config_param['product_name'] = ''

                    config_param['customer_gender_equal'] = ''
                    config_param['customer_gender'] = ''
                    config_param['sales_channel_equal'] =''
                    config_param['sales_channel'] = '' 
                    config_param['city_equal'] = ''
                    config_param['city'] = ''
                    config_param['email_equal'] =''
                    config_param['email'] = '' 
                    config_param['age_equal'] = ''
                    config_param['age'] = ''

                    message = "display config param"

                else:
                    config_param = {}
                    config_param['compare_period_time'] = int(config[0].compare_period_time)
                    config_param['period_time'] = int( config[0].period_time )

                    config_param['product_category_equal'] = config[0].product_category_equal
                    config_param['product_category'] = config[0].product_category
                    config_param['product_brand_equal'] =config[0].product_brand_equal
                    config_param['product_brand'] = config[0].product_brand 
                    config_param['product_name_equal'] = config[0].product_name_equal
                    config_param['product_name'] = config[0].product_name

                    config_param['customer_gender_equal'] = config[0].customer_gender_equal
                    config_param['customer_gender'] = config[0].customer_gender
                    config_param['sales_channel_equal'] =config[0].sales_channel_equal
                    config_param['sales_channel'] = config[0].sales_channel
                    config_param['city_equal'] = config[0].city_equal
                    config_param['city'] = config[0].city
                    config_param['email_equal'] =config[0].email_equal
                    config_param['email'] = config[0].email
                    config_param['age_equal'] = config[0].age_equal
                    config_param['age'] = config[0].age
                    message = f"display config param"

                # convert datafram to json
                response_data = result_response(ver, seq, message, config_param)
                data_status = status.HTTP_200_OK    
                return Response(response_data, status = data_status)
            except Exception as e:
                response_data = error_response(ver,seq,e)
                data_status = status.HTTP_200_OK    
                return Response(response_data, status = data_status)


class UpdateDisplayConfigView(APIView):
    def post(self, request): 
        owner        = self.request.user  
        if not 1:
            response_data = permission_response()
            return Response(response_data, status = status.HTTP_200_OK)
        else:
            ver = 0
            seq = 6

            try:

                config = DisplayConfig.objects.filter(owner=owner)
                config_param = {}
                config_param['compare_period_time'] = int(request.data.get('compare_period_time', 11) )
                config_param['period_time'] = int(request.data.get('period_time', 0) )

                config_param['product_category_equal'] = True if request.data.get('product_category_equal') == "true" else False
                config_param['product_category'] = request.data.get('product_category')
                config_param['product_brand_equal'] = True if request.data.get('product_brand_equal') == "true" else False
                config_param['product_brand'] = request.data.get('product_brand') 
                config_param['product_name_equal'] = True if request.data.get('product_name_equal') == "true" else False
                config_param['product_name'] = request.data.get('product_name') 
            
                config_param['customer_gender_equal'] = True if request.data.get('customer_gender_equal') == "true" else False
                config_param['customer_gender'] = request.data.get('customer_gender')
                config_param['sales_channel_equal'] = True if request.data.get('sales_channel_equal') == "true" else False
                config_param['sales_channel'] = request.data.get('sales_channel') 
                config_param['city_equal'] = True if request.data.get('city_equal') == "true" else False
                config_param['city'] = request.data.get('city') 
                config_param['email_equal'] = True if request.data.get('email_equal') == "true" else False
                config_param['email'] = request.data.get('email')
                config_param['age_equal'] = True if request.data.get('age_equal') == "true" else False
                config_param['age'] = request.data.get('age') 
                if len(config) == 0:
                    config_param['owner'] = owner
                    obj = DisplayConfig(**config_param)
                    obj.save()
                    message = "an new obj saved"

                else:
                    DisplayConfig.objects.filter(owner=owner).update(**config_param)
                    message = f"the config updated"
                # convert datafram to json
                response_data = result_response(ver, seq, message)
                data_status = status.HTTP_200_OK    
                return Response(response_data, status = data_status)
            except Exception as e:
                response_data = error_response(ver,seq,e)
                data_status = status.HTTP_200_OK    
                return Response(response_data, status = data_status)


class UpdateConfigView(APIView):
    def post(self, request): 
        owner        = self.request.user  
        if not 1:
            response_data = permission_response()
            return Response(response_data, status = status.HTTP_200_OK)
        else:
            ver = 0
            seq = 6

            try:
                
                config = Config.objects.filter(owner=owner)
                if len(config) == 0:
                    config_param = {}
                    config_param['segment'] = request.data.get('segment', 11) 
                    config_param['outlayer'] = request.data.get('outlayer', 0)  
                    config_param['recency1'] = request.data.get('recency1', 20)  
                    config_param['recency2'] = request.data.get('recency2', 40)  
                    config_param['recency3'] = request.data.get('recency3', 60)   
                    config_param['recency4'] = request.data.get('recency4', 80)  
                    config_param['frequency1'] = request.data.get('frequency1',20)  
                    config_param['frequency2'] = request.data.get('frequency2', 40)  
                    config_param['frequency3'] = request.data.get('frequency3', 60)  
                    config_param['frequency4'] = request.data.get('frequency4', 80)  
                    config_param['monetary1'] = request.data.get('monetary1', 20)  
                    config_param['monetary2'] = request.data.get('monetary2', 40)  
                    config_param['monetary3'] = request.data.get('monetary3', 60)  
                    config_param['monetary4'] = request.data.get('monetary4', 80)  
                    for k,v in config_param.items():
                        config_param[k] = int(v)
                    config_param['frequncy_type'] = request.data.get('frequncy_type', 'factor_count')  
                    config_param['recency_type'] = request.data.get('recency_type', 'pure_sale') 

                    config_param['owner'] = owner
                    obj = Config(**config_param)
                    obj.save()
                    message = "an new obj saved"

                else:
                    config_param = {}
                    config_param['segment'] = request.data.get('segment', int(config[0].segment)) 
                    config_param['outlayer'] = request.data.get('outlayer', int(config[0].outlayer))  
                    config_param['recency1'] = request.data.get('recency1', int(config[0].recency1))  
                    config_param['recency2'] = request.data.get('recency2', int(config[0].recency2))  
                    config_param['recency3'] = request.data.get('recency3', int(config[0].recency3))   
                    config_param['recency4'] = request.data.get('recency4', int(config[0].recency4))  
                    config_param['frequency1'] = request.data.get('frequency1', int(config[0].frequency1))  
                    config_param['frequency2'] = request.data.get('frequency2', int(config[0].frequency2))  
                    config_param['frequency3'] = request.data.get('frequency3', int(config[0].frequency3))  
                    config_param['frequency4'] = request.data.get('frequency4', int(config[0].frequency4))  
                    config_param['monetary1'] = request.data.get('monetary1', int(config[0].monetary1))  
                    config_param['monetary2'] = request.data.get('monetary2', int(config[0].monetary2))  
                    config_param['monetary3'] = request.data.get('monetary3', int(config[0].monetary3))  
                    config_param['monetary4'] = request.data.get('monetary4', int(config[0].monetary4))  
                    for k,v in config_param.items():
                        config_param[k] = int(v)
                    config_param['frequncy_type'] = request.data.get('frequncy_type', str(config[0].frequncy_type)) 
                    config_param['recency_type'] = request.data.get('recency_type', str(config[0].recency_type)) 
                    Config.objects.filter(owner=owner).update(**config_param)
                    message = f"the config updated"
                # convert datafram to json
                print(message)
                response_data = result_response(ver, seq, message)
                data_status = status.HTTP_200_OK    
                return Response(response_data, status = data_status)
            except Exception as e:
                response_data = error_response(ver,seq,e)
                data_status = status.HTTP_200_OK    
                return Response(response_data, status = data_status)

class UpdateCustomerPerRFMView(APIView):
    def post(self, request): 
        owner        = self.request.user  
        if not 1:
            response_data = permission_response()
            return Response(response_data, status = status.HTTP_200_OK)
        else:
            ver = 0
            seq = 6

            try:
                segment_types = [11, 6, 3]
                for segment in segment_types:
                    products = Product.objects.filter(owner=owner).filter(invoice_type="SALES")
                    df = pd.DataFrame(list(products.values()))
                    config_param = {}
                    try:
                        config = Config.objects.filter(owner=owner)
                    except Exception as e:
                        print(e)
                    if len(config) == 0:
                        config_param['segment'] = 11
                        config_param['outlayer'] = 0
                        config_param['recency1'] = 20
                        config_param['recency2'] = 40
                        config_param['recency3'] = 60
                        config_param['recency4'] = 80
                        config_param['frequency1'] = 20
                        config_param['frequency2'] = 40
                        config_param['frequency3'] = 60
                        config_param['frequency4'] = 80
                        config_param['monetary1'] = 20
                        config_param['monetary2'] = 40
                        config_param['monetary3'] = 60
                        config_param['monetary4'] = 80
                        config_param['frequncy_type'] = 'factor_count' 
                        config_param['recency_type'] = 'pure_sale'
                    else:
                        config_param['segment'] = config[0].segment
                        config_param['outlayer'] = config[0].outlayer
                        config_param['recency1'] = config[0].recency1
                        config_param['recency2'] = config[0].recency2
                        config_param['recency3'] = config[0].recency3
                        config_param['recency4'] = config[0].recency4
                        config_param['frequency1'] = config[0].frequency1
                        config_param['frequency2'] = config[0].frequency2
                        config_param['frequency3'] = config[0].frequency3
                        config_param['frequency4'] = config[0].frequency4
                        config_param['monetary1'] = config[0].monetary1
                        config_param['monetary2'] = config[0].monetary2
                        config_param['monetary3'] = config[0].monetary3
                        config_param['monetary4'] = config[0].monetary4
                        config_param['frequncy_type'] = config[0].frequncy_type
                        config_param['recency_type'] = config[0].recency_type

                    rfm_df = get_rfm_score(df, segment, config_param)
                    
                    # upate products
                    groups = rfm_df.groupby(by='Customer_segment',
                            as_index=True)['customer_id'].apply(list).to_dict()
                    # print(groups)
                    for k,v in groups.items():
                        if segment == 11:
                            products.filter(customer_id__in=v).update(type_11=k)
                        elif segment == 6:
                            products.filter(customer_id__in=v).update(type_6=k)
                        elif segment == 3:
                            products.filter(customer_id__in=v).update(type_3=k)
                results= {}
                message = f"customer rfm types updated for segments {segment_types} "
                # convert datafram to json
                print(message)
                response_data = result_response(ver, seq, message, results)
                data_status = status.HTTP_200_OK    
                return Response(response_data, status = data_status)
            except Exception as e:
                response_data = error_response(ver,seq,e)
                data_status = status.HTTP_200_OK    
                return Response(response_data, status = data_status)


class RFMTransitionView(APIView):
    def post(self, request): 
        owner        = self.request.user  
        if not 1:
            response_data = permission_response()
            return Response(response_data, status = status.HTTP_200_OK)
        else:
            ver = 0
            seq = 6
            try:
                display_conf = DisplayConfig.objects.get_or_create(owner=owner)
                seg_conf = Config.objects.get_or_create(owner=owner)
                segments = seg_conf[0].segment
                day_ebfor = display_conf[0].period_time if display_conf[0].period_time else 1000

                start_date_miladi1 = datetime.now() - timedelta(days=day_ebfor)
                
                end_date_miladi1   = datetime.now()

                start_products = Product.objects.filter(owner=owner, date_jalali__lte = start_date_miladi1, invoice_type='SALES')
                end_products = Product.objects.filter(owner=owner, date_jalali__lte = end_date_miladi1, invoice_type='SALES')

                start_date_results = {}
                index = f"type_{segments}"
                value_lists = list(set(start_products.values_list(index, flat=True)))
                for value in value_lists:
                    my_filter = Q()
                    my_or_filters = {index:value}
                    for item in my_or_filters:
                        my_filter |= Q(**{item:my_or_filters[item]})
                    # results[value] = start_products.filter(my_filter).values_list('customer_id', flat=True).distinct().count()
                    start_date_results[value] = list(start_products.filter(my_filter).values_list('customer_id', flat=True))

                end_date_results = {}
                index = f"type_{segments}"
                value_lists = list(set(end_products.values_list(index, flat=True)))
                for value in value_lists:
                    my_filter = Q()
                    my_or_filters = {index:value}
                    for item in my_or_filters:
                        my_filter |= Q(**{item:my_or_filters[item]})
                    # results[value] = start_products.filter(my_filter).values_list('customer_id', flat=True).distinct().count()
                    end_date_results[value] = list(end_products.filter(my_filter).values_list('customer_id', flat=True))

                results = {
                    "start_date_results": start_date_results,
                    "end_date_results":   end_date_results
                }

                # adding deactivate 
                all_users = [item.customer_id for item in Product.objects.filter(owner=owner)]
                start_date_users = [item.customer_id for item in start_products]
                end_date_users   = [item.customer_id for item in end_products]
                results["start_date_results"]["deactivate"] = list(set(all_users) - set(start_date_users))
                results["end_date_results"]["deactivate"] = list(set(all_users) - set(end_date_users))

                # creating transition
                transition = {"labels":["type", "start_count", "start_count_percentage", "end_count", "end_count_percentage", "transition_count"], "data":[]}
                all_keys = list(set(list(results['start_date_results'].keys()) + list(results['end_date_results'].keys())))
                
                
                for key in all_keys:
                    transition_count = {"labels":all_keys, "data":[], "percentage":[]}
                    
                    for item in all_keys:
                        item_count =  len(
                                list(set(results['start_date_results'].get(key, [])) &
                                set(results['end_date_results'].get(item, [])))
                             )
                        transition_count['data'].append(item_count)
                        try:
                            transition_count['percentage'].append(item_count/len(results['start_date_results'].get(key, [])))
                        except:
                            transition_count['percentage'].append(0)
                    
                    
                    transition['data'].append([
                    key,
                    len(results['start_date_results'].get(key, [])),
                    len(results['start_date_results'].get(key, []))/len(all_users),
                    len(results['end_date_results'].get(key, [])),
                    len(results['end_date_results'].get(key, []))/len(all_users),
                    transition_count
                    ]
                    )

                out_result = []
                for item in transition['data']:
                    source = item[0]
                    for idx in range(len(item[-1]['labels'])):
                        destination = item[-1]['labels'][idx]
                        value = abs(item[1] - item[-1]['data'][idx])
                        out_result.append({'source': source, 'destination': destination, 'value': value})
                


                # print(out_result)
                message = "Transition scores  "
                # convert datafram to json
                response_data = result_response(ver, seq, message, out_result)
                data_status = status.HTTP_200_OK    
                return Response(response_data, status = data_status)
            except Exception as e:
                response_data = error_response(ver,seq,e)
                data_status = status.HTTP_200_OK    
                return Response(response_data, status = data_status)



class DownloadDictView(APIView):

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

                if not os.path.exists( os.path.join("media", "temp")):
                    os.makedirs(os.path.join("media", "temp"))

                # creating file
                out_path = os.path.join("media", "temp", str(uuid.uuid4())+'.csv')
                data = request.data.get('data', {'labels':[], 'data':[]})
                data = json.loads(data)
                

                try:
                    df = pd.DataFrame(data['data'], columns=data['labels'])
                    df.to_csv(out_path)
                except:
                    out_path = ''

                message = f"downlod file" 
                results = {
                    "link": out_path
                }
                response_data = result_response(ver, seq, message, results)
                data_status = status.HTTP_200_OK    
                return Response(response_data, status = data_status)
            except Exception as e:
                response_data = error_response(ver,seq,e)
                data_status = status.HTTP_200_OK    
                return Response(response_data, status = data_status)



class LifeTimeView(APIView):

    def post(self, request): 
        owner        = self.request.user  
        if not 1:
            response_data = permission_response()
            return Response(response_data, status = status.HTTP_200_OK)
        else:
            ver = 0
            seq = 6
            display_conf = DisplayConfig.objects.get_or_create(owner=owner)
            seg_conf = Config.objects.get_or_create(owner=owner)
            segments = seg_conf[0].segment
            day_ebfor = display_conf[0].period_time if display_conf[0].period_time else 1000

            start_date_miladi1 = datetime.now() - timedelta(days=day_ebfor)
            
            end_date_miladi1   = datetime.now()

            try:

                products = Product.objects.filter(owner=owner, date_jalali__lte=end_date_miladi1,
                         date_jalali__gte=start_date_miladi1, invoice_type='SALES')
                results= {
                    "factor_amount_average":  factor_amount_average(products, f'type_{segments}'),
                    "pure_sale":  pure_sale(products, f'type_{segments}'),
                    "average_purchase_count": average_purchase_count(products, start_date_miladi1, end_date_miladi1, f'type_{segments}'),
                    "average_customer_liftime": average_customer_liftime(products, start_date_miladi1, end_date_miladi1, f'type_{segments}')
                }
                message = "Life time scores  "

                # convert to js format
                for k,v in results.items():
                    results[k] = {"labels": list(v.keys()), "data": list(v.values())}

                final_out = [
                    results['factor_amount_average'],

                    {"labels": [
                        'بخش',
                        'میانگین ارزش طول عمر',
                        'میانگین مبلغ خالص فاکتور',
                        'میانگین تعدا خرید در ماه',
                        'میانگین طول عمر مشتری',
                    ],
                      "data":[ [
                        results['factor_amount_average']['labels'][i], 
                        results['factor_amount_average']['data'][i],
                        results['pure_sale']['data'][i],
                        results['average_purchase_count']['data'][i],
                        results['average_customer_liftime']['data'][i], 
                    ] for i in range(len(results['average_customer_liftime']['data']))]}
                ]

                # print(results['average_customer_liftime']['data'])
                # final_out[1]["data"] = [['میانگین',
                #                         sum(results['factor_amount_average']['data'])/len(results['factor_amount_average']['data']),
                #                          sum(results['pure_sale']['data'])/len(results['pure_sale']['data']['data']),
                #                           sum(results['average_purchase_count']['data'])/len(results['average_purchase_count']['data']),
                #                            sum(results['average_customer_liftime']['data'])/len(results['average_customer_liftime']['data']),
        
                #                         ] ] + final_out[1]["data"]
                final_out[1]["data"] = [['میانگین',
                                        sum(results['factor_amount_average']['data'])/len(results['factor_amount_average']['data']),
                                         sum(results['pure_sale']['data'])/len(results['pure_sale']['data']),
                                          sum(results['average_purchase_count']['data'])/len(results['average_purchase_count']['data']),
                                           sum(results['average_customer_liftime']['data'])/len(results['average_customer_liftime']['data']),
        
                                        ] ] + final_out[1]["data"]

                # print(final_out)

                response_data = result_response(ver, seq, message, final_out)
                data_status = status.HTTP_200_OK    
                return Response(response_data, status = data_status)
            except Exception as e:
                response_data = error_response(ver,seq,e)
                data_status = status.HTTP_200_OK  


class ShareShopingView(APIView):

    def post(self, request): 
        owner        = self.request.user  
        if not 1:
            response_data = permission_response()
            return Response(response_data, status = status.HTTP_200_OK)
        else:
            ver = 0
            seq = 6


            period = int(request.data.get('period', 30))
            start_date1 = request.data.get('start_time1', 0)
            end_date1   = request.data.get('end_time1', 0)
            print(period, start_date1, end_date1, )
            label_name = ""
            if period == 30:
                label_name = 'ماه'
            elif period == 1:
                label_name = 'روز'
            elif period == 7:
                label_name = 'هفته'
            elif period == 90:
                label_name = 'فصل'
            elif period == 360:
                label_name = 'سال'
            else:
                label_name = 'دوره'

            try:

                start_date_miladi1 = convert_date(start_date1)
                end_date_miladi1   = convert_date(end_date1)
                products = Product.objects.filter(owner=owner, date_jalali__lte=end_date_miladi1, invoice_type='SALES',
                        date_jalali__gte=start_date_miladi1)

                results= share_shoping(products, start_date_miladi1, end_date_miladi1, period)
                for k,v in results.items():
                    if type(v) is list:
                        results[k] = [i if i else 0 for i in v]
                results['labels'] = [ f"{label_name} {i}" for i in range(len(results['new_customers']))]
                
                message = "sharing shoping information  "
                # convert datafram to json aggregate(Avg('quantity'))

                table_data = {
                    "labels": ['بازه زمانی', 'فروش ناخالص', 'درآمد از مشتریان جدید', 'سهم مشتریان جدید از کل درآمد'],
                    'data':[[results['labels'][i],
                              results['new_customers'][i]+results['old_customers'][i],
                              results['new_customers'][i], results['percent_new_customers'][i] 
                             ] for i in range(len(results['labels']))]
                }
                
                table_data['data'] = [[
                    'کل', sum(results['new_customers']) + sum(results['old_customers']), sum(results['new_customers']), sum(results['percent_new_customers'])
                ]] + table_data['data']
                print(table_data)

                final_out = [results, table_data]
                
                response_data = result_response(ver, seq, message, final_out)
                data_status = status.HTTP_200_OK    
                return Response(response_data, status = data_status)
            except Exception as e:
                response_data = error_response(ver,seq,e)
                data_status = status.HTTP_200_OK 


class RetentionView(APIView):

    def post(self, request): 
        owner        = self.request.user  
        if not 1:
            response_data = permission_response()
            return Response(response_data, status = status.HTTP_200_OK)
        else:
            ver = 0
            seq = 6


            period = int(request.data.get('period', 30))
            start_date1 = request.data.get('start_time1', 0)
            end_date1   = request.data.get('end_time1', 0)
            seperation  = request.data.get('seperation', None)
            seperation = None if seperation == 'None' else seperation
            print(period, start_date1, end_date1, seperation)
            label_name = ""
            if period == 30:
                label_name = 'ماه'
            elif period == 1:
                label_name = 'روز'
            elif period == 7:
                label_name = 'هفته'
            elif period == 90:
                label_name = 'فصل'
            elif period == 360:
                label_name = 'سال'
            else:
                label_name = 'دوره'

            try:
                if start_date1 and end_date1:
                    start_date_miladi1 = convert_date(start_date1)
                    end_date_miladi1   = convert_date(end_date1)
                    products = Product.objects.filter(owner=owner, date_jalali__lte=end_date_miladi1, invoice_type='SALES',
                         date_jalali__gte=start_date_miladi1)
                else:
                    products = Product.objects.filter(owner=owner, invoice_type='SALES')

                out_result = {}
                results = {}
                if seperation:
                    try:
                        results['retention_seperation'] = retention_seperation(products, start_date_miladi1, end_date_miladi1, period, seperation)
                    except:
                        results['retention_seperation'] = {}

                
                results['retention'] = retention(products, start_date_miladi1, end_date_miladi1, period)
                
                labels= [f"{label_name} {i}" for i in range(len(results['retention']['retention']))]
                out_result['labels'] = labels
                out_result['retention'] = [item if item else 0 for item in results['retention']['retention']]
                out_result['table'] = [['all', sum([item if item else 0 for item in results['retention']['new_customers']]) ]+out_result['retention']]
                if seperation:
                    for k,v in results['retention_seperation'].items():
                        temp = [item if item else 0 for item in v['retention']]
                        out_result['table'].append([k, sum([item if item else 0 for item in v['new_customers']]) ]+temp)
 
                message = "sharing shoping information  "
                # convert datafram to json aggregate(Avg('quantity'))
                
                response_data = result_response(ver, seq, message, out_result)
                data_status = status.HTTP_200_OK    
                return Response(response_data, status = data_status)
            except Exception as e:
                response_data = error_response(ver,seq,e)
                data_status = status.HTTP_200_OK 


def get_interval_info(intervals):
    intervals_0 = intervals
    intervals_0['max'] = max(intervals_0['distance']) if len(intervals_0['distance']) else 0
    intervals_0['min'] = min(intervals_0['distance']) if len(intervals_0['distance']) else 0
    intervals_0['avg'] = sum(intervals_0['distance'])/len(intervals_0['distance']) if len(intervals_0['distance']) and sum(intervals_0['distance']) else 0
    intervals_0['std'] = statistics.stdev(intervals_0['distance']) if len(intervals_0['distance']) and sum(intervals_0['distance'])  else 0
    intervals_0['distance'] = sorted(intervals_0['distance']    )
    intervals_0['percent_25'] = intervals_0['distance'][int((len(intervals_0['distance'])*0.25))] if len(intervals_0['distance']) else 0
    intervals_0['percent_50'] = intervals_0['distance'][int((len(intervals_0['distance'])*0.50))] if len(intervals_0['distance']) else 0
    intervals_0['percent_75'] = intervals_0['distance'][int((len(intervals_0['distance'])*0.75))] if len(intervals_0['distance']) else 0
    intervals_0['percent_90'] = intervals_0['distance'][int((len(intervals_0['distance'])*0.90))] if len(intervals_0['distance']) else 0
    return intervals_0

def get_interval_table_data(products):
    intervals_1_2 = {'count':0, 'distance':[]}
    intervals_2_3  = {'count':0, 'distance':[] }
    intervals_3_4  = {'count':0, 'distance':[] }
    intervals_4_5  = {'count':0, 'distance':[] }
    intervals_5_last  = {'count':0, 'distance':[] }
    intervals_all  = {'count':0, 'distance':[] }

    df = pd.DataFrame(list(products.values()))
    if len(df) == 0:
        table_data = {
        'labels': ['فاصله زمانی', 'تعداد خرید', 'میانگین زمانی', 'انحراف معیار', 'کمینه', '۲۵٪ خریدها', '۵۰٪ خریدها', '۷۵٪خریدها', '۹۰٪ خریدها', 'بیشینه'],
        'data':[]
        }
        return table_data
    for customer_id in set(df['customer_id']):
        new_df = df[(df.customer_id == customer_id)][['date_jalali', 'invoice_id']]
        new_df = new_df.groupby('invoice_id').first()
        new_df['date_jalali']= pd.to_datetime(new_df['date_jalali'])
        new_df = new_df.sort_values(by=['date_jalali'])
        
        data = new_df.values
        if len(new_df) > 1:
            delta = data[1][0] - data[0][0]
            intervals_1_2 ['count'] += 1
            intervals_1_2 ['distance'].append(int(delta/(1000000000*60*60*24)))

            delta = data[-1][0] - data[0][0]
            intervals_all ['count'] += 1
            intervals_all ['distance'].append(int(delta/(1000000000*60*60*24)))

        if len(new_df) > 2:
            delta = data[2][0] - data[1][0]
            intervals_2_3 ['count'] += 1
            intervals_2_3 ['distance'].append(int(delta/(1000000000*60*60*24)))
        if len(new_df) > 3:
            delta = data[3][0] - data[2][0]
            intervals_3_4 ['count'] += 1
            intervals_3_4 ['distance'].append(int(delta/(1000000000*60*60*24)))
        if len(new_df) > 4:
            delta = data[4][0] - data[3][0]
            intervals_4_5 ['count'] += 1
            intervals_4_5 ['distance'].append(int(delta/(1000000000*60*60*24)))
        if len(new_df) > 5:
            delta = data[5][0] - data[-1][0]
            intervals_5_last ['count'] += 1
            intervals_5_last ['distance'].append(int(delta/(1000000000*60*60*24)))

    intervals_1_2 = get_interval_info(intervals_1_2 )
    intervals_1_2 = ['بین خرید اول  و دوم', intervals_1_2.get('count', 0), intervals_1_2.get('avg', 0), intervals_1_2.get('std', 0),
        intervals_1_2.get('min', 0), intervals_1_2.get('percent_25', 0), intervals_1_2.get('percent_50', 0) , intervals_1_2.get('percent_75', 0),
        intervals_1_2.get('percent_90', 0),     intervals_1_2.get('max', 0)     ]
    
    intervals_2_3 = get_interval_info(intervals_2_3 )
    intervals_2_3 = ['بین خرید دوم  و سوم', intervals_2_3.get('count', 0), intervals_2_3.get('avg', 0), intervals_2_3.get('std', 0),
        intervals_2_3.get('min', 0), intervals_2_3.get('percent_25', 0), intervals_2_3.get('percent_50', 0) , intervals_2_3.get('percent_75', 0),
        intervals_2_3.get('percent_90', 0),     intervals_2_3.get('max', 0)     ]
    
    intervals_3_4 = get_interval_info(intervals_3_4 )
    intervals_3_4 = ['بین خرید سوم  و چهارم', intervals_3_4.get('count', 0), intervals_3_4.get('avg', 0), intervals_3_4.get('std', 0),
        intervals_3_4.get('min', 0), intervals_3_4.get('percent_25', 0), intervals_3_4.get('percent_50', 0) , intervals_3_4.get('percent_75', 0),
        intervals_3_4.get('percent_90', 0),     intervals_3_4.get('max', 0)     ]
    
    intervals_4_5 = get_interval_info(intervals_4_5 )
    intervals_4_5 = ['بین خرید چهارم  و پنجم', intervals_4_5.get('count', 0), intervals_4_5.get('avg', 0), intervals_4_5.get('std', 0),
        intervals_4_5.get('min', 0), intervals_4_5.get('percent_25', 0), intervals_4_5.get('percent_50', 0) , intervals_4_5.get('percent_75', 0),
        intervals_4_5.get('percent_90', 0),     intervals_4_5.get('max', 0)     ]
    
    intervals_5_last = get_interval_info(intervals_5_last )
    intervals_5_last = ['بین خرید پنجم  به بعد ', intervals_5_last.get('count', 0), intervals_5_last.get('avg', 0), intervals_5_last.get('std', 0),
        intervals_5_last.get('min', 0), intervals_5_last.get('percent_25', 0), intervals_5_last.get('percent_50', 0) , intervals_5_last.get('percent_75', 0),
        intervals_5_last.get('percent_90', 0),     intervals_5_last.get('max', 0)     ]

    intervals_all = get_interval_info(intervals_all )
    intervals_all = ['بین همه خریدها     ', intervals_all.get('count', 0), intervals_all.get('avg', 0), intervals_all.get('std', 0),
        intervals_all.get('min', 0), intervals_all.get('percent_25', 0), intervals_all.get('percent_50', 0) , intervals_all.get('percent_75', 0),
        intervals_all.get('percent_90', 0),     intervals_all.get('max', 0)     ]
    
    table_data = {
        'labels': ['فاصله زمانی', 'تعداد خرید', 'میانگین زمانی', 'انحراف معیار', 'کمینه', '۲۵٪ خریدها', '۵۰٪ خریدها', '۷۵٪خریدها', '۹۰٪ خریدها', 'بیشینه'],
        'data':[intervals_all, intervals_1_2, intervals_2_3, intervals_3_4, intervals_4_5, intervals_5_last]
    }
    return table_data


def get_interval_graph_data(products):
    intervals = {'0-2':{'purches1':0, 'purches2':0, 'purches3':0, 'purches4':0, 'purches5':0, },
                 '2-15':{'purches1':0, 'purches2':0, 'purches3':0, 'purches4':0, 'purches5':0, },
                 '15-29':{'purches1':0, 'purches2':0, 'purches3':0, 'purches4':0, 'purches5':0, },
                 '29-00':{'purches1':0, 'purches2':0, 'purches3':0, 'purches4':0, 'purches5':0, },
                  }


    df = pd.DataFrame(list(products.values()))
    if len(df) == 0:

        out = {
            "labels": ['بین ۰ تا ۲ روز خرید', 'بین ۲ تا ۱۵ روز خرید', ' بین ۱۵ تا ۲۹ روز خرید', 'بیش از ۲۹ روز خرید'],
            'purches1':[0, 0, 0, 0 ], 
            'purches2':[0, 0, 0, 0 ],
            'purches3':[0, 0, 0, 0 ], 
            'purches4':[0, 0, 0, 0 ],
            'purches5':[0, 0, 0, 0 ],
        }
        return out
    
    for customer_id in set(df['customer_id']):
        new_df = df[(df.customer_id == customer_id)][['date_jalali', 'invoice_id']]
        new_df = new_df.groupby('invoice_id').first()
        new_df['date_jalali']= pd.to_datetime(new_df['date_jalali'])
        new_df = new_df.sort_values(by=['date_jalali'])
        data = new_df.values

        distances = []
        if len(new_df) > 1:
            for i in range(1,len(new_df)):
                delta = data[i][0] - data[0][0]
                distances.append(int(delta/(1000000000*60*60*24)))
        elif len(new_df) == 1:
            distances.append(0)

        dist = [i for i in distances if i>= 0 and i<2]
        if len(dist) > 0 and len(dist) < 6:
            intervals['0-2'][f'purches{len(dist)}'] += 1

        dist = [i for i in distances if i>= 2 and i<15]
        if len(dist) > 0 and len(dist) < 6:
            intervals['2-15'][f'purches{len(dist)}'] += 1

        dist = [i for i in distances if i>= 15 and i<29]
        if len(dist) > 0 and len(dist) < 6:
            intervals['15-29'][f'purches{len(dist)}'] += 1

        dist = [i for i in distances if i>= 29]
        if len(dist) > 0 and len(dist) < 6:
            intervals['29-00'][f'purches{len(dist)}'] += 1

    out = {
        "labels": ['بین ۰ تا ۲ روز خرید', 'بین ۲ تا ۱۵ روز خرید', ' بین ۱۵ تا ۲۹ روز خرید', 'بیش از ۲۹ روز خرید'],
        'purches1':[intervals['0-2']['purches1'], intervals['2-15']['purches1'],
                        intervals['15-29']['purches1'], intervals['29-00']['purches1'] ], 
        'purches2':[intervals['0-2']['purches2'], intervals['2-15']['purches2'],
                        intervals['15-29']['purches2'], intervals['29-00']['purches2'] ], 
        'purches3':[intervals['0-2']['purches3'], intervals['2-15']['purches3'],
                        intervals['15-29']['purches3'], intervals['29-00']['purches3'] ], 
        'purches4':[intervals['0-2']['purches4'], intervals['2-15']['purches4'],
                        intervals['15-29']['purches4'], intervals['29-00']['purches4'] ], 
        'purches5':[intervals['0-2']['purches5'], intervals['2-15']['purches5'],
                        intervals['15-29']['purches5'], intervals['29-00']['purches5'] ], 
    }
    return out
    

class PurchaseInterval(APIView):

    def post(self, request): 
        owner        = self.request.user  
        if not 1:
            response_data = permission_response()
            return Response(response_data, status = status.HTTP_200_OK)
        else:
            ver = 0
            seq = 6

            display_conf = DisplayConfig.objects.get_or_create(owner=owner)
            seg_conf = Config.objects.get_or_create(owner=owner)
            segments = seg_conf[0].segment
            day_ebfor = display_conf[0].period_time if display_conf[0].period_time else 1000

            start_date_miladi1 = datetime.now() - timedelta(days=day_ebfor)
            
            end_date_miladi1   = datetime.now()

            try:
                products = Product.objects.filter(owner=owner, date_jalali__lte=end_date_miladi1, invoice_type='SALES',
                         date_jalali__gte=start_date_miladi1)
                
                table_data = get_interval_table_data(products)
                graph_data = get_interval_graph_data(products)
                out_results = [graph_data, table_data]
                # print(table_data)
                message = "interval  "
                response_data = result_response(ver, seq, message, out_results)
                data_status = status.HTTP_200_OK    
                return Response(response_data, status = data_status)
            except Exception as e:
                response_data = error_response(ver,seq,e)
                data_status = status.HTTP_200_OK 


class ClusteringView(APIView):


    def post(self, request): 
        owner        = self.request.user  
        if not 1:
            response_data = permission_response()
            return Response(response_data, status = status.HTTP_200_OK)
        else:
            ver = 0
            seq = 6
            json_data     = json.loads(request.body)
            start_date = json_data['params'].get('start_date', 0)
            end_date   = json_data['params'].get('end_date', 0)
            num_cluster = json_data['params'].get('num_cluster', 3)
            print('num_cluster', num_cluster)
            try:
                start_date_miladi1 = convert_date(start_date)
                end_date_miladi1   = convert_date(end_date)
                products = Product.objects.filter(owner=owner, date_jalali__lte=end_date_miladi1,
                         date_jalali__gte=start_date_miladi1)
                df = pd.DataFrame(list(products.values()))
                
                col_names = ['unit_price', 'quantity', 'weight']
                features = pd.DataFrame(df, columns = col_names)
                scaler = StandardScaler().fit(features.values)
                features = scaler.transform(features.values)
                scaled_features = pd.DataFrame(features, columns = col_names)
     
                LE = LabelEncoder()
                scaled_features['invoice_type'] = LE.fit_transform(df['invoice_type'])

                kmeans = KMeans( n_clusters = num_cluster, init='k-means++')
                kmeans.fit(scaled_features)
                
                # Format results as a DataFrame
                df['cluster'] = kmeans.labels_

                message = "clustering scores  "
                # convert datafram to json
                results= df.to_json(orient='index')
                response_data = result_response(ver, seq, message, results)
                data_status = status.HTTP_200_OK    
                return Response(response_data, status = data_status)
            except Exception as e:
                response_data = error_response(ver,seq,e)
                data_status = status.HTTP_200_OK    
                return Response(response_data, status = data_status)


class BundlingView(APIView):

    def post(self, request): 
        owner        = self.request.user  
        if not 1:
            response_data = permission_response()
            return Response(response_data, status = status.HTTP_200_OK)
        else:
            ver = 0
            seq = 6
            json_data     = json.loads(request.body)
            start_date = json_data['params'].get('start_date', 0)
            end_date   = json_data['params'].get('end_date', 0)
            user_id   = json_data['params'].get('user_id', 0)
            try:
                start_date_miladi1 = convert_date(start_date)
                end_date_miladi1   = convert_date(end_date)
                products = Product.objects.filter(date_jalali__lte=end_date_miladi1,
                         date_jalali__gte=start_date_miladi1)
                df = pd.DataFrame(list(products.values()))
                

                # This is the same data that was plotted for similarity earlier
                # with one new user "E" who has rated only movie 1
                
                # creating data
                items = list()
                users = list()
                ratings = list()

                for item_name in set(df['product_name']):
                    for user_id in set(df['customer_id']):
                        rating = len(df[(df['product_name'] == item_name) & (df['customer_id'] == user_id)])
                        if rating > 0:
                            items.append(item_name)
                            users.append(user_id)
                            ratings.append(rating)

                ratings_dict = {
                    "item": items,
                    "user": users,
                    "rating": ratings,
                }

                rating_df = pd.DataFrame(ratings_dict)
                reader = Reader(rating_scale=(1, max(ratings)))

                # Loads Pandas dataframe
                data = Dataset.load_from_df(rating_df[["user", "item", "rating"]], reader)
                from surprise import KNNWithMeans

                # To use item-based cosine similarity
                sim_options = {
                    "name": "cosine",
                    "user_based": False,  # Compute  similarities between items
                }
                algo = KNNWithMeans(sim_options=sim_options)
                trainingSet = data.build_full_trainset()
                algo.fit(trainingSet)

                

                def predection(user_id, items, algo):
                    out = list()
                    for item in set(items):
                        rate_pred = algo.predict(user_id, item)
                        out.append((rate_pred.est, item))
                    return [item[1] for item in sorted(out,key=itemgetter(0), reverse=1)]

                user_id = df['customer_id'][0]
                prediction = predection(user_id, items, algo)
                message = "bundeling scores  "
                # convert datafram to json
                results= prediction
                response_data = result_response(ver, seq, message, results)
                data_status = status.HTTP_200_OK    
                return Response(response_data, status = data_status)
            except Exception as e:
                response_data = error_response(ver,seq,e)
                data_status = status.HTTP_200_OK    
                return Response(response_data, status = data_status)
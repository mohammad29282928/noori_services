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
from .utils                                   import convert_date, get_result, sale_factor_count
from .utils                                   import rejected_factor_count, factor_product_average, factor_rows_average
from .utils                                   import factor_amount_average, factor_amount_product_average
from .utils                                   import customer_income_average, gross_sale, factor_product_count
from .utils                                   import factor_product_weight, factor_commisions, pure_factor_counts
from .utils                                   import pure_gross_sale, gross_rejected, pure_sale, rejected_product_count
from .utils                                   import rejedted_product_weight, pure_product_count, pure_product_weight 
from .utils                                   import users_count, new_users_count, old_users_count
from .utils                                   import percent_users, percent_rejected_count, percent_rejected_amount
from .utils                                   import sum_discount, gross_new_users, gross_sale_per_country
from .utils                                   import gross_sale_per_product_category, gross_sale_per_product_brand
from .utils                                   import gross_sale_per_customer_gender
from django.conf                              import settings



def get_product_per_segment(products, owner, start_date_miladi, end_date_miladi, segments):
    results= {
        "sale_factor_count":      sale_factor_count(products, segments),
        "rejected_factor_count":  rejected_factor_count(products, segments),
        "factor_product_average": factor_product_average(products, segments),
        "factor_rows_average":    factor_rows_average(products, segments),
        "factor_amount_average":  factor_amount_average(products, segments),
        "factor_amount_product_average":  factor_amount_product_average(products, segments),
        "customer_income_average":  customer_income_average(products, segments),
        "gross_sale":               gross_sale(products, segments),
        "factor_product_count":     factor_product_count(products, segments),
        "factor_product_weight":    factor_product_weight(products, segments),
        "factor_commisions":        factor_commisions(products, segments),
        "pure_factor_counts":       pure_factor_counts(products, segments),
        "pure_gross_sale":          pure_gross_sale(products, segments),
        "gross_rejected":           gross_rejected(products, segments),
        "pure_sale":                pure_sale(products, segments),
        "rejected_product_count":   rejected_product_count(products, segments),
        "pure_product_count":       pure_product_count(products, segments),
        "rejedted_product_weight":   rejedted_product_weight(products, segments),
        "pure_product_weight":       pure_product_weight(products),
        "users_count":               users_count(products, segments),
        "new_users_count":           new_users_count(products,owner, start_date_miladi, end_date_miladi, segments),
        "old_users_count":            old_users_count(products,owner, start_date_miladi, end_date_miladi, segments),
        "percent_users":               percent_users(products, owner, start_date_miladi, end_date_miladi, segments),                
        "percent_rejected_count":     percent_rejected_count(products, segments),
        "percent_rejected_amount":     percent_rejected_amount(products, segments),
        "sum_discount":                 sum_discount(products, segments),
        "gross_new_users":               gross_new_users(products, owner, start_date_miladi, end_date_miladi, segments),
        # "gross_sale_per_country":       gross_sale_per_country(products, 'product_name'),
        # "gross_sale_per_product_category":  gross_sale_per_product_category(products, 'product_name'),
        # "gross_sale_per_product_brand":  gross_sale_per_product_brand(products, 'product_name'),
        # "gross_sale_per_customer_gender":  gross_sale_per_customer_gender(products, 'product_name'),
        # "gross_sale_per_customer_gender":  gross_sale_per_customer_gender(products, 'type_11')
    }
    return results
class ProductsInfoView(APIView):

    def post(self, request): 
        owner        = self.request.user  
        segment_key_persian_maps = {
            'At risk':'در معرض خطر',
            'Potantial loyalist':'به سوی وفاداری',
            'Lost':'رویگردانان',
            'Hibernating':'خواب زمستانی',
            'About to sleep':'خواب آلود',
            'New Customer':'تازه وارد',
            'Promising':'امیدوارکننده',
            'Loyal':'وفادار',
            'Need Attention':'نیازمند توجه',
            'Champions':'قهرمان',
            'Can not Lose them':'از دست ندهید',
            'deactive':'غیر فعال'
        }
        segment_11 =     ['At risk', 'Potantial loyalist', 'Lost', 'Hibernating',  'About to sleep',
            'New Customer','Promising','Loyal','Need Attention', 'Champions','Can not Lose them', 'deactive']
        segment_6 = ['At risk',  'Lost', 'Loyal', 'New Customer', 'Promising', 'Champions', 'deactive']
        segment_3 = ['Lost', 'New Customer', 'Champions', 'deactive']

        if not 1:
            response_data = permission_response()
            return Response(response_data, status = status.HTTP_200_OK)
        else:
            ver = 0
            seq = 6

            segments_count = int(request.data.get('segments', 11))
            start_date1 = request.data.get('start_date1', 0)
            end_date1   = request.data.get('end_date1', 0)
            export = request.data.get("export", 0)


            if segments_count == 11:
                segments = 'type_11'
                segments_keys = segment_11
            elif segments_count == 6:
                segments = 'type_6'
                segments_keys = segment_6
            else:
                segments = 'type_3'
                segments_keys = segment_3


            try:
                if start_date1 and end_date1:
                    start_date_miladi1 = convert_date(start_date1)
                    end_date_miladi1   = convert_date(end_date1)
                    products = Product.objects.filter(owner=owner, date_jalali__lte=end_date_miladi1,
                         date_jalali__gte=start_date_miladi1)
                else:
                    products = Product.objects.filter(owner=owner)

                results = get_product_per_segment(products, owner, start_date_miladi1, end_date_miladi1, segments)
                

                
   
                
                for k,v in results.items():
                    temp = {"labels":[], "data":[]}
                    for key, val in v.items():
                        temp['labels'].append(segment_key_persian_maps.get(key))
                        temp['data'].append(val)
                    for key in segments_keys:
                        if key not in v.keys():
                            temp['labels'].append(segment_key_persian_maps.get(key))
                            temp['data'].append(0)
                    results[k] = temp
                
                # print(results)
                if export:
                    csv_path = "not saved"
                    # save in csv file 
                    index= list(results.keys())
                    labels = results['pure_sale']['labels']
                    df_data = {'labels':labels}
 
                    for i in range(len(index)):
                        try:
                            temp_dict = {results[index[i]]['labels'][idx]:results[index[i]]['data'][idx]
                                                for idx in range(len(labels))}
                            out_temp = []
                            for l in labels:
                                out_temp.append(temp_dict[l])
                            df_data[index[i]] = out_temp
                        except:
                            pass
                        
                    
                    df =pd.DataFrame(df_data)
                    
                    csv_path = str(uuid.uuid4()) + '.csv'
                    df.to_csv(os.path.join('media', 'temp', csv_path))
                    
                    # csv_path =  "http://127.0.0.1:8000" + MEDIA_URL+csv_path 
                    # csv_path = os.path.join(settings.MEDIA_ROOT, csv_path)
                    csv_path = os.path.join('media', 'temp', csv_path)
                    message = "products informations  "
                    # convert datafram to json aggregate(Avg('quantity'))
                    
                    results["csv_path"] = csv_path
                else:
                    results["csv_path"] = ''

                message = "products informations  "
                # convert datafram to json aggregate(Avg('quantity'))
                
                response_data = result_response(ver, seq, message, results)
                data_status = status.HTTP_200_OK    
                return Response(response_data, status = data_status)
            except Exception as e:
                response_data = error_response(ver,seq,e)
                data_status = status.HTTP_200_OK  



class ClearProductView(APIView):

    def post(self, request): 
        owner        = self.request.user  
        if not 1:
            response_data = permission_response()
            return Response(response_data, status = status.HTTP_200_OK)
        else:
            ver = 0
            seq = 6
            try:
                products = Product.objects.filter(owner=owner)
                for product in products:
                    product.delete()

                message = "all products cleared "
                # convert datafram to json
                results= []
                response_data = result_response(ver, seq, message, results)
                data_status = status.HTTP_200_OK    
                return Response(response_data, status = data_status)
            except Exception as e:
                response_data = error_response(ver,seq,e)
                data_status = status.HTTP_200_OK    



class ListProductView(APIView):

    def post(self, request): 
        owner        = self.request.user  
        if not 1:
            response_data = permission_response()
            return Response(response_data, status = status.HTTP_200_OK)
        else:
            ver = 0
            seq = 6
            json_data     = json.loads(request.body)
            try:
                products = Product.objects.filter(owner=owner)
                segments = int(json_data['params'].get('segments', 11))
                message = f"list of all my products {len(products)}"
                # convert datafram to json
                if segments == 6:
                    results= [i.type_6 for i in products]
                elif segments == 3:
                    results= [i.type_3 for i in products]
                else:
                    results= [i.type_11 for i in products]

                response_data = result_response(ver, seq, message, results)
                data_status = status.HTTP_200_OK    
                return Response(response_data, status = data_status)
            except Exception as e:
                response_data = error_response(ver,seq,e)
                data_status = status.HTTP_200_OK 




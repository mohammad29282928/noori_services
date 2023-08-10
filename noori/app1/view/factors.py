from unittest import result
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
import django
from django.db.models import Avg, Count, Sum, F

from .utils           import convert_date, get_result, convert_to_list_per_keys



class FactorsInfoDescriptionView(APIView):

    def post(self, request): 
        owner        = self.request.user  
        if not 1:
            response_data = permission_response()
            return Response(response_data, status = status.HTTP_200_OK)
        else:
            ver = 0
            seq = 6

            try:

                message = "factors services description  "
                # convert datafram to json aggregate(Avg('quantity'))
                results = {
                    "sale_factor_count": "تعداد فاکتورهای فروش", 
                    "rejected_factor_count": "تعداد فاکتورهای مرجوعی",
                    "factor_product_average": "میانگین تعداد محصول در فاکتور",
                    "factor_rows_average": "میانگین تعداد سطر در فاکتورها",
                    "factor_amount_average": "میانگین مبلغ فاکتورها",
                    "factor_amount_product_average": "میانگین مبلغ کالاها",
                    "customer_income_average": "میانگین مبلغ درامد خالص از مشتری",
                    "gross_sale": "فروش ناخالص",
                    "factor_product_count": "تعداد ناخالص محصول فروخته شده",
                    "factor_product_weight": "وزن محصولات در فاکتورهای فروش",
                    "factor_commisions": "مجموع کارمزد",
                    "pure_factor_counts": "تعداد خالص فاکتورها",
                    "pure_gross_sale": "مبلغ خالص پرداختی فاکتورها",
                    "gross_rejected": "مبلغ فاکتورهای مرجوعی",
                    "pure_sale": "فروش خالص",
                    "rejected_product_count": "تعداد محصولات مرجوعی",
                    "pure_product_count": "تعداد خالص محصولات فروخته شده",
                    "rejedted_product_weight": "وزن محصولات مرجوعی",
                    "pure_product_weight": "وزن محصولات در تمام فاکتورها",
                    "users_count": "تعداد مشتریان",
                    "new_users_count": "تعداد مشتریان جدید",
                    "old_users_count": "تعداد مشتریان تکراری",
                    "percent_users": "درصد مشتریان تکراری",
                    "percent_rejected_count": "درصد کالاهای مرجوعی",
                    "percent_rejected_amount": "درصد مبلغ مرجوعی",
                    "sum_discount": "مبلغ تخفیف فاکتورها",
                    "gross_new_users": "مجموع درآمد از مشتریان جدید",
                    "gross_sale_per_country": "فروش بر اساس اسم کشور",
                    "gross_sale_per_product_category": "فروش بر اساس دسته بندی محصول",
                    "gross_sale_per_product_brand": "فروش بر اساس برند محصول",
                    "gross_sale_per_customer_gender": "فروش بر اساس جنسیت کاربران",
                }
                response_data = result_response(ver, seq, message, results)
                data_status = status.HTTP_200_OK    
                return Response(response_data, status = data_status)
            except Exception as e:
                response_data = error_response(ver,seq,e)
                data_status = status.HTTP_200_OK   


def convert_factor_info_result_to_chart(result):
    for k,v in result.items():
        temp = {"labels":[], "data":[]}
        if type(v)==django.db.models.query.QuerySet:
            for item in  v:
                values = list(item.values())

                temp['labels'].append(values[0]) if values[0] != None else temp['labels'].append("no label")
                temp['data'].append(values[1]) 
            result[k] = temp
    return result

class FactorsInfoView(APIView):

    def post(self, request): 
        owner        = self.request.user  
        if not 1:
            response_data = permission_response()
            return Response(response_data, status = status.HTTP_200_OK)
        else:
            ver = 0
            seq = 6
            # json_data     = json.loads(request.body)

            segments = int(request.data.get('segments', 11))
            start_date1 = request.data.get('start_date1', 0)
            end_date1   = request.data.get('end_date1', 0)
            start_date2 = request.data.get('start_date2', 0)
            end_date2   = request.data.get('end_date2', 0)
            # print("start_date1", start_date1, end_date1, start_date2, end_date2)
            try:
                if start_date1 and end_date1:
                    start_date_miladi1 = convert_date(start_date1)
                    end_date_miladi1   = convert_date(end_date1)
                    products = Product.objects.filter(owner=owner, date_jalali__lte=end_date_miladi1,
                         date_jalali__gte=start_date_miladi1)
                else:
                    products = Product.objects.filter(owner=owner)

                result = get_result(products, owner, start_date_miladi1, end_date_miladi1)       
                results= {
                  "date1": convert_factor_info_result_to_chart(result)
                }
                
                if start_date2 and end_date2:
                    start_date_miladi2 = convert_date(start_date2)
                    end_date_miladi2   = convert_date(end_date2)
                    products = Product.objects.filter(owner=owner, date_jalali__lte=end_date_miladi2,
                          date_jalali__gte=start_date_miladi2)
                    result = get_result(products,  owner, start_date_miladi2, end_date_miladi2)
                    
                    results['date2']= convert_factor_info_result_to_chart(result)
                    # add percentage
                    percentage = {}
                    for k,v in results['date1'].items():
                        if k.startswith('gross_sale_per'):
                            continue
                        if type(v) != dict:
                            try:
                                percentage[k] =  (results["date1"][k] - results["date2"][k])/results["date1"][k]
                            except:
                                percentage[k] = 1
                        else:
                            temp = {"labels":[], "data":[]}
                            date1_items = results["date1"][k]
                            date2_items = results["date2"][k]
                            for label in set((date1_items['labels']+date2_items['labels'])):
                                temp['labels'].append(label)
                                if label in date1_items['labels'] and label in date2_items['labels']:
                                    try:
                                        val  = (date1_items['data'][date1_items['labels'].index(label)] - 
                                                date2_items['data'][date2_items['labels'].index(label)])
                                        val = val / date1_items['data'][date1_items['labels'].index(label)]
                                        temp['data'].append(val)
                                    except:
                                        temp['data'].append(0)
                                elif label in date1_items['labels'] and label not in date2_items['labels']:
                                    temp['data'].append(1)
                                else:
                                    temp['data'].append(-1)
                            percentage[k] = temp
                            
                            
                    results['percentage'] = percentage


                message = "factors informations  "
                # convert datafram to json aggregate(Avg('quantity'))
                if results.get('date1', 0):
                    for k,v in results['date1'].items():
                        try:
                            value = float("%.1f" % v)
                            if (value/1000000) > 1:
                                value = "%.3f M" % (value/1000000)
                            elif (value/1000) > 1:
                                value = "%.2f K" % (value/1000)
                            results['date1'][k] = value

                        except:
                            pass
                # print(results)
                response_data = result_response(ver, seq, message, results)
                data_status = status.HTTP_200_OK    
                return Response(response_data, status = data_status)
            except Exception as e:
                response_data = error_response(ver,seq,e)
                data_status = status.HTTP_200_OK   



class TrendsView(APIView):

    def post(self, request): 
        owner        = self.request.user  
        if not 1:
            response_data = permission_response()
            return Response(response_data, status = status.HTTP_200_OK)
        else:
            ver = 0
            seq = 6
            json_data     = json.loads(request.body)

            start_date1 = json_data['params'].get('start_date1', 0)
            end_date1   = json_data['params'].get('end_date1', 0)
            start_date2 = json_data['params'].get('start_date2', 0)
            end_date2   = json_data['params'].get('end_date2', 0)
            steps       = json_data['params'].get('steps', 1)
            recived_filters     = json_data['params'].get('filters',{})

            filters     = {} 
            # ['product_category', 'product_name', 'product_brand', 'country', 'customer_gender', 
            #   'customer_age', 'sales_channel', '']
            if recived_filters != {}:
                for k,v in recived_filters.items():
                    pass


            start_date_miladi1 = convert_date(start_date1)
            end_date_miladi1   = convert_date(end_date1)
            count_of_days = (end_date_miladi1-start_date_miladi1).days
            results = {}
            try:
                all_data1 = []
                for i in range(0, count_of_days, steps):
                    start_date_miladi = start_date_miladi1 + datetime.timedelta(days=i)
                    end_date_miladi = start_date_miladi + datetime.timedelta(days=i)

                    products = Product.objects.filter(owner=owner, date_jalali__lte=end_date_miladi,
                         date_jalali__gte=start_date_miladi)
                    result = get_result(products, owner, start_date_miladi, end_date_miladi)
                    result['start_time'] = start_date_miladi
                    result['end_time'] = end_date_miladi
                    all_data1.append(result)

                if end_date_miladi < end_date_miladi1:
                    start_date_miladi = end_date_miladi
                    products = Product.objects.filter(owner=owner, date_jalali__lte=end_date_miladi1,
                         date_jalali__gte=start_date_miladi)

                    result = get_result(products, owner, start_date_miladi, end_date_miladi1)
                    result['start_time'] = start_date_miladi
                    result['end_time'] = end_date_miladi
                    all_data1.append(result)

                results['date1']= convert_to_list_per_keys(all_data1)

                if start_date2 and end_date2:
                    start_date_miladi2 = convert_date(start_date2)
                    end_date_miladi2   = convert_date(end_date2)
                    count_of_days = (end_date_miladi2-start_date_miladi2).days

                    all_data2 = []
                    for i in range(0, count_of_days, steps):
                        start_date_miladi = start_date_miladi2 + datetime.timedelta(days=i)
                        end_date_miladi = start_date_miladi + datetime.timedelta(days=i)

                        products = Product.objects.filter(owner=owner, date_jalali__lte=end_date_miladi,
                            date_jalali__gte=start_date_miladi)
                        result = get_result(products, owner, start_date_miladi, end_date_miladi)
                        result['start_time'] = start_date_miladi
                        result['end_time'] = end_date_miladi
                        all_data2.append(result)

                    if end_date_miladi < end_date_miladi2:
                        start_date_miladi = end_date_miladi
                        products = Product.objects.filter(owner=owner, date_jalali__lte=end_date_miladi2,
                            date_jalali__gte=start_date_miladi)

                        result = get_result(products, owner, start_date_miladi, end_date_miladi2)
                        result['start_time'] = start_date_miladi
                        result['end_time'] = end_date_miladi
                        all_data2.append(result)

                    results['date2']= convert_to_list_per_keys(all_data2)
                    # results= {
                    #     "date2": convert_to_list_per_keys(all_data2)
                    # }

                message = "factors trends informations  "
                # convert datafram to json aggregate(Avg('quantity'))
                
                response_data = result_response(ver, seq, message, results)
                data_status = status.HTTP_200_OK    
                return Response(response_data, status = data_status)
            except Exception as e:
                response_data = error_response(ver,seq,e)
                data_status = status.HTTP_200_OK   
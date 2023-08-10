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

from django.db.models import Avg, Count, Sum, F


def convert_date(date_jalali):
    date_jalali = date_jalali.split('T')[0].split('-')
    date_miladi = JalaliDate(int(date_jalali[0]), 
                int(date_jalali[1]), int(date_jalali[2])).to_gregorian()
    return date_miladi



def get_result(products,owner, start_date_miladi, end_date_miladi):
    results = {}
    results['sale_factor_count'] = products.values_list('invoice_id', flat=True).filter(
        invoice_type="SALES").distinct().count()

    results['rejected_factor_count'] = products.values_list('invoice_id', flat=True).filter(
        invoice_type="REJECTED").distinct().count()

    results['factor_product_average'] = products.values('invoice_id').filter(
        invoice_type="SALES").annotate(
      total=Sum('quantity')).aggregate(total__avg=Avg('total'))['total__avg']

    results['factor_rows_average'] = products.values('invoice_id').annotate(
      total=Sum(1)).aggregate(total__avg=Avg('total'))['total__avg']

    results['factor_amount_average'] = products.values('invoice_id').filter(
        invoice_type="SALES").annotate(
        quantity_price=F('quantity') * F('unit_price')).values('invoice_id').annotate(
      total=Sum('quantity_price')).aggregate(
            total__avg=Avg('total'))['total__avg']

    results['factor_amount_product_average'] = products.values_list('unit_price', flat=True).filter(
        invoice_type="SALES").aggregate(
            total__avg=Avg('unit_price'))['total__avg']

    results['customer_income_average'] = results['factor_amount_average']

    results['sale_factor_count'] = products.filter(invoice_type="SALES").values_list('invoice_id', flat=True).distinct().count()

    results['gross_sale'] = products.values('invoice_id').filter(
        invoice_type="SALES").annotate(
        quantity_price=F('quantity') * F('unit_price')).values('invoice_id').annotate(
      total=Sum('quantity_price')).aggregate(
            total__avg=Sum('total'))['total__avg']

    results['factor_product_count'] = products.values('invoice_id').filter(
        invoice_type="SALES").annotate(
      total=Sum('quantity')).aggregate(total__sum=Sum('total'))['total__sum']

    results['factor_product_weight'] = products.values('invoice_id').filter(
        invoice_type="SALES").annotate(
      total=Sum('weight')).aggregate(total__sum=Sum('total'))['total__sum']

    results['factor_commisions'] = products.values('invoice_id').filter(
        invoice_type="SALES").annotate(
      total=Sum('commission')).aggregate(total__sum=Sum('total'))['total__sum']

    results['pure_factor_counts'] = results['sale_factor_count'] - results['rejected_factor_count']

    results['pure_gross_sale'] = products.values('invoice_id').filter(
        invoice_type="SALES").annotate(
        quantity_price=F('quantity') * F('unit_price')).values('invoice_id').annotate(
        pure_price=F('quantity_price') - F('discount')).values('invoice_id').annotate(
      total=Sum('pure_price')).aggregate(
            total__avg=Sum('total'))['total__avg']

    results['gross_rejected'] = products.values('invoice_id').filter(
        invoice_type="REJECTED").annotate(
        quantity_price=F('quantity') * F('unit_price')).values('invoice_id').annotate(
      total=Sum('quantity_price')).aggregate(
            total__avg=Sum('total'))['total__avg']
    if not results['gross_rejected']:
      results['gross_rejected'] = 0

    results['pure_sale'] = results['gross_sale']- results['gross_rejected']

    results['rejected_product_count'] = products.values('invoice_id').filter(
        invoice_type="REJECTED").annotate(
      total=Sum('quantity')).aggregate(total__sum=Sum('total'))['total__sum']
    if not results['rejected_product_count']:
      results['rejected_product_count'] = 0

    results['pure_product_count'] = results['factor_product_count'] - results['rejected_product_count'] 

    results['rejedted_product_weight'] = products.values('invoice_id').filter(
        invoice_type="Rejected").annotate(
      total=Sum('weight')).aggregate(total__sum=Sum('total'))['total__sum']
    if not results['rejedted_product_weight']:
      results['rejedted_product_weight'] = 0

    results['pure_product_weight'] = results['factor_product_weight'] - results['rejedted_product_weight']

    results['users_count'] =  products.values('customer_id').distinct().count()
    
    other_time_users = Product.objects.filter(
      owner=owner, date_jalali__gt=end_date_miladi,
                         date_jalali__lt=start_date_miladi
    ).values('customer_id').distinct().values_list('customer_id', flat=True)

    this_time_users = products.values('customer_id').distinct().values_list('customer_id', flat=True)


    results['new_users_count'] = results['users_count'] - len(list(this_time_users.intersection(other_time_users)))
    
    results['old_users_count'] = len(list(this_time_users.intersection(other_time_users)))
    
    results['percent_users'] = results['old_users_count'] / results['users_count']
    
    results['percent_rejected_count'] = results['rejected_product_count'] / results['factor_product_count']
    
    results['percent_rejected_amount'] = results['gross_rejected'] / results['gross_sale']
    
    results['sum_credit_payment_amount'] = products.values('invoice_id').filter(
        invoice_type="SALES").aggregate(total__sum=Sum('credit_payment_amount'))['total__sum']
    
    results['sum_discount'] = products.values('invoice_id').filter(
        invoice_type="SALES").aggregate(total__sum=Sum('discount'))['total__sum']

        

    new_users = list(set(this_time_users) - set(list(this_time_users.intersection(other_time_users))))

    
    
    results['gross_new_users'] = products.values('invoice_id').filter(
        invoice_type="SALES").filter(
        customer_id__in=new_users).annotate(
        quantity_price=F('quantity') * F('unit_price')).values('invoice_id').annotate(
      total=Sum('quantity_price')).aggregate(
            total__avg=Sum('total'))['total__avg']
            
    if not  results['gross_new_users'] :
       results['gross_new_users'] = 0


    results["gross_sale_per_country"] = products.values('invoice_id').filter(
        invoice_type="SALES").annotate(
        quantity_price=F('quantity') * F('unit_price')).values('country').annotate(country_sale=Sum('quantity_price') ).order_by()


    results["gross_sale_per_region"] = products.values('invoice_id').filter(
        invoice_type="SALES").annotate(
        quantity_price=F('quantity') * F('unit_price')).values('region').annotate(country_sale=Sum('quantity_price') ).order_by()

    results["gross_sale_per_city"] = products.values('invoice_id').filter(
        invoice_type="SALES").annotate(
        quantity_price=F('quantity') * F('unit_price')).values('city').annotate(country_sale=Sum('quantity_price') ).order_by()
    
    results["gross_sale_per_product_category"] = products.values('invoice_id').filter(
        invoice_type="SALES").annotate(
        quantity_price=F('quantity') * F('unit_price')).values('product_category').annotate(country_sale=Sum('quantity_price') ).order_by()
    
    results["gross_sale_per_product_brand"] = products.values('invoice_id').filter(
        invoice_type="SALES").annotate(
        quantity_price=F('quantity') * F('unit_price')).values('product_brand').annotate(country_sale=Sum('quantity_price') ).order_by()
    
    results["gross_sale_per_customer_gender"] = products.values('invoice_id').filter(
        invoice_type="SALES").annotate(
        quantity_price=F('quantity') * F('unit_price')).values('customer_gender').annotate(country_sale=Sum('quantity_price') ).order_by()
    

    
    return results


class FactorsInfoView(APIView):

    def post(self, request): 
        owner        = self.request.user  
        if not 1:
            response_data = permission_response()
            return Response(response_data, status = status.HTTP_200_OK)
        else:
            ver = 0
            seq = 6
            json_data     = json.loads(request.body)

            segments = int(json_data['params'].get('segments', 11))
            start_date1 = json_data['params'].get('start_date1', 0)
            end_date1   = json_data['params'].get('end_date1', 0)
            start_date2 = json_data['params'].get('start_date2', 0)
            end_date2   = json_data['params'].get('end_date2', 0)
            try:
                if start_date1 and end_date1:
                    start_date_miladi1 = convert_date(start_date1)
                    end_date_miladi1   = convert_date(end_date1)
                    products = Product.objects.filter(owner=owner, date_jalali__lte=end_date_miladi1,
                         date_jalali__gte=start_date_miladi1)
                else:
                    products = Product.objects.filter(owner=owner)

                
                results= {
                  "date1": get_result(products, owner, start_date_miladi1, end_date_miladi1)
                }
                if start_date2 and end_date2:
                    start_date_miladi2 = convert_date(start_date2)
                    end_date_miladi2   = convert_date(end_date2)
                    products = Product.objects.filter(owner=owner, date_jalali__lte=end_date_miladi2,
                          date_jalali__gte=start_date_miladi2)
                    results['date2': get_result(products)]

                message = "factors informations  "
                # convert datafram to json aggregate(Avg('quantity'))
                
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
            start_date_miladi1 = convert_date(start_date1)
            end_date_miladi1   = convert_date(end_date1)

            try:

                products = Product.objects.filter(owner=owner, date_jalali__lte=end_date_miladi1,
                         date_jalali__gte=start_date_miladi1)


                
                results= {
                  "date1": get_result(products, owner, start_date_miladi1, end_date_miladi1)
                }
                if start_date2 and end_date2:
                    start_date_miladi2 = convert_date(start_date2)
                    end_date_miladi2   = convert_date(end_date2)
                    products = Product.objects.filter(owner=owner, date_jalali__lte=end_date_miladi2,
                          date_jalali__gte=start_date_miladi2)
                    results['date2': get_result(products)]

                message = "factors informations  "
                # convert datafram to json aggregate(Avg('quantity'))
                
                response_data = result_response(ver, seq, message, results)
                data_status = status.HTTP_200_OK    
                return Response(response_data, status = data_status)
            except Exception as e:
                response_data = error_response(ver,seq,e)
                data_status = status.HTTP_200_OK   
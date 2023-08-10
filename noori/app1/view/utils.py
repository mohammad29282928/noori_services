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
from collections                              import Counter
from django.db.models import Avg, Count, Sum, F
from dateutil.relativedelta                import relativedelta


def handle_zeros_divide(x1, x2):
    try:
        return x1/x2
    except:
        return 0
        
def handle_none_value(x1):
    if x1:
        return x1
    else:
        return 0

def convert_date(date_jalali):
    date_jalali = date_jalali.split('T')[0].split('-')
    date_miladi = JalaliDate(int(date_jalali[0]), 
                int(date_jalali[1]), int(date_jalali[2])).to_gregorian()
    return date_miladi


def convert_to_list_per_keys(all_data):
    out = {}
    for i in all_data:
        for k,v in i.items():
            if not v:
                v = 0
            try:
                out[k].append(v)
            except:
                out[k] = [v]
    return out


def sale_factor_count(products, index=None):
    # تعداد فاکتورهای فروش
    results = {}
    if index is  None:
        results['sale_factor_count'] = products.values_list('invoice_id', flat=True).filter(
            invoice_type="SALES").distinct().count()
    else:
        value_lists = list(set(products.values_list(index, flat=True)))
        for value in value_lists:
            my_filter = Q()
            my_or_filters = {index:value}
            for item in my_or_filters:
                my_filter |= Q(**{item:my_or_filters[item]})
            results[value] = products.filter(my_filter).values_list('invoice_id', flat=True).filter(
            invoice_type="SALES").distinct().count()
    return results


def rejected_factor_count(products, index=None):
    # تعداد فاکتورهای مرجوعی
    results = {}
    if index is  None:
        results['rejected_factor_count'] = products.values_list('invoice_id', flat=True).filter(
            invoice_type="RETURN").distinct().count()
    else:
        value_lists = list(set(products.values_list(index, flat=True)))
        for value in value_lists:
            my_filter = Q()
            my_or_filters = {index:value}
            for item in my_or_filters:
                my_filter |= Q(**{item:my_or_filters[item]})
            results[value] = products.filter(my_filter).values_list('invoice_id', flat=True).filter(
                invoice_type="RETURN").distinct().count()
    return results
    

def factor_product_average(products, index=None):

    # میانگین تعداد محصول در فاکتور
    results = {}
    if index is  None:
        results['factor_product_average'] = products.filter(
            invoice_type="SALES").values('invoice_id').annotate(
            total=Sum('quantity')).aggregate(total__avg=Avg('total'))['total__avg']
    else:
        value_lists = list(set(products.values_list(index, flat=True)))
        for value in value_lists:
            my_filter = Q()
            my_or_filters = {index:value}
            for item in my_or_filters:
                my_filter |= Q(**{item:my_or_filters[item]})
            results[value] = products.filter(
            invoice_type="SALES").filter(my_filter).values('invoice_id').filter(
            invoice_type="SALES").annotate(
            total=Sum('quantity')).aggregate(total__avg=Avg('total'))['total__avg']
    return results


def factor_rows_average(products, index=None):
    #میانگین تعداد سطر در فاکتور
    results = {}
    if index is  None:
        results['factor_rows_average'] = products.filter(
            invoice_type="SALES").values('invoice_id').annotate(
            total=Sum(1)).aggregate(total__avg=Avg('total'))['total__avg']
    else:
        value_lists = list(set(products.values_list(index, flat=True)))
        for value in value_lists:
            my_filter = Q()
            my_or_filters = {index:value}
            for item in my_or_filters:
                my_filter |= Q(**{item:my_or_filters[item]})
            results[value] = products.filter(
            invoice_type="SALES").filter(my_filter).values('invoice_id').annotate(
            total=Sum(1)).aggregate(total__avg=Avg('total'))['total__avg']
    return results


def factor_amount_average(products, index=None):
    # میانگین مبلغ فاکتور
    results = {}
    if index is  None:
        results['factor_amount_average'] = products.values('invoice_id').filter(
            invoice_type="SALES").annotate(
            quantity_price=F('quantity') * F('unit_price')).values('invoice_id').annotate(
            total=Sum('quantity_price')).aggregate(
            total__avg=Avg('total'))['total__avg']

    else:
        value_lists = list(set(products.values_list(index, flat=True)))
        for value in value_lists:
            my_filter = Q()
            my_or_filters = {index:value}
            for item in my_or_filters:
                my_filter |= Q(**{item:my_or_filters[item]})
            results[value] = products.filter(my_filter).values('invoice_id').filter(
            invoice_type="SALES").annotate(
            quantity_price=F('quantity') * F('unit_price')).values('invoice_id').annotate(
            total=Sum('quantity_price')).aggregate(
            total__avg=Avg('total'))['total__avg']
    return results


def factor_amount_product_average(products, index=None):
    # میانگین مبلف کالا
    
    results = {}
    if index is  None:
        results['factor_amount_product_average'] = products.values_list('unit_price', flat=True).aggregate(
            total__avg=Avg('unit_price'))['total__avg']

    else:
        value_lists = list(set(products.values_list(index, flat=True)))
        for value in value_lists:
            my_filter = Q()
            my_or_filters = {index:value}
            for item in my_or_filters:
                my_filter |= Q(**{item:my_or_filters[item]})
            results[value] = products.filter(my_filter).values_list('unit_price', flat=True).aggregate(
            total__avg=Avg('unit_price'))['total__avg']
    return results

    
def customer_income_average(products, index=None):
    # میانگین درامد خالص از مشتری
    results = {}
    
    if index is  None:
        number_of_users = products.values_list('customer_id', flat=True).distinct().count()
        results['customer_income_average'] = products.values('invoice_id').annotate(
            quantity_price=F('quantity') * F('unit_price')).values('invoice_id').annotate(
            total=Sum('quantity_price')).aggregate(
            total__avg=Sum('total'))['total__avg'] 
        try:
            results['customer_income_average']  = results['customer_income_average']/number_of_users
        except:
            results['customer_income_average'] = 0

    else:
        value_lists = list(set(products.values_list(index, flat=True)))
        for value in value_lists:
            my_filter = Q()
            my_or_filters = {index:value}
            for item in my_or_filters:
                my_filter |= Q(**{item:my_or_filters[item]})

            number_of_users = products.filter(my_filter).values_list('customer_id', flat=True).distinct().count()
            results[value] = products.filter(my_filter).values('invoice_id').annotate(
            quantity_price=F('quantity') * F('unit_price')).values('invoice_id').annotate(
            total=Sum('quantity_price')).aggregate(
            total__avg=Sum('total'))['total__avg']

            try:
                results[value]  = results[value]/number_of_users
            except:
                results[value] = 0


    return results


def gross_sale(products, index=None):
    # فروش ناخالص
    results = {}
    if index is  None:
        results['gross_sale'] = products.values('invoice_id').filter(
            invoice_type="SALES").annotate(
            quantity_price=F('quantity') * F('unit_price')).values('invoice_id').annotate(
            total=Sum('quantity_price')).aggregate(
            total__avg=Sum('total'))['total__avg']

    else:
        value_lists = list(set(products.values_list(index, flat=True)))
        for value in value_lists:
            my_filter = Q()
            my_or_filters = {index:value}
            for item in my_or_filters:
                my_filter |= Q(**{item:my_or_filters[item]})
            results[value] = products.filter(my_filter).values('invoice_id').filter(
            invoice_type="SALES").annotate(
            quantity_price=F('quantity') * F('unit_price')).values('invoice_id').annotate(
            total=Sum('quantity_price')).aggregate(
            total__avg=Sum('total'))['total__avg']
    return results


def factor_product_count(products, index=None):
    # تعداد ناخالص محصول فروخته شده
    results = {}
    if index is  None:
        results['factor_product_count'] = products.values('invoice_id').filter(
            invoice_type="SALES").annotate(
            total=Sum('quantity')).aggregate(total__sum=Sum('total'))['total__sum']

    else:
        value_lists = list(set(products.values_list(index, flat=True)))
        for value in value_lists:
            my_filter = Q()
            my_or_filters = {index:value}
            for item in my_or_filters:
                my_filter |= Q(**{item:my_or_filters[item]})
            results[value] = products.filter(my_filter).values('invoice_id').filter(
            invoice_type="SALES").annotate(
            total=Sum('quantity')).aggregate(total__sum=Sum('total'))['total__sum']
    for k,v in results.items():
        if not v:
            results[k] = 0
    return results

    
def factor_product_weight(products, index=None):
    # وزن محصولات در فاکتورهای فروش
    results = {}
    if index is  None:
        results['factor_product_weight'] = products.values('invoice_id').filter(
            invoice_type="SALES").annotate(
            total=Sum('weight')).aggregate(total__sum=Sum('total'))['total__sum']

    else:
        value_lists = list(set(products.values_list(index, flat=True)))
        for value in value_lists:
            my_filter = Q()
            my_or_filters = {index:value}
            for item in my_or_filters:
                my_filter |= Q(**{item:my_or_filters[item]})
            results[value] = products.filter(my_filter).values('invoice_id').filter(
            invoice_type="SALES").annotate(
            total=Sum('weight')).aggregate(total__sum=Sum('total'))['total__sum']
    for k,v in results.items():
        if not v:
            results[k] = 0
    return results


def factor_commisions(products, index=None):
    # کارمزد
    results = {}
    if index is  None:
        results['factor_commisions'] = products.values('invoice_id').filter(
            invoice_type="SALES").annotate(
            total=Sum('commission')).aggregate(total__sum=Sum('total'))['total__sum']

    else:
        value_lists = list(set(products.values_list(index, flat=True)))
        for value in value_lists:
            my_filter = Q()
            my_or_filters = {index:value}
            for item in my_or_filters:
                my_filter |= Q(**{item:my_or_filters[item]})
            results[value] = products.filter(my_filter).values('invoice_id').filter(
            invoice_type="SALES").annotate(
            total=Sum('commission')).aggregate(total__sum=Sum('total'))['total__sum']

    for k,v in results.items():
        if not v:
            results[k] = 0
    return results


def pure_factor_counts(products, index=None):
    # تعداد خالص فاکتورها
    # TODO: i think this name not true    
    results = {}
    if index is  None:
        results['pure_factor_counts'] = sale_factor_count(products, index)['sale_factor_count'] + rejected_factor_count(products, index)['rejected_factor_count']

    else:
        value_lists = list(set(products.values_list(index, flat=True)))
        for value in value_lists:
            my_filter = Q()
            my_or_filters = {index:value}
            for item in my_or_filters:
                my_filter |= Q(**{item:my_or_filters[item]})
            results[value] = Counter(sale_factor_count(products, index))[value] - Counter(rejected_factor_count(products, index))[value]

    for k,v in results.items():
        if not v:
            results[k] = 0
    return results


def pure_gross_sale(products, index=None):
    # مبلغ خالص پرداختی فاکتورها
    # TODO: i think this name not true 
    results = {}
    if index is  None:
        results['pure_gross_sale'] = products.values('invoice_id').annotate(
            quantity_price=F('quantity') * F('unit_price')).values('invoice_id').annotate(
            pure_price=F('quantity_price') - F('discount')).values('invoice_id').annotate(
            total=Sum('pure_price')).aggregate(
            total__avg=Sum('total'))['total__avg']

    else:
        value_lists = list(set(products.values_list(index, flat=True)))
        for value in value_lists:
            my_filter = Q()
            my_or_filters = {index:value}
            for item in my_or_filters:
                my_filter |= Q(**{item:my_or_filters[item]})
            results[value] = products.filter(my_filter).values('invoice_id').annotate(
            quantity_price=F('quantity') * F('unit_price')).values('invoice_id').annotate(
            pure_price=F('quantity_price') - F('discount')).values('invoice_id').annotate(
            total=Sum('pure_price')).aggregate(
            total__avg=Sum('total'))['total__avg']
    return results


def gross_rejected(products, index=None):
    # مبلغ فاکتورهای مرجوعی
    results = {}
    if index is  None:
        results['gross_rejected'] = products.values('invoice_id').filter(
            invoice_type="RETURN").annotate(
            quantity_price=F('quantity') * F('unit_price')).values('invoice_id').annotate(
            total=Sum('quantity_price')).aggregate(
            total__avg=Sum('total'))['total__avg']

    else:
        value_lists = list(set(products.values_list(index, flat=True)))
        for value in value_lists:
            my_filter = Q()
            my_or_filters = {index:value}
            for item in my_or_filters:
                my_filter |= Q(**{item:my_or_filters[item]})
            results[value] = products.filter(my_filter).values('invoice_id').filter(
            invoice_type="RETURN").annotate(
            quantity_price=F('quantity') * F('unit_price')).values('invoice_id').annotate(
            total=Sum('quantity_price')).aggregate(
            total__avg=Sum('total'))['total__avg']
    for k,v in results.items():
        if not v:
            results[k] = 0
    return results


def pure_sale(products, index=None):
    # فروش خالص
    results = {}
    if index is None:
        results['pure_sale'] = pure_gross_sale(products, index)['pure_gross_sale']
    else:
        results = Counter(gross_sale(products, index))
    
    return results


def rejected_product_count(products, index=None):
    results = {}
    if index is  None:
        results['rejected_product_count'] = products.values('invoice_id').filter(
                invoice_type="RETURN").annotate(
                total=Sum('quantity')).aggregate(total__sum=Sum('total'))['total__sum']

    else:
        value_lists = list(set(products.values_list(index, flat=True)))
        for value in value_lists:
            my_filter = Q()
            my_or_filters = {index:value}
            for item in my_or_filters:
                my_filter |= Q(**{item:my_or_filters[item]})
            results[value] = products.filter(my_filter).values('invoice_id').filter(
                invoice_type="RETURN").annotate(
                total=Sum('quantity')).aggregate(total__sum=Sum('total'))['total__sum']
    for k,v in results.items():
        if not v:
            results[k] = 0
    return results  

 
def pure_product_count(products, index=None):
    # تعداد خالص محصولات فروخته شده 
    results = {}
    if index is None:
        results['pure_product_count'] = factor_product_count(products, index)['factor_product_count'] + rejected_product_count(products, index)['rejected_product_count']
    else:
        results = Counter(factor_product_count(products, index)) + Counter(rejected_product_count(products, index))
    

    return results 

    
def rejedted_product_weight(products, index=None):
    results = {}
    if index is  None:
        results['rejedted_product_weight'] = products.values('invoice_id').filter(
            invoice_type="RETURN").annotate(
            total=Sum('weight')).aggregate(total__sum=Sum('total'))['total__sum']

    else:
        value_lists = list(set(products.values_list(index, flat=True)))
        for value in value_lists:
            my_filter = Q()
            my_or_filters = {index:value}
            for item in my_or_filters:
                my_filter |= Q(**{item:my_or_filters[item]})
            results[value] = products.filter(my_filter).values('invoice_id').filter(
            invoice_type="RETURN").annotate(
            total=Sum('weight')).aggregate(total__sum=Sum('total'))['total__sum']
    for k,v in results.items():
        if not v:
            results[k] = 0
    return results  


def pure_product_weight(products, index=None):
    # وزن محصولات در تمام فاکتورها
    results = {}
    if index is None:
        results['pure_product_weight'] = factor_product_weight(products, index)['factor_product_weight'] + rejedted_product_weight(products, index)['rejedted_product_weight']
    else:
        results = Counter(factor_product_weight(products, index)) + Counter(rejedted_product_weight(products, index))
    
    return results 


def users_count(products, index=None):
    # تعداد مشتریان
    results = {}
    if index is  None:
        results['users_count'] =  products.values('customer_id').distinct().count()

    else:
        value_lists = list(set(products.values_list(index, flat=True)))
        for value in value_lists:
            my_filter = Q()
            my_or_filters = {index:value}
            for item in my_or_filters:
                my_filter |= Q(**{item:my_or_filters[item]})
            results[value] = products.filter(my_filter).values('customer_id').distinct().count()
    for k,v in results.items():
        if not v:
            results[k] = 0
    return results  


def new_users_count(products, owner, start_date_miladi, end_date_miladi,  index=None):
    # تعداد مشتریان جدید
    other_time_users = Product.objects.filter(
        owner=owner, date_jalali__lt=start_date_miladi
        ).values('customer_id').distinct().values_list('customer_id', flat=True)
    

 

    this_time_users = products.values('customer_id').distinct().values_list('customer_id', flat=True)

    results = {}
    temp = len(list(this_time_users.intersection(other_time_users)))
    if index is  None:
        results['new_users_count'] = Counter(users_count(products, index))['users_count']

    else:
        results = Counter(users_count(products, index))
    for k, v in results.items():
        results[k] = v - temp
    return results


def old_users_count(products, owner, start_date_miladi, end_date_miladi,  index=None):
    # تعداد مشتریان تکراری
    other_time_users = Product.objects.filter(
        owner=owner, 
        date_jalali__lt=start_date_miladi
        ).values('customer_id').distinct().values_list('customer_id', flat=True)
    
    this_time_users = products.values('customer_id').distinct().values_list('customer_id', flat=True)
    
    results = {}
    temp = len(list(this_time_users.intersection(other_time_users)))
    if index is  None:
        results['old_users_count'] = temp

    else:
        results = Counter(users_count(products, index))
    for k, v in results.items():
        results[k] = temp
    return results
    

def percent_users(products, owner, start_date_miladi, end_date_miladi, index=None):
    # درصد مشتریان تکراری
    results = {}
    if index is None:
        if Counter(users_count(products, index))['users_count']:
            results['percent_users'] = Counter(old_users_count(products,owner, start_date_miladi, end_date_miladi, index))['old_users_count']/Counter(users_count(products, index))['users_count']
        else:
            results['percent_users'] = 0 
    else:
        temp = Counter(old_users_count(products, owner, start_date_miladi, end_date_miladi, index))
        for k, v in Counter(users_count(products, index)).items():
            if v:
                results[k] = temp[k]/v
            else:
               results[k] = 0 
    return results 


def percent_rejected_count(products, index=None):
    results = {}
    if index is None:
        if Counter(factor_product_count(products, index))['factor_product_count']:
            results['percent_rejected_count'] = Counter(rejected_product_count(products, index))['rejected_product_count']/Counter(factor_product_count(products, index))['factor_product_count']
        else:
            results['percent_rejected_count'] = 0 
    else:
        temp = Counter(rejected_product_count(products, index))
        for k, v in Counter(factor_product_count(products, index)).items():
            if v:
                results[k] = temp[k]/v
            else:
               results[k] = 0 
    return results


def percent_rejected_amount(products, index=None):
    # درصد مبلغ مرجوعی
    results = {}
    if index is None:
        if Counter(gross_sale(products, index))['gross_sale']:
            results['percent_rejected_amount'] = Counter(gross_rejected(products, index))['gross_rejected']/Counter(gross_sale(products, index))['gross_sale']
        else:
            results['percent_rejected_amount'] = 0 
    else:
        temp = Counter(gross_rejected(products, index))
        for k, v in Counter(gross_sale(products, index)).items():
            if v:
                results[k] = temp[k]/v
            else:
               results[k] = 0 
    return results


def sum_discount(products, index=None):
    # مبلغ تخفیف فاکتورها
    results = {}
    if index is  None:
        results['sum_discount'] = products.values('invoice_id').filter(
            invoice_type="SALES").aggregate(total__sum=Sum('discount'))['total__sum']

    else:
        value_lists = list(set(products.values_list(index, flat=True)))
        for value in value_lists:
            my_filter = Q()
            my_or_filters = {index:value}
            for item in my_or_filters:
                my_filter |= Q(**{item:my_or_filters[item]})
            results[value] = products.filter(my_filter).values('invoice_id').filter(
            invoice_type="SALES").aggregate(total__sum=Sum('discount'))['total__sum']
    for k,v in results.items():
        if not v:
            results[k] = 0
    return results
    

def gross_new_users(products, owner, start_date_miladi, end_date_miladi,  index=None):
    results = {}
    other_time_users = Product.objects.filter(
        owner=owner,
        date_jalali__lt=start_date_miladi
        ).values('customer_id').distinct().values_list('customer_id', flat=True)
    
    this_time_users = products.values('customer_id').distinct().values_list('customer_id', flat=True)
    
    new_users = list(set(this_time_users) - set(list(this_time_users.intersection(other_time_users))))

    if index is  None:
        results['gross_new_users'] = products.values('invoice_id').filter(
            invoice_type="SALES").filter(
            customer_id__in=new_users).annotate(
            quantity_price=F('quantity') * F('unit_price')).values('invoice_id').annotate(
            total=Sum('quantity_price')).aggregate(
            total__avg=Sum('total'))['total__avg']

    else:
        value_lists = list(set(products.values_list(index, flat=True)))
        for value in value_lists:
            my_filter = Q()
            my_or_filters = {index:value}
            for item in my_or_filters:
                my_filter |= Q(**{item:my_or_filters[item]})
            results[value] = products.filter(my_filter).values('invoice_id').filter(
                invoice_type="SALES").filter(
                customer_id__in=new_users).annotate(
                quantity_price=F('quantity') * F('unit_price')).values('invoice_id').annotate(
                total=Sum('quantity_price')).aggregate(
                total__avg=Sum('total'))['total__avg']
    for k,v in results.items():
        if not v:
            results[k] = 0
    return results

        
def gross_sale_per_country(products, index=None):
    results = {}
    if index is  None:
        results["gross_sale_per_country"] = products.values('invoice_id').filter(
            invoice_type="SALES").annotate(
            quantity_price=F('quantity') * F('unit_price')).values('country').annotate(
                country_sale=Sum('quantity_price') ).order_by()
    else:
        value_lists = list(set(products.values_list(index, flat=True)))
        for value in value_lists:
            my_filter = Q()
            my_or_filters = {index:value}
            for item in my_or_filters:
                my_filter |= Q(**{item:my_or_filters[item]})
            results[value] = products.filter(my_filter).values('invoice_id').filter(
            invoice_type="SALES").annotate(
            quantity_price=F('quantity') * F('unit_price')).values('country').annotate(
                country_sale=Sum('quantity_price') ).order_by()
    for k,v in results.items():
        if not v:
            results[k] = 0
    return results

    
def gross_sale_per_product_category(products, index=None):
    results = {}
    if index is  None:
        results["gross_sale_per_product_category"] = products.values('invoice_id').filter(
            invoice_type="SALES").annotate(
            quantity_price=F('quantity') * F('unit_price')).values('product_category').annotate(
                product_sale=Sum('quantity_price') ).order_by()
        
    else:
        value_lists = list(set(products.values_list(index, flat=True)))
        for value in value_lists:
            my_filter = Q()
            my_or_filters = {index:value}
            for item in my_or_filters:
                my_filter |= Q(**{item:my_or_filters[item]})
            results[value] = products.filter(my_filter).values('invoice_id').filter(
            invoice_type="SALES").annotate(
            quantity_price=F('quantity') * F('unit_price')).values('product_category').annotate(
                product_sale=Sum('quantity_price') ).order_by()
    for k,v in results.items():
        if not v:
            results[k] = 0
    return results


def gross_sale_per_product_brand(products, index=None):
    results = {}
    if index is  None:
        results["gross_sale_per_product_brand"] = products.values('invoice_id').filter(
            invoice_type="SALES").annotate(
            quantity_price=F('quantity') * F('unit_price')).values('product_brand').annotate(
                brand_sale=Sum('quantity_price') ).order_by()
        
    else:
        value_lists = list(set(products.values_list(index, flat=True)))
        for value in value_lists:
            my_filter = Q()
            my_or_filters = {index:value}
            for item in my_or_filters:
                my_filter |= Q(**{item:my_or_filters[item]})
            results[value] = products.filter(my_filter).values('invoice_id').filter(
            invoice_type="SALES").annotate(
            quantity_price=F('quantity') * F('unit_price')).values('product_brand').annotate(
                brand_sale=Sum('quantity_price') ).order_by()
    for k,v in results.items():
        if not v:
            results[k] = 0
    return results


def gross_sale_per_customer_gender(products, index=None):
    results = {}
    if index is  None:
        results["gross_sale_per_customer_gender"] = products.values('invoice_id').filter(
            invoice_type="SALES").annotate(
            quantity_price=F('quantity') * F('unit_price')).values('customer_gender').annotate(
                gender_sale=Sum('quantity_price') ).order_by()
        
    else:
        value_lists = list(set(products.values_list(index, flat=True)))
        for value in value_lists:
            my_filter = Q()
            my_or_filters = {index:value}
            for item in my_or_filters:
                my_filter |= Q(**{item:my_or_filters[item]})
            results[value] = products.filter(my_filter).values('invoice_id').filter(
            invoice_type="SALES").annotate(
            quantity_price=F('quantity') * F('unit_price')).values('customer_gender').annotate(
                gender_sale=Sum('quantity_price') ).order_by()
    for k,v in results.items():
        if not v:
            results[k] = 0
    return results


def average_purchase_count(products, start_date_miladi, end_date_miladi,  index=None):
    results = {}

    if index is  None:
        pass

    else:
        temp_end_date = start_date_miladi + relativedelta(months=1)
        temp_start_date = start_date_miladi
        while temp_end_date <= end_date_miladi:
            value_lists = list(set(products.values_list(index, flat=True)))
            R = {}
            for value in value_lists:
                my_filter = Q()
                my_or_filters = {index:value}
                for item in my_or_filters:
                    my_filter |= Q(**{item:my_or_filters[item]})
                    R[value] = products.filter(date_jalali__gt=temp_start_date,
                    date_jalali__lte=temp_end_date).filter(my_filter).values_list('invoice_id',
                    flat=True).filter(
                    invoice_type="SALES").distinct().count()

            temp_end_date = temp_end_date + relativedelta(months=1)
            temp_start_date = temp_start_date + relativedelta(months=1)
            for k, v in R.items():
                try:
                    results[k].append(v)
                except:
                    results[k] = [v]

        if temp_start_date != end_date_miladi:
            R = {}
            for value in value_lists:
                my_filter = Q()
                my_or_filters = {index:value}
                for item in my_or_filters:
                    my_filter |= Q(**{item:my_or_filters[item]})
                    R[value] = products.filter(date_jalali__gt=temp_start_date,
                    date_jalali__lte=end_date_miladi).filter(my_filter).values_list('invoice_id',
                    flat=True).filter(
                    invoice_type="SALES").distinct().count()

            for k, v in R.items():
                try:
                    results[k].append(v)
                except:
                    results[k] = [v]
        
    for k,v in results.items():
        results[k] = sum(v)/len(v)
    return results


def average_customer_liftime(products, start_date_miladi, end_date_miladi, index=None):
    results = {}

    if index is  None:
        pass

    else:
        temp_end_date = start_date_miladi + relativedelta(months=1)
        temp_start_date = start_date_miladi
        last_customers = []
        while temp_end_date <= end_date_miladi:
            value_lists = list(set(products.values_list(index, flat=True)))
            R = {}
            for value in value_lists:
                my_filter = Q()
                my_or_filters = {index:value}
                for item in my_or_filters:
                    my_filter |= Q(**{item:my_or_filters[item]})
                    customers = products.filter(date_jalali__gt=temp_start_date,
                    date_jalali__lte=temp_end_date).filter(my_filter).values_list('customer_id',
                    flat=True).filter(
                    invoice_type="SALES").distinct()
                    common_customers = list(set(customers) & set(last_customers))
                    
                    try:
                        R[value] = 1/abs(len(last_customers)-len(common_customers))
                    except:
                        R[value] = 0
                    last_customers = customers

            temp_end_date = temp_end_date + relativedelta(months=1)
            temp_start_date = temp_start_date + relativedelta(months=1)
            for k, v in R.items():
                try:
                    results[k].append(v)
                except:
                    results[k] = [v]

        if temp_start_date != end_date_miladi:
            R = {}
            for value in value_lists:
                my_filter = Q()
                my_or_filters = {index:value}
                for item in my_or_filters:
                    my_filter |= Q(**{item:my_or_filters[item]})
                    customers = products.filter(date_jalali__gt=temp_start_date,
                    date_jalali__lte=end_date_miladi).filter(my_filter).values_list('customer_id',
                    flat=True).filter(
                    invoice_type="SALES").distinct()
                    common_customers = list(set(customers) & set(last_customers))
                    
                    try:
                        R[value] = 1/abs(len(last_customers)-len(common_customers))
                        # R[value] = abs(len(last_customers)-len(common_customers))
                    except:
                        R[value] = 0

            for k, v in R.items():
                try:
                    results[k].append(v)
                except:
                    results[k] = [v]
        
    for k,v in results.items():
        results[k] = round(sum(v)/len(v), 2)
        # results[k] = sum(v)
    return results


def share_shoping(products, start_date_miladi, end_date_miladi, period):
    results = {
        "new_customers": [],
        "old_customers": [],
        "percent_new_customers": []
    }


    # if type == 30:
    #     step  = relativedelta(months=1)
    # elif type == 1:
    #     step = relativedelta(days=1)
    # elif type == 7:
    #     step  = relativedelta(days=7)
    # else:
    #     step  = relativedelta(months=12)

    temp_end_date = start_date_miladi + relativedelta(days=period)
    temp_start_date = start_date_miladi
    last_customers = []
    results['all_customers'] = gross_sale(products)['gross_sale']
    while temp_end_date <= end_date_miladi:

        filtered_products = products.filter(date_jalali__gt=temp_start_date,
        date_jalali__lte=temp_end_date)
        customers = filtered_products.values_list('customer_id',
            flat=True).filter(
            invoice_type="SALES").distinct()
        
        
        new_customers = list(set(customers) - set(last_customers))
        old_customers = list(set(customers) - set(new_customers))
        
        
        
        results['new_customers'].append(gross_sale(filtered_products.filter(customer_id__in=new_customers))['gross_sale'])
        results['old_customers'].append(gross_sale(filtered_products.filter(customer_id__in=old_customers))['gross_sale'])
        
        try:
            results['percent_new_customers'].append(results['new_customers'][-1] / results['all_customers'])
        except:
            results['percent_new_customers'].append(0)
        
        last_customers += customers
        last_customers = list(set(last_customers))

        temp_end_date = temp_end_date + relativedelta(days=period)
        temp_start_date = temp_start_date + relativedelta(days=period)
    
    if temp_start_date != end_date_miladi:

        filtered_products = products.filter(date_jalali__gt=temp_start_date,
        date_jalali__lte=end_date_miladi)

        customers = filtered_products.values_list('customer_id',
            flat=True).filter(
            invoice_type="SALES").distinct()

        new_customers = list(set(customers) - set(last_customers))
        old_customers = list(set(customers) - set(new_customers))
                
        results['new_customers'].append(gross_sale(filtered_products.filter(customer_id__in=new_customers))['gross_sale'])
        results['old_customers'].append(gross_sale(filtered_products.filter(customer_id__in=old_customers))['gross_sale'])
        try:
            results['percent_new_customers'].append(results['new_customers'][-1] / results['all_customers'])
        except:
            results['percent_new_customers'].append(0)
    return results


def retention(products, start_date_miladi, end_date_miladi, period):
    results = {
        "new_customers": [],
        "retention": [],
    }
    step = relativedelta(days=period)
    temp_end_date = start_date_miladi + step
    temp_start_date = start_date_miladi
    last_customers = []
    old_customers = []
    while temp_end_date <= end_date_miladi:

        filtered_products = products.filter(date_jalali__gt=temp_start_date,
        date_jalali__lte=temp_end_date)
        customers = filtered_products.values_list('customer_id',
            flat=True).filter(
            invoice_type="SALES").distinct()
        
        
        new_customers = list(set(customers) - set(old_customers))
        
        results['new_customers'].append(len(new_customers))
        if len(new_customers) != 0:
            results['retention'].append(
                (sum([1 for i in last_customers if i in new_customers])/len(last_customers))*100 if len(last_customers) != 0 else 100,  
            )
        else:
            results['retention'].append(
                None
            )

        old_customers += customers
        old_customers = list(set(old_customers))
        last_customers = list(set(new_customers))

        temp_end_date = temp_end_date + step
        temp_start_date = temp_start_date + step

    if temp_start_date != end_date_miladi:

        filtered_products = products.filter(date_jalali__gt=temp_start_date,
        date_jalali__lte=end_date_miladi)
        customers = filtered_products.values_list('customer_id',
            flat=True).filter(
            invoice_type="SALES").distinct()
        
        
        new_customers = list(set(customers) - set(old_customers))
        
        results['new_customers'].append(len(new_customers))
        if len(new_customers) != 0:
            results['retention'].append(
                (sum([1 for i in last_customers if i in new_customers])/len(last_customers))*100 if len(last_customers) != 0 else 100,  
            )
        else:
            results['retention'].append(
                0
            )

        old_customers += customers
        old_customers = list(set(old_customers))
        last_customers = list(set(new_customers))   
    return results


def retention_seperation(products, start_date_miladi, end_date_miladi, period, index):
    results = {}

    value_lists = list(set(products.values_list(index, flat=True)))
    for value in value_lists:
        my_filter = Q()
        my_or_filters = {index:value}
        for item in my_or_filters:
            my_filter |= Q(**{item:my_or_filters[item]})
        filtered_products = products.filter(my_filter)
        results[value] =  retention(filtered_products, start_date_miladi, end_date_miladi, period)
    return results


def get_result(products,owner, start_date_miladi1, end_date_miladi1):
    results = {
        "sale_factor_count":      sale_factor_count(products)['sale_factor_count'],
        "rejected_factor_count":  rejected_factor_count(products)['rejected_factor_count'],
        "factor_product_average": factor_product_average(products)['factor_product_average'],
        "factor_rows_average":    factor_rows_average(products)['factor_rows_average'],
        "factor_amount_average":  factor_amount_average(products)['factor_amount_average'],
        "factor_amount_product_average":  factor_amount_product_average(products)['factor_amount_product_average'],
        "customer_income_average":  customer_income_average(products)['customer_income_average'],
        "gross_sale":               gross_sale(products)['gross_sale'],
        "factor_product_count":     factor_product_count(products)['factor_product_count'],
        "factor_product_weight":    factor_product_weight(products)['factor_product_weight'],
        "factor_commisions":        factor_commisions(products)['factor_commisions'],
        "pure_factor_counts":       pure_factor_counts(products)['pure_factor_counts'],
        "pure_gross_sale":          pure_gross_sale(products)['pure_gross_sale'],
        "gross_rejected":           gross_rejected(products)['gross_rejected'],
        "pure_sale":                pure_sale(products)['pure_sale'],
        "rejected_product_count":   rejected_product_count(products)['rejected_product_count'],
        "pure_product_count":       pure_product_count(products)['pure_product_count'],
        "rejedted_product_weight":   rejedted_product_weight(products)['rejedted_product_weight'],
        "pure_product_weight":       pure_product_weight(products)['pure_product_weight'],
        "users_count":               users_count(products)['users_count'],
        "new_users_count":           new_users_count(products,owner, start_date_miladi1,
                     end_date_miladi1)['new_users_count'],
        "old_users_count":            old_users_count(products,owner, start_date_miladi1,
                     end_date_miladi1)['old_users_count'],
        "percent_users":               percent_users(products, owner, start_date_miladi1,
                     end_date_miladi1)['percent_users'],                
        "percent_rejected_count":     percent_rejected_count(products)['percent_rejected_count'],
        "percent_rejected_amount":     percent_rejected_amount(products)['percent_rejected_amount'],
        "sum_discount":                 sum_discount(products)['sum_discount'],
        "gross_new_users":               gross_new_users(products, owner, start_date_miladi1,
                     end_date_miladi1)['gross_new_users'],
        "gross_sale_per_country":       gross_sale_per_country(products)['gross_sale_per_country'],
        "gross_sale_per_product_category":  gross_sale_per_product_category(products)['gross_sale_per_product_category'],
        "gross_sale_per_product_brand":  gross_sale_per_product_brand(products)['gross_sale_per_product_brand'],
        "gross_sale_per_customer_gender":  gross_sale_per_customer_gender(products)['gross_sale_per_customer_gender'],
    }
    return results


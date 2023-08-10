
import                                        datetime
from                                          tabulate import tabulate
from sklearn.cluster                          import KMeans
from persiantools.jdatetime                   import JalaliDate
import                                        lifetimes
from datetime                                 import timedelta


def r_score(x, quintiles, config_param):
    if x <= quintiles['Recency'][float((config_param['recency1']/100))]:
        return 5
    elif x <= quintiles['Recency'][float((config_param['recency2']/100))]:
        return 4
    elif x <= quintiles['Recency'][float((config_param['recency3']/100))]:
        return 3
    elif x <= quintiles['Recency'][float((config_param['recency4']/100))]:
        return 2
    else:
        return 1


def f_score(x, c, quintiles, config_param):
    if x <= quintiles[c][float((config_param['frequency1']/100))]:
        return 1
    elif x <= quintiles[c][float((config_param['frequency2']/100))]:
        return 2
    elif x <= quintiles[c][float((config_param['frequency3']/100))]:
        return 3
    elif x <= quintiles[c][float((config_param['frequency4']/100))]:
        return 4
    else:
        return 5    


def m_score(x, c, quintiles, config_param):
    if x <= quintiles[c][float((config_param['monetary1']/100))]:
        return 1
    elif x <= quintiles[c][float((config_param['monetary2']/100))]:
        return 2
    elif x <= quintiles[c][float((config_param['monetary3']/100))]:
        return 3
    elif x <= quintiles[c][float((config_param['monetary4']/100))]:
        return 4
    else:
        return 5


maps_11 = {
    'At risk': [151, 251, 152, 252, 142, 242, 143, 243, 144, 244, 134, 234, 124,
                224, 145, 245, 135, 235, 125, 225, 115, 215],
    'Potantial loyalist': [351, 451, 551, 341, 441, 541, 431, 531, 352, 452, 552,
                342, 442,542, 332, 432, 532, 333, 433, 533],
    'Lost': [141, 131, 121, 111, 132, 122, 112, 133, 123, 113, 114 ],
    'Hibernating': [241, 231, 221, 211, 232, 222, 212, 233, 223, 213, 214],
    'About to sleep': [331, 321, 311, 322, 312, 323, 313],
    'New Customer':[421, 411, 521, 511, 422, 412, 522, 512],
    'Promising': [423, 413, 523, 513, 424, 414, 524, 514, 314, 325, 315, 425, 415, 525, 515],
    'Loyal': [353, 453, 553, 343, 443, 543, 354, 344, 444, 355, 345],
    'Need Attention': [334, 434, 534, 324, 335, 435, 535], 
    'Champions': [454, 554, 544, 455, 555, 445, 545],
    'Can not Lose them': [155, 255, 154, 254, 153, 253 ]
}

maps_6 = {
    'At risk': [151, 251, 152, 252, 153, 253, 143, 243, 154, 254, 144, 244, 134, 234,
                155, 255, 145, 245, 135, 235],
    'Lost': [141, 131, 121, 111, 241, 231, 221, 211, 142, 132, 122, 112, 242, 232, 222, 212, 
             133, 123, 113, 233, 223, 213, 124, 224, 114, 214, 125, 225, 115, 215],
    'Loyal': [351,451, 551, 341, 441, 541, 331, 431, 531, 352, 452, 552, 342, 442, 542, 332, 432, 532,
            353, 343, 333, 433, 553, 443, 354, 344, 334, 434, 534, 335, 345, 435],
    'New Customer':[321, 421, 521, 311, 411, 511, 322, 422, 522, 312, 412, 512, 323, 423, 523, 313, 413, 513 ], 
    'Promising': [324, 424, 524, 314, 414, 514, 325, 425, 525, 315, 415, 515],
    'Champions': [453, 553, 543, 454, 554, 444, 544, 355, 455, 555, 445, 545, 535]
}

maps_3 = {
    'Lost': [151, 141, 131, 121, 111, 251, 241, 231, 221, 211, 152, 142, 132, 122, 112, 252, 242, 232, 222, 212,
            153, 143, 133, 123, 113, 253, 243, 233, 223, 213, 154, 144, 134, 124, 114, 254, 244, 234, 224, 214,
            155, 145, 135, 125, 115, 255, 245, 235, 225, 215],
    'Champions': [351, 451, 551,341, 441, 541, 331, 431, 531, 352, 452, 552,342, 442, 542, 332, 432, 532,
                353, 453, 553,343, 443, 543, 333, 433, 533, 354, 454, 554,344, 444, 544, 334, 434, 534,
                355, 455, 555,345, 445, 545, 335, 435, 535], 
    'New Customer':[321, 421, 521, 311, 411, 511, 322, 422, 522, 312, 412, 512, 323, 423, 523, 313, 413, 513, 
                324, 424, 524, 314, 414, 514, 325, 425, 525, 315, 415, 515]    
    
}

def map_to_segment(x, segments):
    if segments == 11:
        for k, v in maps_11.items():
            if int(x) in v:
                return k
    if segments == 6:
        for k, v in maps_6.items():
            if int(x) in v:
                return k
    if segments == 3:
        for k, v in maps_3.items():
            if int(x) in v:
                return k
    return None 


def get_rfm_score(df, segments, config_param, period = 365):

    df.dropna(subset=['customer_id'], inplace=True)
    
    # print(df[['quantity', 'invoice_id']])
    # print(df['invoice_id'].value_counts().head())
    df['date_jalali'] = df['date_jalali'].apply(
        lambda x: datetime.datetime.fromisoformat(x))
    

    if config_param['recency_type'] == "pure_sale":
        df['Price'] = df['quantity'] * df['unit_price']

    elif config_param['recency_type'] == "impure_sale":
        df['Price'] = [item[0]*item[1] if item[2] == "SALES" else 0 for item in df[['quantity', 'unit_price', 'invoice_type']].values  ]

    elif config_param['recency_type'] == "average_factor_amount":
        df['Price'] = df['quantity'] * df['unit_price']

    elif config_param['recency_type'] == "impure_sale_products_count":
        df['Price'] = [item[0] if item[2] == "SALES" else 0 for item in df[['quantity', 'unit_price', 'invoice_type']].values  ]

    elif config_param['recency_type'] == "sale_products_weights":
        df['Price'] = [item[0] if item[2] == "SALES" else 0 for item in df[['weight', 'unit_price', 'invoice_type']].values  ]

    elif config_param['recency_type'] == "products_weights":
        df['Price'] = [item[0] for item in df[['weight', 'unit_price', 'invoice_type']].values  ]

    elif config_param['recency_type'] == "pure_factor_amount":
        df['Price'] = [item[0]*item[1] - item[3]*(item[0]*item[1]) if item[2] == "SALES" else 0  for item in df[['weight', 'unit_price', 'invoice_type', 'discount']].values  ]




    orders = df.groupby(['invoice_id', 'date_jalali', 'customer_id']).agg({'Price': lambda x: x.sum()
                    }).reset_index()



    NOW = orders['date_jalali'].max() + timedelta(days=1)
    orders['DaysSinceOrder'] = orders['date_jalali'].apply(lambda x: (NOW - x).days)

    
    if config_param['frequncy_type'] == "factor_count":
        orders['factors_count'] = orders['customer_id'].apply(lambda x: len(df.query(f'customer_id == "{x}"')['invoice_id'].unique()))

    elif config_param['frequncy_type'] == "average_product_count_per_factor":
        orders['factors_count'] = orders['customer_id'].apply(lambda x: sum(df.query(f'customer_id == "{x}"')['quantity'])/ len(df.query(f'customer_id == "{x}"')['quantity']))
    
    elif config_param['frequncy_type'] == "average_row_count_per_factor":
        orders['factors_count'] = orders['customer_id'].apply(lambda x: sum([1 for item in df.query(f'customer_id == "{x}"')['quantity'] ]) )

    elif config_param['frequncy_type'] == "pure_factor_count":
        orders['factors_count'] = orders['customer_id'].apply(lambda x: sum([1 for item in df.query(f'customer_id == "{x}"')['invoice_type'] if item == "SALES" ]) )
    
    elif config_param['frequncy_type'] == "uniq_product_count":
        orders['factors_count'] = orders['customer_id'].apply(lambda x: len(df.query(f'customer_id == "{x}"')['product_name'].unique()))

    elif config_param['frequncy_type'] == "pure_sale_product_count":
        orders['factors_count'] = orders['customer_id'].apply(lambda x: 
                                    sum([item[1] for item in df.query(f'customer_id == "{x}"')[['invoice_type', 'quantity']].values if item[0] == "SALES" ]) )

    # print(orders)

    orders1 = orders.groupby(['customer_id']).agg({'Price': lambda x: x.sum(), 'factors_count': lambda x: x.sum()/len(x),
                    'DaysSinceOrder': lambda x: x.min() }).reset_index()

    rfm = orders1
    rfm.rename(columns={'DaysSinceOrder': 'Recency', 'factors_count': 'Frequency',
            'Price': 'Monetary'}, inplace=True)
    

    quintiles = rfm[['Recency']].quantile([float((config_param['recency1']/100)),
            float((config_param['recency2']/100)), float((config_param['recency3']/100)), float((config_param['recency4']/100))]).to_dict()
    rfm['R'] = rfm['Recency'].apply(lambda x: r_score(x, quintiles, config_param))

    quintiles = rfm[['Frequency']].quantile([float((config_param['frequency1']/100)),
            float((config_param['frequency2']/100)), float((config_param['frequency3']/100)), float((config_param['frequency4']/100))]).to_dict()
    rfm['F'] = rfm['Frequency'].apply(lambda x: f_score(x, 'Frequency', quintiles, config_param))

    quintiles = rfm[['Monetary']].quantile([float((config_param['monetary1']/100)),
            float((config_param['monetary2']/100)), float((config_param['monetary3']/100)), float((config_param['monetary4']/100))]).to_dict()
    rfm['M'] = rfm['Monetary'].apply(lambda x: m_score(x, 'Monetary', quintiles, config_param))

    rfm['RFM Score'] = rfm['R'].map(str) + rfm['F'].map(str) + rfm['M'].map(str)
    rfm['Customer_segment'] = rfm['RFM Score'].apply(lambda x: map_to_segment(x, segments))
    # print(rfm)
    return rfm 


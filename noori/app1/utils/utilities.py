def remove_from_list(input_list, elements):
    for i in elements:
        try:
            input_list.remove(i)
        except:
            pass
    return input_list


def get_param_filter(keys, json_data, foreign_keys={}):
    params = {}
    for i in keys:
        temp = i + '__icontains'
        params[temp] = json_data['params'].get(i)
    
    for k, v in foreign_keys.items():
        params[k] = v
    return params

def obj_filter(keys, search):
    params = {}
    for i in keys:
        temp = i + '__icontains'
        params[temp] = search

    return params
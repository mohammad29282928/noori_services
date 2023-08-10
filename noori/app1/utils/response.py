def permission_response():  
    response_data = ({
        "error"      : {
            "message"    : 'Access permission error',
            "hasError"   : True,
        },
        "results"      : {
        } 
    })
    return response_data


def error_response(ver="ver", seq="sqe", e=""):
    response_data = ({
        "error"      : {
            "seq"        : seq, 
            "ver"        : ver,
            "message"    : str(e),
            "hasError"   : True,
        },
        "results"      : {
        } 
    })
    return response_data


def result_response(ver="ver", seq="sqe", message="", results={}):
    response_data = ({
    "error"      : {
        "message"    : message,
        "hasError"   : False
    },
    "results"      : results 
    })
    return response_data
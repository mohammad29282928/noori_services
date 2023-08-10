from django.shortcuts                         import render
from rest_framework.views                     import APIView
from rest_framework                           import status
from rest_framework.response                  import Response
from django.contrib.auth                      import authenticate
from django.contrib.auth.models               import update_last_login
from rest_framework.authtoken.models          import Token


from .serializers.user                        import UserSerializer 



class UserLoginView(APIView):
    

    def post(self, request,):
        if 'username' in self.request.data: 
            username = request.data.get("username")
        else:
            response_data = ({  
                "detail": "username field is required",
                "isSuccess": False
            })
            data_status = status.HTTP_200_OK    
            return Response(response_data, status = data_status) 

        if 'password' in self.request.data: 
            password = request.data.get("password")
            
        else:
            response_data = ({  
                "detail": "password field is required",
                "isSuccess": False
            })
            data_status = status.HTTP_200_OK    
            return Response(response_data, status = data_status) 

        user = authenticate(
            username = username, 
            password = password
        )
        
        if user is not None:
            if user.is_active:
                update_last_login(None, user)  
                # terminateOtherSessions(user)
                token, created = Token.objects.get_or_create(user = user)
                userSerializer = UserSerializer(user)
                response_data = ({  
                    "detail"    : "Welcome",
                    "key"       : token.key,
                    "results"   : userSerializer.data,
                    "isSuccess" : True
                })
                data_status = status.HTTP_200_OK    
                return Response(response_data, status = data_status) 

            else:
                response_data = ({  
                    "detail"    : "User is not active",
                    "isSuccess" : False
                })
                
                data_status = status.HTTP_200_OK    
                return Response(response_data, status = data_status) 
        else:
            response_data = ({  
                    "detail"    : "Incorrect username or password",
                    "isSuccess" : False
                })
            data_status = status.HTTP_200_OK    
            return Response(response_data, status = data_status) 

def terminateOtherSessions(user):
    # only one user active
    try:
        old_token = Token.objects.get(user = user)
        old_token.delete()
        return True
    except:
        return False
        
from .utils.IsAuthenticated                  import IsAuthenticated


class UserLogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request,):

        # get user object 
        owner = request.user
        if 1:
            ## terminate all sessions
            terminateOtherSessions(owner)
            response_data = ({  
                "detail"    : "You have successfully loged out",
                "isSuccess" : True,
            })
            data_status = status.HTTP_200_OK    
            return Response(response_data, status = data_status)
        else:
            response_data = ({  
                "detail"    : "please check your data",
                "isSuccess" : False,
            })
            data_status = status.HTTP_200_OK    
            return Response(response_data, status = data_status)

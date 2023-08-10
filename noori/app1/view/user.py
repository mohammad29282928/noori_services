from sqlite3 import Time
from django.shortcuts                         import render
from rest_framework.views                     import APIView
from rest_framework                           import status
from rest_framework.response                  import Response
from django.contrib.auth                      import authenticate
from django.contrib.auth.models               import update_last_login
from rest_framework.authtoken.models          import Token
import json
from rest_framework.exceptions                import APIException
import datetime
from django.db.models                         import ForeignKey

from ..models                                 import Agent, User
from ..utils.response                         import permission_response, error_response, result_response
from ..utils.utilities                        import remove_from_list, get_param_filter, obj_filter
from django.db.models                         import Q
from django.core.files                        import File

from django.core.files.storage                import default_storage
from django.core.files.base                   import ContentFile
from django.conf                              import settings
from django.core.files.storage                import FileSystemStorage

from ..utils.IsAuthenticated                  import IsAuthenticated
from ..serializers.agent                      import AgentSerializer
from ..serializers.user                       import UserSerializer








class AgentListView(APIView):
    # permission_classes = [IsAuthenticated]

    def post(self, request): 
        owner        = self.request.user  
        if not 1:
            response_data = permission_response()
            return Response(response_data, status = status.HTTP_200_OK)
        else:
            ver = 0
            seq = 6
            try:
                if owner.is_superuser:
                    
                    results = []
                    agents = Agent.objects.all()
                    for agent in agents:
                        results.append({
                            "title": agent.title,
                            "description": agent.description,
                            "created_at": agent.created_at
                        })
                    message= "list of agent" 
                else:
                    results = []
                    message= "this request needs to superuser permision" 

                response_data = result_response(ver, seq, message, results)
                data_status   = status.HTTP_200_OK    
                return Response(response_data, status = data_status)
            except Exception as e:
                response_data = error_response(ver,seq,e)
                data_status = status.HTTP_200_OK    
                return Response(response_data, status = data_status)


class AgentAddView(APIView):
    # permission_classes = [IsAuthenticated]

    def post(self, request): 
        owner        = self.request.user  
        if not 1:
            response_data = permission_response()
            return Response(response_data, status = status.HTTP_200_OK)
        else:
            ver = 0
            seq = 6
            try:
                if owner.is_superuser:
                    results = []

                    title = request.POST.get('title', '')
                    description = request.POST.get('description', '')
                    if len(title) < 3:
                        message = "title must have length more than 3 charachter "

                    elif len(Agent.objects.filter(title=title)):
                        message = "this agent exist "
                    
                    else:
                        agent = Agent(title=title, description=description)
                        agent.save()
                        message= "an agent created" 
                else:
                    results = []
                    message= "this request needs to superuser permision" 
                print(message)
                response_data = result_response(ver, seq, message, results)
                data_status   = status.HTTP_200_OK    
                return Response(response_data, status = data_status)
            except Exception as e:
                response_data = error_response(ver,seq,e)
                data_status = status.HTTP_200_OK    
                return Response(response_data, status = data_status)


class AgentDelView(APIView):
    # permission_classes = [IsAuthenticated]

    def post(self, request): 
        owner        = self.request.user  
        if not 1:
            response_data = permission_response()
            return Response(response_data, status = status.HTTP_200_OK)
        else:
            ver = 0
            seq = 6
            try:
                if owner.is_superuser:
                    results = []

                    title = request.POST.get('title', '')
                    try:
                        agent = Agent.objects.get(title=title)
                        agent.delete()
                        message= "an agent created" 
                    except:
                        message ="agent not exist"
                else:
                    results = []
                    message= "this request needs to superuser permision" 
                print(message)
                response_data = result_response(ver, seq, message, results)
                data_status   = status.HTTP_200_OK    
                return Response(response_data, status = data_status)
            except Exception as e:
                response_data = error_response(ver,seq,e)
                data_status = status.HTTP_200_OK    
                return Response(response_data, status = data_status)










class UserListView(APIView):
    # permission_classes = [IsAuthenticated]

    def post(self, request): 
        owner        = self.request.user  
        if not 1:
            response_data = permission_response()
            return Response(response_data, status = status.HTTP_200_OK)
        else:
            ver = 0
            seq = 6
            try:

                if owner.agent:
                    results = []
                    users = User.objects.filter(agent=owner.agent)
                    for item in users:
                        try:
                            agent = item.agent.title
                        except:
                            agent = None
                        results.append(
                            {
                                "phone": item.phone,
                                "is_superuser": item.is_superuser,
                                "agent": agent,
                                "is_active": item.is_active,
                                "adduser_permission": item.adduser_permission,
                                "deluser_permission":item.deluser_permission, 
                                "username": item.username, 
                                "last_seen":item.last_seen
                            }
                        )
                else:
                    results = []
                    users = User.objects.all()

                    for item in users:
                        
                        try:
                            agent = item.agent.title
                        except:
                            agent = None

                        results.append(
                            {
                                "phone": item.phone,
                                "is_superuser": item.is_superuser,
                                "agent": agent,
                                "is_active": item.is_active,
                                "adduser_permission": item.adduser_permission,
                                "deluser_permission":item.deluser_permission, 
                                "username": item.username, 
                                "last_seen":item.last_seen
                            }
                        )

                message= "list of users" 
                response_data = result_response(ver, seq, message, results)
                data_status   = status.HTTP_200_OK    
                return Response(response_data, status = data_status)
            except Exception as e:
                response_data = error_response(ver,seq,e)
                data_status = status.HTTP_200_OK    
                return Response(response_data, status = data_status)


class UserAddView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request): 
        owner        = self.request.user  
        if not 1:
            response_data = permission_response()
            return Response(response_data, status = status.HTTP_200_OK)
        else:
            ver = 1
            seq = 6
            try:
                user_info = {}
                user_info['username']         = request.POST.get('username', '')
                pass1        = request.POST.get('password1', '')
                pass2        = request.POST.get('password2', '')
                user_info['email']            = request.POST.get('email', '')
                user_info['phone']            = request.POST.get('phone', '')
                user_info['sendsms_permission']            = False if request.POST.get('sendsms_permission') == 'false' else True
                user_info['adduser_permission']            = False if request.POST.get('adduser_permission') == 'false' else True
                user_info['first_name']      = request.POST.get('first_name', '')
                user_info['last_name']      = request.POST.get('last_name', '')
                

                if owner.agent:

                    user_info['agent'] = owner.agent
                else:
                    agent_title = request.POST.get('agent_title', '')
                    agent             = Agent.objects.filter(title=agent_title) 
                    if len(agent):
                        user_info['agent'] = agent[0]
                    else:
                        user_info['agent'] = ''

                    
                if pass1 != pass2:
                    message = "password1 and password2 are not equal"
                
                elif user_info['agent'] == '':
                    message = "agent needed"
                elif user_info['email'] == '':
                    message = "email needed"
                    
                elif len(User.objects.filter(username=user_info['username'])):
                    message = "user does exist"
                elif len(user_info['username']) < 4:
                    message = "username must have length more than 4"
                else:
                    user_info['password'] = pass1
                    print("user_info", user_info)
                    user = User.objects.create_user(**user_info)
                    user.save()
                    token, created = Token.objects.get_or_create(user=user)
                    print(token)
                    message= 'An user with username '+ str(user_info['username']) +' added' 

                print(message)
                response_data = result_response(ver, seq, message,  results = [])
                data_status = status.HTTP_200_OK    
                return Response(response_data, status = data_status)
            except Exception as e:
                response_data = error_response(ver,seq,e)
                data_status = status.HTTP_200_OK    
                return Response(response_data, status = data_status)


class UserDeleteView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request): 
        owner        = self.request.user  
        if not 1:
            response_data = permission_response()
            return Response(response_data, status = status.HTTP_200_OK)
        else:

            ver = 5
            seq = 1
            try:
                username  = request.POST.get('username', '')
                try:
                    obj = User.objects.get(username=username)
                    if obj.is_superuser:
                        message = 'you don not have permision'
                    else:
                        obj.delete()
                        message = 'the following users with usernames: ' + str(username) + " was deleted"
                except:
                    message = "user is not exist"
                
                print(message)
                response_data = result_response(ver, seq, message)
                data_status = status.HTTP_200_OK    
                return Response(response_data, status = data_status)
            except Exception as e:
                response_data = error_response(ver,seq,e)
                data_status = status.HTTP_200_OK    
                return Response(response_data, status = data_status)

import os
import uuid
class UserEditView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request): 
        owner        = self.request.user  
        if not 1:
            response_data = permission_response()
            return Response(response_data, status = status.HTTP_200_OK)
        else:
            json_data     = request.data
            # json_data     = json.loads(request.body, encoding="utf8", errors="ignore")
            ver = json_data.get("ver")
            seq = json_data.get("seq")

            try:
                username           = json_data.get('username', '')
                # print("username", username)
                # print(request.FILES.get('image', 0))
                user               = User.objects.get(username=username)  
                first_name         = json_data.get('first_name',     user.first_name)
                last_name          = json_data.get('last_name',      user.last_name)
                email              = json_data.get('email',          user.email)
                phone              = json_data.get('phone',          user.phone)
                agent_id           = json_data.get('agent_id',       user.agent.id)
                image              = request.FILES.get('image', 0)
        
                if image:
                    fs = FileSystemStorage()
                    ext      = image.name.split('.')[-1]              # Seprate the file ext.
                    filename = "%s.%s" % (str(uuid.uuid4()), ext) 
                    filename = os.path.join(f"userImages/{filename}")
                    filename = fs.save(filename, image)
                    image = settings.MEDIA_URL+filename
                    
                else:
                    image = user.image

                User.objects.filter(username=username).update(first_name=first_name, last_name=last_name, email=email, phone=phone,
                         agent= Agent.objects.get(id=agent_id), image=image)
                # os.remove(os.path.join(settings.MEDIA_ROOT, filename))
                message= "user updated with params " +  str(json_data)
                response_data = result_response(ver, seq, message)
                data_status = status.HTTP_200_OK    
                return Response(response_data, status = data_status)
            except Exception as e:
                response_data = error_response(ver,seq,e)
                data_status = status.HTTP_200_OK    
                return Response(response_data, status = data_status)
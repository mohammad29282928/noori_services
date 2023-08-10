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

from ..serializers.agent                      import AgentSerializer
from ..models                                 import Agent
from ..utils.response                         import permission_response, error_response, result_response
from ..utils.utilities                        import remove_from_list, get_param_filter, obj_filter
from django.db.models                         import Q

from ..utils.IsAuthenticated                  import IsAuthenticated


class AgentListView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request): 
        owner        = self.request.user  
        if not 1:
            response_data = permission_response()
            return Response(response_data, status = status.HTTP_200_OK)
        else:
            json_data     = json.loads(request.body)
            ver = json_data.get("ver")
            seq = json_data.get("seq")
            
            try:
                limit         = int(json_data['params'].get('limit', len(Agent.objects.all()))) 
                offset        = int(json_data['params'].get('offset', 0)) 
                keys          = remove_from_list(list(json_data['params'].keys()), ['limit', 'offset' ])
                foreign_keys  = {}
                agent       = int(json_data['params'].get('agent', 0))

                if agent:
                    foreign_keys['agent'] = Agent.objects.get(id=agent)
                    keys                    = remove_from_list(keys, ['agent'])
                keys = remove_from_list(keys, ['search'])
                if json_data['params'].get('search', 0):
                    search = json_data['params'].get('search')
                    plants = Agent.objects.filter(Q(title__icontains=search) | Q(description__icontains=search) 
                        | Q(updated_at__icontains=search) | Q(created_at__icontains=search)
                        )
                    serializer    = AgentSerializer(plants, many=True,  context={'request': request})
                elif 'id' in keys:
                    serializer    = AgentSerializer(Agent.objects.filter(id=int(json_data['params'].get('id'))), many=True,  context={'request': request})
                elif keys or list(foreign_keys.keys()):
                    serializer    = AgentSerializer(Agent.objects.filter(**get_param_filter(keys, json_data, foreign_keys)), many=True,  context={'request': request})
                else:
                    serializer    = AgentSerializer(Agent.objects.all(), many=True,  context={'request': request})
                message= "list of agents" 
                results = {
                    "records"   : serializer.data[offset:offset+limit],
                    "total"     : len(Agent.objects.all())
                }
                response_data = result_response(ver, seq, message, results)
                data_status   = status.HTTP_200_OK    
                return Response(response_data, status = data_status)
            except Exception as e:
                response_data = error_response(ver,seq,e)
                data_status = status.HTTP_200_OK    
                return Response(response_data, status = data_status)


class AgentAddView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request): 
        owner        = self.request.user  
        if not 1:
            response_data = permission_response()
            return Response(response_data, status = status.HTTP_200_OK)
        else:
            json_data     = json.loads(request.body)
            ver = json_data.get("ver")
            seq = json_data.get("seq")
            try:
                title        = json_data['params'].get('title')
                description      = json_data['params'].get('description')
 
                id            = json_data['params'].get('id', 0)
                if id:
                    agent         = Agent(title=title, description=description)
                else:
                    agent         = Agent(title=title, description=description)
                agent.save()
                message= 'An Agent with id '+ str(agent.id) +' added' 
                response_data = result_response(ver, seq, message)
                data_status = status.HTTP_200_OK    
                return Response(response_data, status = data_status)
            except Exception as e:
                response_data = error_response(ver,seq,e)
                data_status = status.HTTP_200_OK    
                return Response(response_data, status = data_status)


class AgentDeleteView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request): 
        owner        = self.request.user  
        if not 1:
            response_data = permission_response()
            return Response(response_data, status = status.HTTP_200_OK)
        else:
            json_data     = json.loads(request.body)
            ver = json_data.get("ver")
            seq = json_data.get("seq")
            try:
                deleted_ids  = json_data['params'].get('id', [])
                for i in deleted_ids:
                    obj = Agent.objects.get(id=i)
                    obj.delete()
                message = 'the following agents with id: ' + str(deleted_ids) + " are deleted"
                response_data = result_response(ver, seq, message)
                data_status = status.HTTP_200_OK    
                return Response(response_data, status = data_status)
            except Exception as e:
                response_data = error_response(ver,seq,e)
                data_status = status.HTTP_200_OK    
                return Response(response_data, status = data_status)


class AgentEditView(APIView):
    def post(self, request): 
        owner        = self.request.user  
        if not 1:
            response_data = permission_response()
            return Response(response_data, status = status.HTTP_200_OK)
        else:
            json_data     = json.loads(request.body)
            ver = json_data.get("ver")
            seq = json_data.get("seq")
            try:
                agent_id      = json_data['params'].get('id', '')
                agent         = Agent.objects.get(id=agent_id)      
                title         = json_data['params'].get('title',     agent.title)
                description   = json_data['params'].get('description',     agent.description)
                Agent.objects.filter(id=agent_id).update(title=title, description=description, updated_at=datetime.datetime.now())
                message= "agent updated with params " +  str(json_data['params'])
                response_data = result_response(ver, seq, message)
                data_status = status.HTTP_200_OK    
                return Response(response_data, status = data_status)
            except Exception as e:
                response_data = error_response(ver,seq,e)
                data_status = status.HTTP_200_OK    
                return Response(response_data, status = data_status)
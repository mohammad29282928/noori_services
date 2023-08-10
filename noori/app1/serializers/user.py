from ..models                            import User
from rest_framework.serializers          import ModelSerializer
from .agent                              import AgentSerializer


class UserSerializer(ModelSerializer): 

    agent      = AgentSerializer(many = False, required = False)

    class Meta:
        model = User

        fields = [
            'id', 
            'username', 
            'first_name', 
            'last_name', 
            'email',
            'phone',
            'agent', 
            'password',
            'is_active',
        ]

        read_only_fields =[
            'id'
        ]
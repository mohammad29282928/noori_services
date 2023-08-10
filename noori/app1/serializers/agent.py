from ..models                            import Agent
from rest_framework.serializers          import ModelSerializer


class AgentSerializer(ModelSerializer):

    class Meta:
        model = Agent

        fields = [
            'id', 
            'title', 
            'description', 
            'created_at'
        ]

        read_only_fields = [
            'id'
        ]
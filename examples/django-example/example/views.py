from rest_framework import generics
from example.models import SimpleMessage
from example.serializers import SimpleMessageSerializer

# Create your views here.
class SimpleMessageList(generics.ListCreateAPIView):
    model = SimpleMessage
    serializer_class = SimpleMessageSerializer
    queryset = SimpleMessage.objects.all()

class SimpleMessageDetail(generics.RetrieveDestroyAPIView):
    model = SimpleMessage
    serializer_class = SimpleMessageSerializer

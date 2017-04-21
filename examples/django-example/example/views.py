from rest_framework import generics
from example.models import SimpleMessage, Problem
from example.serializers import SimpleMessageSerializer, ProblemSerializer

# Create your views here.
class SimpleMessageList(generics.ListCreateAPIView):
    model = SimpleMessage
    serializer_class = SimpleMessageSerializer
    queryset = SimpleMessage.objects.all()


class SimpleMessageDetail(generics.RetrieveUpdateDestroyAPIView):
    model = SimpleMessage
    serializer_class = SimpleMessageSerializer
    queryset = SimpleMessage.objects.all()


class ProblemList(generics.ListCreateAPIView):
    model = Problem
    serializer_class = ProblemSerializer
    queryset = Problem.objects.all()


class ProblemDetail(generics.RetrieveUpdateDestroyAPIView):
    model = Problem
    serializer_class = ProblemSerializer
    queryset = Problem.objects.all()

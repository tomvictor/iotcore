from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView


class TestView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        data = {"date": "test"}
        return Response(data, status.HTTP_200_OK)

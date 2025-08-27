from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.pagination import PageNumberPagination
from django.db.models import Q
from django.shortcuts import get_object_or_404
from django.core.paginator import Paginator, EmptyPage
from Application.models import *
from .serializers import *
import json
from datetime import datetime, timedelta
from .permissions import *

class CustomPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 10
    
    def get_paginated_response(self, data):
        return Response({
            'links': {
                'next': self.get_next_link(),
                'previous': self.get_previous_link()
            },
            'count': self.page.paginator.count,
            'total_pages': self.page.paginator.num_pages,
            'current_page': self.page.number,
            'page_size': self.page_size,
            'results': data
        }) 


class StudentDetailsView(APIView):
    pagination_class = CustomPagination
    permission_class = SuperUSerAndStaffOnly
    
    def get(self, request):
        
        name = request.query_params.get('name')
        students = Profile.objects.all()
        if name:
            students = students.filter(Q(name__icontains=name) | Q(email__icontains=name))     
        paginator = self.pagination_class()
        page = paginator.paginate_queryset(students, request)
        if page is not None:
            serializer = StudentSerializer(page, many=True, context={'request': request})
            return paginator.get_paginated_response(serializer.data)
        
        serializer = StudentSerializer(page, many=True, context={'request': request})
        return Response({'results': serializer.data})

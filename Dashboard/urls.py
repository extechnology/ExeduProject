from django.urls import path
from .views import *


urlpatterns = [ 
               
    path('student-details/',StudentDetailsView.as_view(),name='student-details'),
]
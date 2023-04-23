from django.urls import path, include
import os
import sys
print("path:", sys.path);
from . import views




urlpatterns = [
    path('', views.receive_codeData, name = 'receive_codeData'),
]

from django.urls import path
from . import views

app_name = 'crm_core'

urlpatterns = [
    path('', views.HomeView.as_view(), name='home'),
]


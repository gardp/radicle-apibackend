from django.shortcuts import render

# Create your views here.
from rest_framework import generics 
from .models import Address, Contact
from .serializers import AddressSerializer, ContactSerializer
from rest_framework import viewsets 
from rest_framework import permissions  

class AddressViewSet(viewsets.ModelViewSet):
    queryset = Address.objects.all()
    serializer_class = AddressSerializer
    permission_classes = [permissions.AllowAny]

class ContactViewSet(viewsets.ModelViewSet):
    queryset = Contact.objects.all()
    serializer_class = ContactSerializer
    permission_classes = [permissions.AllowAny]
    

    

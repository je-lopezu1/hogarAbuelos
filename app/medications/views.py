from django.shortcuts import render
from medications.logic import medication_logic as ml
from django.core import serializers
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
import json

# Create your views here.
def medications_view(request):
    if request.method == 'GET':
        medications = ml.get_all_medications()
        return render(request, 'list_medications.html', {'medications': medications})

@csrf_exempt
def create_medication_view(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        nombre = data.get('name')
        ml.create_medication({'name': nombre})
        return HttpResponse('Medication created', status=201)
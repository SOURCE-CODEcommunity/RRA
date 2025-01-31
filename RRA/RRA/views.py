from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
import json

from .animal_ethics_review import main

@csrf_exempt
@require_http_methods(["POST", "GET", "OPTIONS"])
#def rra_view(request):
    if request.method == 'POST':
        text = json.loads(request.body)['textContent']

        rpns = main(text)

        response = JsonResponse(data=rpns, safe=False)
        response['Access-Control-Allow-Origin'] = '*'

        return response
    
    elif request.method == 'OPTIONS':
        response = HttpResponse()
        response['Access-Control-Allow-Origin'] = '*'
        response['Access-Control-Allow-Methods'] = 'POST, OPTIONS'
        response['Access-Control-Allow-Headers'] = 'Content-Type'
        return response
    
    elif request.method == 'GET':
        return render(request=request, template_name='home.html')
    
    else:
        response = HttpResponse("Invalid request method", status=405)
        response['Access-Control-Allow-Origin'] = '*'
        return response

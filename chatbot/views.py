from django.shortcuts import render
import api_client
import requests

def home(request):

    request = ""
    #avail = api_client.avail_destination("MCO")

    return render(request, 'core/home.html', {})

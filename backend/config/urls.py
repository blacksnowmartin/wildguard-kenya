from django.http import JsonResponse
from django.urls import path
from accounts.urls import urlpatterns as account_urlpatterns


def health(request):
    return JsonResponse({'status': 'ok', 'service': 'wildguard-api'})


urlpatterns = [path('api/health/', health, name='health'), *account_urlpatterns]

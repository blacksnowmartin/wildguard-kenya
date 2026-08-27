from django.http import JsonResponse
from django.urls import path


def health(request):
    return JsonResponse({'status': 'ok', 'service': 'wildguard-api'})


urlpatterns = [path('api/health/', health, name='health')]

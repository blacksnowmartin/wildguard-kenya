from django.urls import path

from incidents.views import IncidentActionView, IncidentDetailView, IncidentListCreateView

urlpatterns = [
    path('api/incidents/', IncidentListCreateView.as_view(), name='incident-list-create'),
    path('api/incidents/<int:pk>/', IncidentDetailView.as_view(), name='incident-detail'),
    path('api/incidents/<int:pk>/action/', IncidentActionView.as_view(), name='incident-action'),
]

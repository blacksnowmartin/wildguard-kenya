from django.urls import path

from incidents.alert_views import AlertListView, NotificationListView, NotificationMarkReadView
from incidents.views import IncidentActionView, IncidentDetailView, IncidentListCreateView

urlpatterns = [
    path('api/incidents/', IncidentListCreateView.as_view(), name='incident-list-create'),
    path('api/incidents/<int:pk>/', IncidentDetailView.as_view(), name='incident-detail'),
    path('api/incidents/<int:pk>/action/', IncidentActionView.as_view(), name='incident-action'),
    path('api/alerts/', AlertListView.as_view(), name='alert-list'),
    path('api/notifications/', NotificationListView.as_view(), name='notification-list'),
    path('api/notifications/<int:pk>/read/', NotificationMarkReadView.as_view(), name='notification-mark-read'),
]

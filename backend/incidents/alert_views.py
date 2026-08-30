from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from incidents.models import Alert, Notification
from incidents.serializers import AlertSerializer


class AlertListView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        alerts = Alert.objects.select_related('incident', 'incident__species', 'incident__community').all()
        serializer = AlertSerializer(alerts, many=True)
        return Response(serializer.data)


class NotificationListView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        notifications = Notification.objects.filter(recipient=request.user).select_related('alert', 'alert__incident')
        return Response([
            {
                'id': item.id,
                'alert_id': item.alert_id,
                'title': item.alert.title,
                'message': item.alert.message,
                'read_at': item.read_at,
                'created_at': item.created_at,
            }
            for item in notifications
        ])


class NotificationMarkReadView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, pk):
        notification = Notification.objects.get(pk=pk, recipient=request.user)
        notification.read_at = notification.read_at or __import__('django.utils.timezone').utils.timezone.now()
        notification.save(update_fields=['read_at'])
        return Response({'status': 'read'}, status=status.HTTP_200_OK)

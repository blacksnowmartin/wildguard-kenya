from __future__ import annotations

from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from accounts.permissions import IsRangerOrSupervisor
from incidents.models import HWCIncident
from incidents.serializers import IncidentCreateSerializer, IncidentDetailSerializer, IncidentStatusUpdateSerializer
from incidents.services import calculate_hwc_risk, create_critical_alert, transition_incident_status


class IncidentListCreateView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        incidents = HWCIncident.objects.select_related('species', 'community', 'reporter').all()
        serializer = IncidentDetailSerializer(incidents, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = IncidentCreateSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        incident = serializer.save()
        risk = calculate_hwc_risk(
            species_danger_factor=incident.species.danger_factor,
            animal_count=incident.animal_count,
            settlement_within_2km=False,
            is_night=False,
            previous_nearby_incidents=0,
            property_damage=incident.property_damage,
        )
        incident.risk_score = risk['score']
        incident.risk_level = risk['risk_level']
        incident.save(update_fields=['risk_score', 'risk_level', 'updated_at'])

        if incident.risk_level == HWCIncident.Severity.CRITICAL:
            create_critical_alert(incident)

        return Response(IncidentDetailSerializer(incident).data, status=status.HTTP_201_CREATED)


class IncidentDetailView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, pk):
        incident = HWCIncident.objects.select_related('species', 'community', 'reporter').get(pk=pk)
        return Response(IncidentDetailSerializer(incident).data)

    def patch(self, request, pk):
        incident = HWCIncident.objects.get(pk=pk)
        serializer = IncidentStatusUpdateSerializer(incident, data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        incident = serializer.save()
        return Response(IncidentDetailSerializer(incident).data)


class IncidentActionView(APIView):
    permission_classes = (IsAuthenticated, IsRangerOrSupervisor)

    def post(self, request, pk):
        incident = HWCIncident.objects.get(pk=pk)
        action = request.data.get('action')
        target_map = {
            'review': HWCIncident.Status.UNDER_REVIEW,
            'verify': HWCIncident.Status.VERIFIED,
            'reject': HWCIncident.Status.REJECTED,
            'dispatch': HWCIncident.Status.DISPATCHED,
            'respond': HWCIncident.Status.RESPONDING,
            'resolve': HWCIncident.Status.RESOLVED,
            'close': HWCIncident.Status.CLOSED,
        }

        if action not in target_map:
            return Response({'detail': 'Unsupported action.'}, status=status.HTTP_400_BAD_REQUEST)

        target_status = target_map[action]
        try:
            transition_incident_status(incident, target_status, request.user, notes=f'Action: {action}')
        except ValueError as exc:
            return Response({'detail': str(exc)}, status=status.HTTP_400_BAD_REQUEST)

        if incident.risk_level == HWCIncident.Severity.CRITICAL and target_status in {HWCIncident.Status.VERIFIED, HWCIncident.Status.DISPATCHED, HWCIncident.Status.RESPONDING}:
            create_critical_alert(incident)

        return Response(IncidentDetailSerializer(incident).data)

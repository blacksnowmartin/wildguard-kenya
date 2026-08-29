from __future__ import annotations

from django.contrib.gis.db.models import PointField
from django.db import models
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from accounts.permissions import IsRangerOrSupervisor, IsSupervisorOrAdmin
from incidents.models import HWCIncident, IncidentStatusHistory
from incidents.serializers import IncidentCreateSerializer, IncidentDetailSerializer, IncidentStatusUpdateSerializer
from incidents.services import calculate_hwc_risk


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
        if action == 'verify':
            incident.verified = True
            incident.status = HWCIncident.Status.VERIFIED
        elif action == 'dispatch':
            incident.status = HWCIncident.Status.DISPATCHED
        elif action == 'resolve':
            incident.status = HWCIncident.Status.RESOLVED
        else:
            return Response({'detail': 'Unsupported action.'}, status=status.HTTP_400_BAD_REQUEST)

        incident.save(update_fields=['status', 'verified', 'updated_at'])
        IncidentStatusHistory.objects.create(
            incident=incident,
            actor=request.user,
            old_status='',
            new_status=incident.status,
            notes=f'Action: {action}',
        )
        return Response(IncidentDetailSerializer(incident).data)

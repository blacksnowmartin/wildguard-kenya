from __future__ import annotations

from django.contrib.gis.geos import Point
from rest_framework import serializers

from accounts.models import User
from communities.models import Community, WildlifeSpecies
from incidents.models import HWCIncident, IncidentStatusHistory


class WildlifeSpeciesSerializer(serializers.ModelSerializer):
    class Meta:
        model = WildlifeSpecies
        fields = ('id', 'name', 'danger_factor')


class CommunitySerializer(serializers.ModelSerializer):
    class Meta:
        model = Community
        fields = ('id', 'name', 'county')


class IncidentCreateSerializer(serializers.ModelSerializer):
    latitude = serializers.FloatField(write_only=True)
    longitude = serializers.FloatField(write_only=True)
    species = serializers.PrimaryKeyRelatedField(queryset=WildlifeSpecies.objects.all())
    community = serializers.PrimaryKeyRelatedField(queryset=Community.objects.all())

    class Meta:
        model = HWCIncident
        fields = (
            'species',
            'community',
            'animal_count',
            'severity',
            'description',
            'event_time',
            'latitude',
            'longitude',
            'property_damage',
        )

    def create(self, validated_data):
        latitude = validated_data.pop('latitude')
        longitude = validated_data.pop('longitude')
        request = self.context['request']
        incident = HWCIncident.objects.create(
            reporter=request.user,
            location=Point(longitude, latitude, srid=4326),
            **validated_data,
        )
        IncidentStatusHistory.objects.create(
            incident=incident,
            actor=request.user,
            old_status='',
            new_status=HWCIncident.Status.REPORTED,
        )
        return incident


class IncidentDetailSerializer(serializers.ModelSerializer):
    species = WildlifeSpeciesSerializer(read_only=True)
    community = CommunitySerializer(read_only=True)
    reporter = serializers.SerializerMethodField()

    class Meta:
        model = HWCIncident
        fields = (
            'id',
            'species',
            'community',
            'reporter',
            'description',
            'animal_count',
            'severity',
            'status',
            'event_time',
            'verified',
            'risk_score',
            'risk_level',
            'location',
            'created_at',
            'updated_at',
        )

    def get_reporter(self, obj):
        return {'id': obj.reporter_id, 'username': obj.reporter.username, 'role': obj.reporter.role}


class IncidentStatusUpdateSerializer(serializers.ModelSerializer):
    notes = serializers.CharField(required=False, allow_blank=True)

    class Meta:
        model = HWCIncident
        fields = ('status', 'notes')

    def update(self, instance, validated_data):
        notes = validated_data.pop('notes', '')
        user = self.context['request'].user
        instance.status = validated_data['status']
        instance.save(update_fields=['status', 'updated_at'])
        IncidentStatusHistory.objects.create(
            incident=instance,
            actor=user,
            old_status='',
            new_status=instance.status,
            notes=notes,
        )
        return instance

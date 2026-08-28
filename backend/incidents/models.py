from django.conf import settings
from django.contrib.gis.db import models
from django.core.validators import FileExtensionValidator

from communities.models import Community, WildlifeSpecies


class HWCIncident(models.Model):
    class Severity(models.TextChoices):
        LOW = 'LOW', 'Low'
        MODERATE = 'MODERATE', 'Moderate'
        HIGH = 'HIGH', 'High'
        CRITICAL = 'CRITICAL', 'Critical'

    class Status(models.TextChoices):
        REPORTED = 'REPORTED', 'Reported'
        UNDER_REVIEW = 'UNDER_REVIEW', 'Under review'
        VERIFIED = 'VERIFIED', 'Verified'
        REJECTED = 'REJECTED', 'Rejected'
        DISPATCHED = 'DISPATCHED', 'Dispatched'
        RESPONDING = 'RESPONDING', 'Responding'
        RESOLVED = 'RESOLVED', 'Resolved'
        CLOSED = 'CLOSED', 'Closed'

    species = models.ForeignKey(WildlifeSpecies, on_delete=models.PROTECT, related_name='incidents')
    reporter = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='reported_incidents')
    community = models.ForeignKey(Community, on_delete=models.PROTECT, related_name='incidents')
    location = models.PointField(geography=True)
    description = models.TextField()
    animal_count = models.PositiveSmallIntegerField(default=1)
    severity = models.CharField(max_length=12, choices=Severity.choices)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.REPORTED)
    event_time = models.DateTimeField()
    verified = models.BooleanField(default=False)
    risk_score = models.PositiveSmallIntegerField(default=0)
    risk_level = models.CharField(max_length=12, choices=Severity.choices, default=Severity.LOW)
    property_damage = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [models.Index(fields=['status', 'risk_level']), models.Index(fields=['-created_at'])]

    def __str__(self) -> str:
        return f'{self.species} incident {self.pk}'


class IncidentReporterDetails(models.Model):
    incident = models.OneToOneField(HWCIncident, on_delete=models.CASCADE, related_name='private_reporter_details')
    phone_number = models.CharField(max_length=32, blank=True)
    alternate_contact = models.CharField(max_length=160, blank=True)
    consent_to_contact = models.BooleanField(default=False)


class IncidentEvidence(models.Model):
    incident = models.ForeignKey(HWCIncident, on_delete=models.CASCADE, related_name='evidence')
    file = models.FileField(upload_to='incident-evidence/%Y/%m/', validators=[FileExtensionValidator(['jpg', 'jpeg', 'png', 'webp', 'mp4'])])
    caption = models.CharField(max_length=240, blank=True)
    uploaded_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    uploaded_at = models.DateTimeField(auto_now_add=True)


class IncidentStatusHistory(models.Model):
    incident = models.ForeignKey(HWCIncident, on_delete=models.CASCADE, related_name='status_history')
    actor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    old_status = models.CharField(max_length=20, choices=HWCIncident.Status.choices, blank=True)
    new_status = models.CharField(max_length=20, choices=HWCIncident.Status.choices)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']


class RiskAssessment(models.Model):
    incident = models.ForeignKey(HWCIncident, on_delete=models.CASCADE, related_name='risk_assessments')
    score = models.PositiveSmallIntegerField()
    level = models.CharField(max_length=12, choices=HWCIncident.Severity.choices)
    reasons = models.JSONField(default=list)
    rules_version = models.CharField(max_length=32, default='v1')
    created_at = models.DateTimeField(auto_now_add=True)


class Alert(models.Model):
    incident = models.ForeignKey(HWCIncident, on_delete=models.CASCADE, related_name='alerts')
    title = models.CharField(max_length=180)
    message = models.TextField()
    priority = models.CharField(max_length=12, choices=HWCIncident.Severity.choices, default=HWCIncident.Severity.CRITICAL)
    acknowledged_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [models.UniqueConstraint(fields=['incident', 'priority'], name='unique_incident_alert_priority')]


class Notification(models.Model):
    recipient = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='notifications')
    alert = models.ForeignKey(Alert, on_delete=models.CASCADE, related_name='notifications')
    read_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

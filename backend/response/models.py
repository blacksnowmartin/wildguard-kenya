from django.conf import settings
from django.db import models

from incidents.models import HWCIncident


class RangerResponse(models.Model):
    incident = models.OneToOneField(HWCIncident, on_delete=models.CASCADE, related_name='ranger_response')
    ranger = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='ranger_responses')
    accepted_at = models.DateTimeField(null=True, blank=True)
    dispatched_at = models.DateTimeField(null=True, blank=True)
    responding_at = models.DateTimeField(null=True, blank=True)
    resolved_at = models.DateTimeField(null=True, blank=True)
    resolution_notes = models.TextField(blank=True)
    outcome = models.CharField(max_length=160, blank=True)

    def __str__(self) -> str:
        return f'Response for incident {self.incident_id}'

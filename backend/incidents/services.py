from __future__ import annotations

from typing import Any

from incidents.models import Alert, HWCIncident

ALLOWED_STATUS_TRANSITIONS = {
    HWCIncident.Status.REPORTED: {HWCIncident.Status.UNDER_REVIEW},
    HWCIncident.Status.UNDER_REVIEW: {HWCIncident.Status.VERIFIED, HWCIncident.Status.REJECTED},
    HWCIncident.Status.VERIFIED: {HWCIncident.Status.DISPATCHED},
    HWCIncident.Status.DISPATCHED: {HWCIncident.Status.RESPONDING},
    HWCIncident.Status.RESPONDING: {HWCIncident.Status.RESOLVED},
    HWCIncident.Status.RESOLVED: {HWCIncident.Status.CLOSED},
}


def validate_status_transition(current_status: str, next_status: str) -> bool:
    return next_status in ALLOWED_STATUS_TRANSITIONS.get(current_status, set())


def transition_incident_status(incident, next_status: str, actor, notes: str = '') -> HWCIncident:
    current_status = incident.status
    if not validate_status_transition(current_status, next_status):
        raise ValueError(f'Invalid transition from {current_status} to {next_status}.')

    incident.status = next_status
    incident.save(update_fields=['status', 'updated_at'])

    if hasattr(incident, 'status_history'):
        incident.status_history.create(
            actor=actor,
            old_status=current_status,
            new_status=next_status,
            notes=notes,
        )

    return incident


def create_critical_alert(incident) -> Alert | None:
    if incident.risk_level != HWCIncident.Severity.CRITICAL:
        return None

    alert, created = Alert.objects.get_or_create(
        incident=incident,
        priority=HWCIncident.Severity.CRITICAL,
        defaults={
            'title': 'CRITICAL HWC INCIDENT',
            'message': (
                f'{incident.species.name} incident at {incident.community.name} '
                f'has reached a critical risk score of {incident.risk_score}/100.'
            ),
        },
    )
    return alert if created or alert else None


def calculate_hwc_risk(
    *,
    species_danger_factor: int,
    animal_count: int = 1,
    settlement_within_2km: bool = False,
    is_night: bool = False,
    previous_nearby_incidents: int = 0,
    property_damage: bool = False,
) -> dict[str, Any]:
    reasons: list[str] = []
    score = int(species_danger_factor)

    if species_danger_factor:
        reasons.append(f'Species danger factor +{species_danger_factor}')

    if settlement_within_2km:
        score += 25
        reasons.append('Settlement within 2 km +25')

    if is_night:
        score += 10
        reasons.append('Night-time event +10')

    if animal_count > 1:
        score += 10
        reasons.append('Multiple animals +10')

    if previous_nearby_incidents > 0:
        score += 15
        reasons.append('Previous nearby incidents +15')

    if property_damage:
        score += 15
        reasons.append('Crop or property damage +15')

    score = min(score, 100)

    if score <= 25:
        risk_level = 'LOW'
    elif score <= 50:
        risk_level = 'MODERATE'
    elif score <= 75:
        risk_level = 'HIGH'
    else:
        risk_level = 'CRITICAL'

    return {
        'score': score,
        'risk_level': risk_level,
        'reasons': reasons,
    }

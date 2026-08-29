from __future__ import annotations

from typing import Any


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

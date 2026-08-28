from django.contrib.gis.db import models


class Community(models.Model):
    name = models.CharField(max_length=160)
    county = models.CharField(max_length=120)
    center = models.PointField(geography=True, null=True, blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['county', 'name']
        constraints = [models.UniqueConstraint(fields=['county', 'name'], name='unique_community_per_county')]

    def __str__(self) -> str:
        return f'{self.name}, {self.county}'


class WildlifeSpecies(models.Model):
    name = models.CharField(max_length=120, unique=True)
    danger_factor = models.PositiveSmallIntegerField(default=10)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['name']
        verbose_name_plural = 'wildlife species'

    def __str__(self) -> str:
        return self.name

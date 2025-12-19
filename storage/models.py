from django.db import models
import uuid

class Location(models.Model):
    # Explicit UUID Primary Key
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, unique=True)
    
    def __str__(self):
        return self.name

class SubLocation(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    location = models.ForeignKey(Location, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('location', 'name') 

    def __str__(self):
        return f"{self.location.name} - {self.name}"

class Area(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    sub_location = models.ForeignKey(SubLocation, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('sub_location', 'name')

    def __str__(self):
        return f"{self.sub_location.name} - {self.name}"

class SubArea(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    area = models.ForeignKey(Area, on_delete=models.PROTECT)

    def get_full_location_display(self):
        ar = self.area
        sl = ar.sub_location
        loc = sl.location
        return f"{loc.name} > {sl.name} > {ar.name} > {self.name}"
    
    get_full_location_display.short_description = 'Full Location Path'

    class Meta:
        unique_together = ('area', 'name')

    def __str__(self):
        return f"{self.area.name} - {self.name}"
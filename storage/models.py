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

    class Meta:
        unique_together = ('area', 'name')

    def __str__(self):
        return f"{self.area.name} - {self.name}"

class Storage(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    sub_area = models.ForeignKey(SubArea, on_delete=models.PROTECT)
    item_description = models.CharField(max_length=250)
    
    def get_full_location_display(self):
        sa = self.sub_area
        ar = sa.area
        sl = ar.sub_location
        loc = sl.location
        return f"{loc.name} > {sl.name} > {ar.name} > {sa.name}"
    get_full_location_display.short_description = 'Full Location Path'
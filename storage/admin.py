from django.contrib import admin
from .models import Location, SubLocation, Area, SubArea

class LocationAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'name',
    )
    list_filter = () 
    search_fields = ('name',)

admin.site.register(Location, LocationAdmin)

class SubLocationAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'name',
        'location',
    )
    list_filter = ('location',) 
    search_fields = ('name', 'location__name')

admin.site.register(SubLocation, SubLocationAdmin)

class AreaAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'name',
        'sub_location',
    )
    list_filter = ('sub_location',)
    search_fields = ('name', 'sub_location__name')

admin.site.register(Area, AreaAdmin)

class SubAreaAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'name',
        'area',
    )
    list_filter = ('area',)
    search_fields = ('name', 'area__name')

admin.site.register(SubArea, SubAreaAdmin)
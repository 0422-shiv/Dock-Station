from django.contrib import admin
from .models import DockStation
from django.contrib.auth.models import Group

admin.site.unregister(Group)
# admin.site.register(Bicycle)


@admin.register(DockStation)
class DockStationAdmin(admin.ModelAdmin):
    list_display = ('name', 'address','postcode','landmark','image','total_docks','bikes_availible','dropoff_docks','latitude', 'longitude',)
    search_fields = ('postcode',)

    fieldsets = (
        (None, {
            'fields': ( 'name', 'address','postcode','landmark','image','total_docks','bikes_availible','dropoff_docks','latitude', 'longitude',)
        }),
    )


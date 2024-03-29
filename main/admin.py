from django.contrib import admin
from .models import DockStation,BicycleData,Booking
from django.contrib.auth.models import Group

admin.site.unregister(Group)
admin.site.register(BicycleData)
admin.site.register(Booking)


@admin.register(DockStation)
class DockStationAdmin(admin.ModelAdmin):
    list_display = ('name', 'address','postcode','landmark','latitude', 'longitude','image',)
    search_fields = ('postcode',)

    fieldsets = (
        (None, {
            'fields': ( 'name', 'address','postcode','landmark','image','bicycle','latitude', 'longitude',)
        }),
    )


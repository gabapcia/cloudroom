from django.contrib import admin
from .models import Board


class MicrocontrollersAdmin(admin.ModelAdmin):
    fields = [
        'name',
        'status',
        'allowed',
    ]


admin.site.register(Board, MicrocontrollersAdmin)

from django.contrib import admin
from boards.models import boards


class boardsAdmin(admin.ModelAdmin):
    fields = [
        'name',
        'status',
        'allowed',
    ]


admin.site.register(boards, boardsAdmin)

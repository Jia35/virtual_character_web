from django.contrib import admin

from .models import Media, Character, Update


class MediaAdmin(admin.ModelAdmin):
    list_display = ('name', 'country')


class CharacterAdmin(admin.ModelAdmin):
    list_display = ('name', 'birthday_date', 'gender')


class UpdateAdmin(admin.ModelAdmin):
    list_display = ('type', 'date')


admin.site.register(Media, MediaAdmin)
admin.site.register(Character, CharacterAdmin)
admin.site.register(Update, UpdateAdmin)

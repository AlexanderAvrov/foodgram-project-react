from django.contrib import admin

from .models import User


class UserAdmin(admin.ModelAdmin):
    """Настройки админ панели для модели Пользователей"""

    list_display = ('id', 'first_name', 'last_name', 'email')
    search_fields = ('first_name', 'last_name')
    list_filter = ('first_name', 'email')


admin.site.register(User, UserAdmin)

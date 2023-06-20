from django.contrib import admin

from nail_service.models import Customer, Master, Services, User, Events

admin.site.register(User)
admin.site.register(Customer)
admin.site.register(Master)
admin.site.register(Services)
admin.site.register(Events)

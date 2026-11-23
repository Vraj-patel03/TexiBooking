
from django.contrib import admin
from .models import AdminAccount, Customer, Driver


admin.site.register(AdminAccount)
admin.site.register(Customer)
admin.site.register(Driver)

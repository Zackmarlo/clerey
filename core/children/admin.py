from django.contrib import admin
from .models import ChildProfile, DoctorChildAccess

admin.site.register(ChildProfile)
admin.site.register(DoctorChildAccess)
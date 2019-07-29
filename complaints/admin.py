from django.contrib import admin
from complaints.models import Complaint, Department

# Register your models here.
admin.site.register(Complaint)
admin.site.register(Department)
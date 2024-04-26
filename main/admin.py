from django.contrib import admin
from .models import *

admin.site.register(Admin)
admin.site.register(Moderator)
admin.site.register(Teacher)
admin.site.register(Student)


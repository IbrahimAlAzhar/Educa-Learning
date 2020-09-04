from django.contrib import admin
from .models import Subject, Course, Module


@admin.register(Subject) # to register models in the admin site
class SubjectAdmin(admin.ModelAdmin): # this class for 'subject' model
    list_display = ['title','slug'] # display these list
    prepopulated_fields = {'slug':('title',)} # when we write 'title' its automatically create slug


class ModuleInline(admin.StackedInline):
    model = Module  # using stacked inline,using in CourseAdmin class and


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin): # this class using for 'course' model
    list_display = ['title','subject','created']  # here display these from course model on admin file
    list_filter = ['created','subject']
    search_fields = ['title','overview'] # we can use for searching
    prepopulated_fields = {'slug': ('title',)} # slug is creating when title creates
    inlines = [ModuleInline] # there are a module inside the course,for that reason we add using inline,use 'module' inline in 'Courses' model in admin site

from django.db import models
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey


# subject -> Course ->Module -> Content
# there are many 'subject',inside the subject there are many 'course' and inside the course there are many 'content'
class Subject(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200,unique=True)

    class Meta:
        ordering = ['title']

    def __str__(self):
        return self.title


class Course(models.Model):
    owner = models.ForeignKey(User,related_name='courses_created',on_delete=models.CASCADE) # the instructor that created this course
    subject = models.ForeignKey(Subject,related_name='courses',on_delete=models.CASCADE) # the subject that this course belongs to,a fk field that points to the subject model
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200,unique=True)
    overview = models.TextField() # textfield column to include an overview of the course
    created = models.DateTimeField(auto_now_add=True) # automatically set because of 'auto_now_add=True'

    class Meta:
        ordering = ['-created'] # the newer post show first

    def __str__(self):
        return self.title


class Module(models.Model): # Each course is divided into several modules,
    course = models.ForeignKey(Course,related_name='modules',on_delete=models.CASCADE) # the 'module' model contains a fk field that points to the 'course' model
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.title


class Content(models.Model): # this is the content model
    module = models.ForeignKey(Module,related_name='contents',on_delete=models.CASCADE) # a module contains multiple contents,so we define a fk field to the 'Module' model
    content_type = models.ForeignKey(ContentType,on_delete=models.CASCADE,limit_choices_to={'model__in':('text',   # ContentType is django build in,a fk field to the 'contentType' model(which type it is:image/video etc),
                                                                                                         'video',
                                                                                                         'image',
                                                                                                         'file')}) # we add a 'limit_choices_to' argument to limit the Content type,'model__in' field lookup to filter the query to the ContentType objects with a model attribute that is 'text','video','image' or 'file',which are model(inherit from abstract)
    object_id = models.PositiveIntegerField() # to store pk of the related object
    item = GenericForeignKey('content_type','object_id') # there using a field(django build) to related object by combining the two previous fields
# content_type and object_id fields have corresponding column in the db table of this model,the 'item' field allows you to retrive or set the related obj directly
# we are going to use a different model for each type of content


# the Content(ItemBase) model of our courses application contains a generic relation to associate different types of content to it.We are going to create an abstract model that provides the common fileds for all content models
# the abstract model(ItemBase) are not save into the database,only child's attribute(inherit from abstract model) are save into db
class ItemBase(models.Model): # these common fields(owner,title,created,updated) will be used for all types of content
    owner = models.ForeignKey(User,related_name='%(class)s_related',on_delete=models.CASCADE) # the owner field allows us to store which user create the content.Since the field is defined an abstract class we need different 'related_name' for each sub model,django handles it using placeholder %(class)s,reverse relation is 'text_related','file_related'
    title = models.CharField(max_length=250)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True # this model is abstract model

    def __str__(self):
        return self.title


class Text(ItemBase): # we have 4 different content models,which inherit from the 'ItemBase' abstract model,
    content = models.TextField() # to store text content


class File(ItemBase):
    file = models.FileField(upload_to='files') # to store files such as PDF


class Image(ItemBase): # to store image files
    file = models.FileField(upload_to='images')


class Video(ItemBase): # to store videos,we use an urlfield to provide a video url in order to embed it
    url = models.URLField()


'''
# abstract model(abstract model will not create a db table for it,child model of abstract model creates db table
from django.db import models
class BaseContent(model.Model):
      title = models.CharField(max_length=100)
      created = models.DateTimeField(auto_now_add=True)
      
      class Meta:
            abstract = True # define this class is abstract class(don't create table in database),
class Text(BaseContent):
       body = models.TextField() # here create a child of Abs class
# in this case,django would create a table for the Text model only,including the title,created and body fields   

# mulit table model inheritance,django will create a database table for both original model and sub model

class BaseContent(models.Model):
    title = models.CharField(max_length=100)
    created = models.DateTimeField(auto_now_add=True)
class Text(BaseContent):
    body = models.TextField()
# django would include an automatically generated oneToOneField in the Text model and create a db table for each model

# proxy model,it is used to change the behavior of a model,for example by including additional methods or different meta options.both models operate on the database table of the original model
from django.db import models
from django.utils import timezone

class BaseContent(models.Model):
    title = models.CharField(max_length=100)
    created = models.DateTimeField(auto_now_add=True)
class OrderedContent(BaseContent): # we define an OrderedContent model that is a proxy model for the 'Content' model
    class Meta:
        proxy = True
        ordering = ['created']
    def created_delta(self): 
        return timezone.now() - self.created
# both models,'Content' and 'OrderedContent' operate on the same db table
'''
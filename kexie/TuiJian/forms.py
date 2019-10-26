from django.forms import ModelForm
from .models import *

class KXForm(ModelForm):
    class Meta:
        model=KX
        fields = ['title','url','img','content','time','source']

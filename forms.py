from django import forms
from django.forms import ModelForm
from django.contrib.auth.models import User
from .models import Contents
import datetime

DATE_INPUT_FORMATS = ['%Y%m%d%H%M%S%f']

class UserForm(ModelForm):
    class Meta:
        model = User
        fields = ['username', 'password', 'email']


class LoginForm(ModelForm):
    class Meta:
        model = User
        fields = ['username', 'password']


class ContentsForm(ModelForm):
    contents      = forms.CharField(widget=forms.Textarea(attrs={'v-model': 'firewood_id', '@keydown.enter': 'insert_content'}))
    mention_index = forms.CharField(widget=forms.HiddenInput, initial='0')
    mention_order = forms.CharField(widget=forms.HiddenInput, initial='0')
    image         = forms.FileField(widget=forms.FileInput(attrs={'accept': '.jpg, .jpeg, .png', '@change': 'onChangeImg'})\
                    , initial='', required=False)

    class Meta:
        model = Contents
        fields = ['contents', 'mention_index', 'mention_order', 'image']

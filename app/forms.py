from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.forms.widgets import PasswordInput, TextInput

from .models import Schema, SchemaColumn


class CustomAuthForm(AuthenticationForm):
    username = forms.CharField(widget=TextInput(attrs={'class': 'validate', 'placeholder': 'Username'}))
    password = forms.CharField(widget=PasswordInput(attrs={'placeholder': 'Password'}))


class SchemaForm(forms.ModelForm):
    class Meta:
        model = Schema
        fields = ["schema_name", "schema_column_separator", "schema_string_character",]
        widgets = {
            'schema_name': forms.TextInput(),
        }


class SchemaColumnForm(forms.ModelForm):
    class Meta:
        model = SchemaColumn
        fields = ("column_name","column_type","column_order")
        widgets = {
            'column_name': forms.TextInput( attrs={"class":"content__add-form-name"}),
            'column_type': forms.Select(attrs={"class":"content__add-form-type"}),
            'column_order': forms.NumberInput(attrs={"class":"content__add-form-order"})
        }

from django.urls import re_path,path
from django.contrib.auth.views import LoginView

from .forms import CustomAuthForm
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    re_path(r"^login/$", LoginView.as_view(template_name="login.html",authentication_form=CustomAuthForm,
                                           next_page="index"), name="login"),
    re_path(r"^check_dataset/(?P<schema_id>\d+)", views.dataset_checker, name="check_dataset"),
    re_path(r"^(?P<id>\d+)/dataset/$", views.dataset, name="dataset"),
    re_path(r"^add/",views.create_schema,name="add")
]
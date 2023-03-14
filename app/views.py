from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout

from .models import Schema


# Create your views here.


@login_required(login_url="/login/")
def index(request):
    if request.method == "POST":
        user = request.POST.get("user", None)
        if user:
            if int(user) == request.user.id:
                logout(request)

                return redirect("login")

    schemas = Schema.get_by_user_id(request.user.id)

    print(schemas)

    context = {
        "schemas": schemas,
    }

    return render(request, "index.html", context)

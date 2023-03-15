import json

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.views.decorators.csrf import csrf_exempt

from .models import Schema, SchemaColumn, TypeOfData, DataSet
from .forms import SchemaForm,SchemaColumnForm


# Create your views here.
def is_ajax(request):
    return request.headers.get('X-Requested-With') == 'XMLHttpRequest'

@login_required(login_url="/login/")
def index(request):
    if request.method == "POST":
        user = request.POST.get("user", None)
        if user:
            if int(user) == request.user.id:
                logout(request)

                return redirect("login")

    schemas = Schema.get_by_user_id(request.user.id)


    context = {
        "schemas": schemas,
    }

    return render(request, "index.html", context)

@login_required(login_url="/login/")
def dataset_checker(request,schema_id):
    dataset = DataSet.get_by_schema_id(schema_id)

    if not dataset:
        schema = Schema.get_by_id(schema_id)
        dataset = DataSet.create(schema)

    return redirect("dataset", id=dataset.dataset_id)

@login_required(login_url="/login/")
def dataset(request,id):

    dataset = DataSet.get_by_id(id)

    columns = dataset.dataset_schema.schema_columns.all()
    csv_datasets = dataset.dataset_csv.all()

    context = {
        "dataset": dataset,
        "columns": columns,
        "csv_datasets": csv_datasets,
    }

    return render(request,"dataset.html",context)


@login_required(login_url="/login/")
@csrf_exempt
def create_schema(request):
    schema_id = request.session.get("schema_id",None)
    if schema_id:
        schema = Schema.get_by_id(schema_id)
    else:
        schema = Schema.create(request.user, "New schema", 0, 0)
        request.session["schema_id"] = schema.schema_id

    columns = []

    if request.method == "POST":
        if is_ajax(request):
            body_unicode = request.body.decode('utf-8')
            received_json = json.loads(body_unicode)

            try:
                for key, value in received_json.items():
                    if key != 'specific' and not value:
                        raise Exception("Wrong data")

                if received_json["type"] in ["4","5"] and not received_json["specific"]:
                    raise Exception
            except:
                pass
            else:
                type_of_data = TypeOfData.get_by_id(int(received_json["type"]))

                column = SchemaColumn.create(received_json["name"], type_of_data,
                                             received_json["specific"], int(received_json["order"]))

                try:
                    schema.add_column(column)
                except:
                    SchemaColumn.delete_by_id(column.column_id)

            schema_form = SchemaForm(instance=schema)

        else:
            schema_form = SchemaForm(request.POST)

            if schema_form.is_valid():
                data = schema_form.cleaned_data
                schema.update(data["schema_name"],data["schema_column_separator"],data["schema_string_character"])

                request.session.pop("schema_id")

                return redirect("index")
            else:

                column_id = request.POST.get("id")

                del_column = SchemaColumn.get_by_id(column_id)

                current_schema = del_column.schema_columns.first()

                if request.user.id == current_schema.schema_user.id:
                    SchemaColumn.delete_by_id(column_id)
    else:
        schema_form = SchemaForm()

    for column in schema.schema_columns.all():
        columns.append({
            "column_id": column.column_id,
            "column_name":column.column_name,
            "column_type":column.column_type.type_name,
            "column_specific": column.column_specific,
            "column_order": column.column_order,
        })

    empty_column_form = SchemaColumnForm()

    context = {
        "schema_form": schema_form,
        "empty_column_form": empty_column_form,
        "columns" : columns,
    }

    return render(request,"add.html", context)
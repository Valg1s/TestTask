import json
import csv
from io import StringIO
from re import findall

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.views.decorators.csrf import csrf_exempt
from django.template.loader import render_to_string
from django.http import JsonResponse
from django.core.files.base import File
from faker import Faker


from .models import Schema, SchemaColumn, TypeOfData,CSVDataSet, DataSet
from .forms import SchemaForm, SchemaColumnForm

fake = Faker()


def create_number(min_num, max_num):
    def create():
        return fake.pyint(min_value=min_num, max_value=max_num)

    return create


def create_phone_number(country_cod):
    def create():
        return f"{country_cod}{fake.msisdn()[3:]}"

    return create


def is_ajax(request):
    return request.headers.get('Content-Type') == 'application/json'


@login_required(login_url="/login/")
def index(request):
    if request.method == "POST":
        user = request.POST.get("user", None)
        schema_id = request.POST.get("id")

        if user:
            if int(user) == request.user.id:
                logout(request)

                return redirect("login")

        elif schema_id:
            del_schema = Schema.get_by_id(schema_id)

            if request.user.id == del_schema.schema_user.id:
                Schema.delete_by_id(schema_id)

    schemas = Schema.get_by_user_id(request.user.id)

    context = {
        "schemas": schemas,
    }

    return render(request, "index.html", context)


@login_required(login_url="/login/")
def dataset_checker(request, schema_id):
    dataset = DataSet.get_by_schema_id(schema_id)

    if not dataset:
        schema = Schema.get_by_id(schema_id)
        dataset = DataSet.create(schema)

    return redirect("dataset", id=dataset.dataset_id)


@login_required(login_url="/login/")
@csrf_exempt
def dataset(request, id):
    dataset = DataSet.get_by_id(id)

    if request.method == "POST":
        if is_ajax(request):
            delimiter = dataset.dataset_schema.schema_column_separator

            if delimiter == 0:
                delimiter = ","
            elif delimiter == 1:
                delimiter = ";"
            elif delimiter == 2:
                delimiter = "    "
            elif delimiter == 3:
                delimiter = " "
            elif delimiter == 4:
                delimiter = "|"

            quotechar = dataset.dataset_schema.schema_string_character

            if quotechar == 0:
                quotechar = '"'
            elif quotechar == 1:
                quotechar = "'"

            body_unicode = request.body.decode('utf-8')
            received_json = json.loads(body_unicode)

            rows = received_json["rows"]

            if rows:
                csv_dataset = CSVDataSet.create()

                rows = int(rows)
                data = []

                for cl in dataset.dataset_schema.schema_columns.all():
                    if cl.column_type.type_name == "FullName":
                        column_func = fake.name
                    elif cl.column_type.type_name == "Job":
                        column_func = fake.company
                    elif cl.column_type.type_name == "Email":
                        column_func = fake.email
                    elif cl.column_type.type_name == "Phone number":
                        country_code = cl.column_specific
                        column_func = create_phone_number(country_code)
                    else:
                        range_ = findall(r"\d+", cl.column_specific)
                        column_func = create_number(int(range_[0]), int(range_[1]))

                    row_data = [cl.column_name]

                    for i in range(0, rows):
                        row_data.append(column_func())

                    data.append(row_data)

                file_name = f"{dataset.dataset_schema.schema_name}_{len(dataset.dataset_csv.all())+1}"

                csv_file = StringIO()
                writer = csv.writer(csv_file, delimiter=delimiter, quotechar=quotechar, lineterminator='\n')
                writer.writerows(zip(*data))

                csv_dataset.csv_dataset_file.save(f"{file_name}.csv",File(csv_file))
                csv_dataset.change_status()

                dataset.add_csv(csv_dataset)

                download_link = csv_dataset.csv_dataset_file.url
                print(download_link)

                return JsonResponse({"download_link": download_link})

    columns = dataset.dataset_schema.schema_columns.all()
    csv_datasets = dataset.dataset_csv.all()

    context = {
        "dataset": dataset,
        "columns": columns,
        "csv_datasets": csv_datasets,
    }

    return render(request, "dataset.html", context)


@login_required(login_url="/login/")
@csrf_exempt
def create_schema(request,id = None):
    if id:
        schema = Schema.get_by_id(id)
    else:
        schema_id = request.session.get("schema_id", None)
        schema = None

        if schema_id:
            schema = Schema.get_by_id(schema_id)

        if not schema_id or not schema:
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

                if received_json["type"] in ["4", "5"] and not received_json["specific"]:
                    raise Exception
            except:
                pass
            else:
                type_of_data = TypeOfData.get_by_id(int(received_json["type"]))

                column = SchemaColumn.create(received_json["name"], type_of_data,
                                             received_json["specific"], int(received_json["order"]))

                try:
                    schema.add_column(column)
                except Exception:
                    SchemaColumn.delete_by_id(column.column_id)

                if column:
                    context = {
                        "column": column,
                    }

                    html = render_to_string("add_table.html", context)

                    return JsonResponse({"html": html})

        else:
            schema_form = SchemaForm(request.POST)

            if schema_form.is_valid():
                data = schema_form.cleaned_data
                schema.update(data["schema_name"], data["schema_column_separator"], data["schema_string_character"])

                request.session.pop("schema_id")

                return redirect("index")
            else:

                column_id = request.POST.get("id")

                del_column = SchemaColumn.get_by_id(column_id)

                current_schema = del_column.schema_columns.first()

                if request.user.id == current_schema.schema_user.id:
                    SchemaColumn.delete_by_id(column_id)

    schema_form = SchemaForm(instance=schema)

    for column in schema.schema_columns.all():
        columns.append({
            "column_id": column.column_id,
            "column_name": column.column_name,
            "column_type": column.column_type.type_name,
            "column_specific": column.column_specific,
            "column_order": column.column_order,
        })

    empty_column_form = SchemaColumnForm()

    context = {
        "schema_form": schema_form,
        "empty_column_form": empty_column_form,
        "columns": columns,
    }

    return render(request, "add.html", context)

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

from .models import Schema, SchemaColumn, TypeOfData, CSVDataSet, DataSet
from .forms import SchemaForm, SchemaColumnForm

fake = Faker()

# Dict with function for type of data without specific
COLUMN_FUNCTION = {
    "FullName": fake.name,
    "Job": fake.company,
    "Email": fake.email,
}


def create_number(min_num, max_num):
    # Func for creating fake numbers in range
    def create():
        return fake.pyint(min_value=min_num, max_value=max_num)

    return create


def create_phone_number(country_cod):
    # Func for creating fake numbers with country code
    def create():
        return f"{country_cod}{fake.msisdn()[3:]}"

    return create


def is_ajax(request):
    # Func for checking request ajax or no
    return request.headers.get('Content-Type') == 'application/json'


@login_required(login_url="/login/")
def index(request):
    # Main paige
    if request.method == "POST":
        user_id = request.POST.get("user", None)
        schema_id = request.POST.get("id")

        if user_id:
            # For logout ,using post request
            if int(user_id) == request.user.id:
                logout(request)

                return redirect("login")

        elif schema_id:
            # Delete schemas ,using post request
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
    # Function - checker, if dataset are created , redirect on it ,if not create and redirect
    current_dataset = DataSet.get_by_schema_id(schema_id)

    if not current_dataset:
        schema = Schema.get_by_id(schema_id)
        current_dataset = DataSet.create(schema)

    return redirect("dataset", dataset_id=current_dataset.dataset_id)


@login_required(login_url="/login/")
@csrf_exempt
def dataset(request, dataset_id):
    # Dataset paige
    current_dataset = DataSet.get_by_id(dataset_id)

    if request.method == "POST":
        if is_ajax(request):
            body_unicode = request.body.decode('utf-8')
            received_json = json.loads(body_unicode)

            rows = received_json["rows"]

            if rows:
                csv_dataset = CSVDataSet.create()

                rows = int(rows)
                data = []

                for cl in current_dataset.dataset_schema.schema_columns.all():
                    # Loop for all columns in schema
                    if cl.column_type.type_name == "Phone number":
                        country_code = cl.column_specific
                        column_func = create_phone_number(country_code)
                    elif cl.column_type.type_name == "Integer":
                        range_ = findall(r"\d+", cl.column_specific)
                        column_func = create_number(int(range_[0]), int(range_[1]))
                    else:
                        column_func = COLUMN_FUNCTION[cl.column_type.type_name]

                    # First element of list - name of column
                    row_data = [cl.column_name]

                    for i in range(0, rows):
                        row_data.append(column_func())

                    data.append(row_data)

                file_name = f"{current_dataset.dataset_schema.schema_name}_{len(current_dataset.dataset_csv.all()) + 1}"

                csv_file = StringIO()

                # Take delimiter and quotechar from DB
                delimiter = current_dataset.dataset_schema.get_delimiter()
                quotechar = current_dataset.dataset_schema.get_character()

                writer = csv.writer(csv_file, delimiter=delimiter,
                                    quotechar=quotechar, lineterminator='\n')
                writer.writerows(zip(*data))

                csv_dataset.csv_dataset_file.save(f"{file_name}.csv", File(csv_file))
                csv_dataset.change_status()

                current_dataset.add_csv(csv_dataset)

                download_link = csv_dataset.csv_dataset_file.url

                return JsonResponse({"download_link": download_link})

    columns = current_dataset.dataset_schema.schema_columns.all()
    csv_datasets = current_dataset.dataset_csv.all()

    context = {
        "dataset": current_dataset,
        "columns": columns,
        "csv_datasets": csv_datasets,
    }

    return render(request, "dataset.html", context)


@login_required(login_url="/login/")
@csrf_exempt
def create_schema(request, schema_id=None):
    # Add and edit paiges
    schema_id = schema_id or request.session.get("schema_id")
    schema = Schema.get_by_id(schema_id)

    if not schema:
        schema = Schema.create(request.user, "New schema", 0, 0)
        request.session["schema_id"] = schema.schema_id

    if request.method == "POST":
        if is_ajax(request):
            body_unicode = request.body.decode('utf-8')
            received_json = json.loads(body_unicode)

            try:
                # Data validation
                for key, value in received_json.items():
                    if key != 'specific' and not value:
                        raise ValueError("Wrong data")

                if received_json["type"] in ["4", "5"] and not received_json["specific"]:
                    raise ValueError("Missing value for 'specific'")
            except ValueError:
                pass
            else:
                type_of_data = TypeOfData.get_by_id(int(received_json["type"]))

                column = SchemaColumn.create(received_json["name"],
                                             type_of_data,
                                             received_json["specific"],
                                             int(received_json["order"]))
                try:
                    # If order number is already reserved, would ValueError
                    schema.add_column(column)
                except ValueError:
                    SchemaColumn.delete_by_id(column.column_id)
                else:
                    context = {
                        "column": column,
                    }

                    # In "add_table.html" html code for one row of table
                    html = render_to_string("add_table.html", context)

                    return JsonResponse({"html": html})

        else:
            schema_form = SchemaForm(request.POST)

            if schema_form.is_valid():
                # if form is valid - it`s form for creating new schema
                data = schema_form.cleaned_data
                schema.update(data["schema_name"],
                              data["schema_column_separator"],
                              data["schema_string_character"])

                if request.session.get("schema_id"):
                    request.session.pop("schema_id")

                return redirect("index")
            else:
                # if form isn`t valid - it`s request for delete one column
                column_id = request.POST.get("id")

                del_column = SchemaColumn.get_by_id(column_id)

                current_schema = del_column.schema_columns.first()

                if request.user.id == current_schema.schema_user.id:
                    SchemaColumn.delete_by_id(column_id)

    schema_form = SchemaForm(instance=schema)

    empty_column_form = SchemaColumnForm()

    for cl in schema.schema_columns.all():
        print(cl.to_dict())
        print(cl.column_type in [4,5])

    context = {
        "schema_form": schema_form,
        "empty_column_form": empty_column_form,
        "columns": schema.schema_columns.all(),
    }

    return render(request, "add.html", context)

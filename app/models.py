from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

# Create your models here.
SPECIFICATOR = (
    (0, "Range(For INT)"),
    (1, "Country code(For PhoneNumber)"),
)

SEPARATOR = (
    (0, "Comma(,)"),
    (1, "Semicolon(;)"),
    (2, "Tab(    )"),
    (3, "Space( )"),
    (4, "Pipe(|)"),
)

STRING_CHARACTER = (
    (0, "Double-quote (“)"),
    (1, "One-quote (')"),
)

STATUS = (
    (0, "Progressing"),
    (1, "Ready"),
)


class TypeOfData(models.Model):
    type_id = models.AutoField(primary_key=True)
    type_name = models.TextField(max_length=64, verbose_name="Type", unique=True)
    type_specific = models.IntegerField(choices=SPECIFICATOR, default=None, null=True, blank=True)

    def __str__(self):
        return f"{self.type_name}"

    def __repr__(self):
        return f"{self.__class__.__name__}({self.type_id})"

    @staticmethod
    def get_by_id(id):
        type_of_data = TypeOfData.objects.filter(type_id=id).first()

        if type_of_data:
            return type_of_data

    @staticmethod
    def get_by_name(name):
        type_of_data = TypeOfData.objects.filter(type_name=name).first()

        if type_of_data:
            return type_of_data

        raise Exception("Type didn't find")

    @staticmethod
    def create(name, specification=None):
        type_of_data = TypeOfData.objects.create(type_name=name,type_specific = specification)

        type_of_data.save()

        return type_of_data

    @staticmethod
    def delete_by_name(name):
        TypeOfData.objects.filter(type_name=name).first().delete()

    @staticmethod
    def delete_by_id(id):
        TypeOfData.objects.filter(type_id=id).first().delete()

    @staticmethod
    def get_all():
        return TypeOfData.objects.all()


class SchemaColumn(models.Model):
    column_id = models.AutoField(primary_key=True)
    column_name = models.TextField(max_length=128, verbose_name="Column name")
    column_type = models.ForeignKey(TypeOfData, on_delete=models.DO_NOTHING, verbose_name="Type",
                                    related_name="column_type")
    column_specific = models.TextField(max_length=64, null=True, blank=True)
    column_order = models.IntegerField(verbose_name="Order")

    class Meta:
        ordering = ["column_order"]

    def __str__(self):
        return f"{self.column_name}|{self.column_type}|{self.column_order}"

    def __repr__(self):
        return f"{self.__class__.__name__}({self.column_id})"

    @staticmethod
    def get_by_id(id):
        return SchemaColumn.objects.filter(column_id=id).first()

    @staticmethod
    def create(name, type_of_data,specific, order):
        schema = SchemaColumn.objects.create(column_name = name, column_type = type_of_data,
                                             column_specific=specific, column_order = order)

        schema.save()

        return schema

    def update(self, name=None, type_of_data=None, order=None):
        if name:
            self.column_name = name

        if type_of_data:
            self.column_type = type_of_data

        # Create validation of orders
        if order:
            self.column_order = order

        self.save()

    @staticmethod
    def delete_by_id(id):
        SchemaColumn.objects.filter(column_id=id).first().delete()

    @staticmethod
    def get_all():
        return SchemaColumn.objects.all()

    def to_dict(self):
        return {
            "name": self.column_name,
            "type": self.column_type,
            "specific": self.column_specific,
            "order": self.column_order,
        }


class Schema(models.Model):
    schema_id = models.AutoField(primary_key=True)
    schema_user = models.ForeignKey(User,on_delete=models.CASCADE,related_name="schema_user")
    schema_name = models.TextField(max_length=128, verbose_name="Name")
    schema_column_separator = models.IntegerField(choices=SEPARATOR,default=0,verbose_name="Column separator")
    schema_string_character = models.IntegerField(choices=STRING_CHARACTER,default=0,verbose_name="String character")
    schema_columns = models.ManyToManyField(SchemaColumn,related_name="schema_columns")
    schema_last_modified = models.DateField(verbose_name="Modified",auto_now=True)

    def __str__(self):
        return f"{self.schema_user}:{self.schema_name}"

    def __repr__(self):
        return f"{self.__class__.__name__}({self.schema_id})"

    @staticmethod
    def get_by_id(id):
        return Schema.objects.filter(schema_id=id).first()

    @staticmethod
    def create(user,name,separator,character):
        schema = Schema.objects.create(schema_user=user, schema_name=name,
                                       schema_column_separator=separator, schema_string_character=character)

        schema.save()

        return schema

    def update(self, name = None, separator = None,character = None):
        if name:
            self.schema_name = name

        if separator:
            self.schema_column_separator = separator

        if character:
            self.schema_string_character = character

        self.schema_last_modified = timezone.now()

        self.save()

    def add_column(self,column):
        columns = self.schema_columns.all()
        order_list = []
        name_list = []

        if columns:
            for cl in columns:
                order_list.append(cl.column_order)
                name_list.append(cl.column_name)

            if column.column_order in order_list or column.column_name in name_list:
                raise Exception("This order number or name already reserved")

        self.schema_columns.add(column)

    def delete_column(self,column):
        self.schema_columns.remove(column)

    @staticmethod
    def get_by_user_id(user_id):
        return Schema.objects.filter(schema_user=user_id).all()

    @staticmethod
    def delete_by_id(id):
        Schema.get_by_id(id).delete()


class CSVDataSet(models.Model):
    csv_dataset_id = models.AutoField(primary_key=True)
    csv_dataset_created_at = models.DateField(verbose_name="Created at",auto_now=True)
    csv_dataset_status = models.IntegerField(choices=STATUS)
    csv_dataset_file = models.FileField(blank=True,null=True)
    csv_dataset_link = models.CharField(max_length=256,blank=True,null=True)

    def __str__(self):
        return f"{self.csv_dataset_created_at}|{self.csv_dataset_status}"

    def __repr__(self):
        return f"{self.__class__.__name__}({self.csv_dataset_id})"

    @staticmethod
    def get_by_id(id):
        return CSVDataSet.objects.filter(csv_dataset_id=id).first()

    @staticmethod
    def create():
        csv_set = CSVDataSet.objects.create(csv_dataset_status=0)

        csv_set.save()

        return csv_set

    def change_status(self):
        self.csv_dataset_status = 1

        self.save()


class DataSet(models.Model):
    dataset_id = models.AutoField(primary_key=True)
    dataset_schema = models.ForeignKey(Schema,on_delete=models.CASCADE, related_name="dataset_schema")
    dataset_csv = models.ManyToManyField(CSVDataSet,related_name="dataset_csv")

    def __str__(self):
        return f"{self.dataset_id}|{self.dataset_schema}"

    def __repr__(self):
        return f"{self.__class__.__name__}({self.dataset_id})"

    @staticmethod
    def get_by_id(id):
        return DataSet.objects.filter(dataset_id=id).first()

    @staticmethod
    def create(schema):
        dataset = DataSet.objects.create(dataset_schema=schema)

        dataset.save()

        return dataset

    @staticmethod
    def get_by_schema_id(schema_id):
        schema = Schema.get_by_id(schema_id)

        dataset = DataSet.objects.filter(dataset_schema=schema).first()

        return dataset

    def add_csv(self,scv_dataset):
        self.dataset_csv.add(scv_dataset)
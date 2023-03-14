from django.db import models
from django.contrib.auth.models import User

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


class TypeOfData(models.Model):
    type_id = models.AutoField(primary_key=True)
    type_name = models.TextField(max_length=64, verbose_name="Type", unique=True)
    type_specific = models.IntegerField(choices=SPECIFICATOR, default=None, null=True, blank=True)

    def __str__(self):
        return f"{self.type_name}"

    def __repr__(self):
        return f"{self.__class__.__name__}({self.type_id})"

    @staticmethod
    def get_by_name(name):
        type = TypeOfData.objects.filter(type_name=name).first()

        if type:
            return type

        raise Exception("Type didn't find")

    @staticmethod
    def create(name, specification=None):
        type = TypeOfData.objects.create(type_name=name,type_specific = specification)

        type.save()

        return type

    @staticmethod
    def delete_by_name(name):
        TypeOfData.objects.filter(type_name=name).first().delete()

    @staticmethod
    def get_all():
        return TypeOfData.objects.all()


class SchemaColumn(models.Model):
    column_id = models.AutoField(primary_key=True)
    column_name = models.TextField(max_length=128, verbose_name="Column name")
    column_type = models.ForeignKey(TypeOfData, on_delete=models.DO_NOTHING, verbose_name="Type",
                                    related_name="column_type")
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
    def create(name, type, order):
        schema = SchemaColumn.objects.create(column_name = name, column_type = type, column_order = order)

        schema.save()

        return schema

    def update(self, name=None, type=None, order=None):
        if name:
            self.column_name = name

        if type:
            self.column_type = type

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


class Schema(models.Model):
    schema_id = models.AutoField(primary_key=True)
    schema_user = models.ForeignKey(User,on_delete=models.CASCADE,related_name="schema_user")
    schema_name = models.TextField(max_length=128, verbose_name="Name")
    schema_column_separator = models.IntegerField(choices=SEPARATOR,default=0,verbose_name="Column separator")
    schema_string_character = models.IntegerField(choices=STRING_CHARACTER,default=0,verbose_name="String character")
    schema_columns = models.ManyToManyField(SchemaColumn,related_name="schema_columns")
    schema_last_modified = models.DateField(verbose_name="Modified",auto_now=True)

    def __str__(self):
        return f"{self.user}:{self.schema_name}"

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

        self.save()

    def add_column(self,column):
        columns = self.schema_columns.all().last()

        if columns:
            if column.column_order <= columns.column_order:
                raise Exception("This order number already reserved")

        self.schema_columns.add(column)

    def delete_column(self,column):
        self.schema_columns.remove(column)

    @staticmethod
    def get_by_user_id(user_id):
        return Schema.objects.filter(schema_user=user_id).all()



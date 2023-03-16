import io

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.contrib.auth.models import User
from .models import TypeOfData, Schema, SchemaColumn, CSVDataSet, DataSet


class TypeOfDataTestCase(TestCase):
    def setUp(self):
        self.type1 = TypeOfData.create('integer', 0)
        self.type2 = TypeOfData.create('phone', 1)

    def test_type_str(self):
        self.assertEqual(str(self.type1), 'integer',
                         f"Must be 'integer' but returned {self.type1}")
        self.assertEqual(str(self.type2), 'phone',
                         f"Must be 'phone' but returned {self.type2}")

    def test_type_repr(self):
        self.assertEqual(repr(self.type1),
                         f'TypeOfData({self.type1.type_id})',
                         f"Must be TypeOfData({self.type1.type_id}) but returned {repr(self.type1)}")
        self.assertEqual(repr(self.type2),
                         f'TypeOfData({self.type2.type_id})',
                         f"Must be TypeOfData({self.type2.type_id}) but returned {repr(self.type2)}")

    def test_type_get_by_id(self):
        data_type = TypeOfData.get_by_id(self.type1.type_id)
        self.assertEqual(data_type, self.type1,
                         f"Must be {self.type1} but returned {data_type}")

    def test_type_get_by_name(self):
        data_type = TypeOfData.get_by_name('phone')
        self.assertEqual(data_type, self.type2,
                         f"Must be {self.type2} but returned {data_type}")

    def test_type_create(self):
        data_type = TypeOfData.create('string', 0)
        self.assertEqual(data_type.type_name, 'string',
                         f"Must be 'string' but returned {data_type.type_name}")
        self.assertEqual(data_type.type_specific, 0,
                         f"Must be 0 but returned {data_type.type_specific}")

    def test_type_delete_by_name(self):
        TypeOfData.delete_by_name('phone')
        data_type = TypeOfData.get_by_id(self.type2.type_id)
        self.assertIsNone(data_type,
                          f"Must be 'None' but returned {data_type}")

    def test_type_delete_by_id(self):
        TypeOfData.delete_by_id(self.type1.type_id)
        data_type = TypeOfData.get_by_id(self.type1.type_id)
        self.assertIsNone(data_type,
                          f"Must be 'None' but returned {data_type}")

    def test_type_get_all(self):
        types = TypeOfData.get_all()
        self.assertEqual(len(types), 2,
                         f"Must be 2 but returned {len(types)}")


class SchemaColumnTestCase(TestCase):
    def setUp(self):
        self.type1 = TypeOfData.create('integer', 0)
        self.type2 = TypeOfData.create('phone', 1)
        self.column1 = SchemaColumn.create('age', self.type1, "", 1)
        self.column2 = SchemaColumn.create('phone', self.type2, '+1', 2)

    def test_column_str(self):
        self.assertEqual(str(self.column1), 'age|integer|1',
                         f"Must be 'age|integer|1' but returned {self.column1}")
        self.assertEqual(str(self.column2), 'phone|phone|2',
                         f"Must be 'phone|phone|2' but returned {self.column2}")

    def test_column_repr(self):
        self.assertEqual(repr(self.column1), f'SchemaColumn({self.column1.column_id})',
                         f"Must be TypeOfData({self.type1.type_id}) but returned {repr(self.type1)}")
        self.assertEqual(repr(self.column2), f'SchemaColumn({self.column2.column_id})',
                         f"Must be TypeOfData({self.type2.type_id}) but returned {repr(self.type2)}")

    def test_column_get_by_id(self):
        column = SchemaColumn.get_by_id(self.column1.column_id)
        self.assertEqual(column, self.column1,
                         f"Must be {self.column1} but returned {column}")

    def test_column_create(self):
        column = SchemaColumn.create('name', self.type1, None, 3)
        self.assertEqual(column.column_name, 'name')
        self.assertEqual(column.column_type, self.type1)
        self.assertIsNone(column.column_specific)
        self.assertEqual(column.column_order, 3)

        # Test creating a column with an invalid order value
        with self.assertRaises(ValueError):
            SchemaColumn.create('name', self.type1, None, -1)

        # Test creating a column with an invalid type
        with self.assertRaises(ValueError):
            SchemaColumn.create('name', 'invalid_type', None, 3)


class SchemaTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="test_user",
                                             password="test_password")
        self.schema = Schema.create(user=self.user, name="test_schema",
                                    separator=0, character=0)
        self.type_of_data = TypeOfData.create("test")

    def test_str(self):
        self.assertEqual(str(self.schema), f"{self.user}:test_schema",
                         f"Must be {self.user}:test_schema but returned {str(self.schema)}")

    def test_create(self):
        schema = Schema.create(user=self.user, name="test_schema_2",
                               separator=1, character=1)
        self.assertEqual(schema.schema_user, self.user,
                         f"Must be {self.user} but returned {schema.schema_user}")
        self.assertEqual(schema.schema_name, "test_schema_2",
                         f"Must be test_schema_2 but returned {schema.schema_name}")
        self.assertEqual(schema.schema_column_separator, 1,
                         f"Must be 1 but returned {schema.schema_column_separator}")
        self.assertEqual(schema.schema_string_character, 1,
                         f"Must be 1 but returned {schema.schema_string_character}")

    def test_update(self):
        self.schema.update(name="updated_test_schema",
                           separator=1, character=1)
        self.assertEqual(self.schema.schema_name, "updated_test_schema",
                         f"Must be updated_test_schema but returned {self.schema.schema_name}")
        self.assertEqual(self.schema.schema_column_separator, 1,
                         f"Must be 1 but returned {self.schema.schema_column_separator}")
        self.assertEqual(self.schema.schema_string_character, 1,
                         f"Must be 1 but returned {self.schema.schema_string_character}")

    def test_add_column(self):
        column = SchemaColumn.create("column_1", self.type_of_data, "", 1)
        self.schema.add_column(column)
        self.assertIn(column, self.schema.schema_columns.all(),
                      f"{column} must be in {self.schema.schema_columns.all()}")

    def test_delete_column(self):
        column = SchemaColumn.create("column_1", self.type_of_data, "", 1)
        self.schema.add_column(column)
        self.schema.delete_column(column)
        self.assertNotIn(column, self.schema.schema_columns.all(),
                         f"{column} must not be in {self.schema.schema_columns.all()}")

    def test_get_by_user_id(self):
        schema_list = Schema.get_by_user_id(self.user.id)
        self.assertIn(self.schema, schema_list,
                      f"{self.schema} must be in {schema_list}")

    def test_delete_by_id(self):
        Schema.delete_by_id(self.schema.schema_id)
        schema_list = Schema.get_by_user_id(self.user.id)
        self.assertNotIn(self.schema, schema_list,
                         f"{self.schema} must not be in {schema_list}")

    def test_get_delimiter(self):
        self.assertEqual(self.schema.get_delimiter(), ",",
                         f"Must be ',' but returned {self.schema.get_delimiter()}")

    def test_get_character(self):
        self.assertEqual(self.schema.get_character(), '"',
                         f"Must be '\"' but returned {self.schema.get_character()}")


class CSVDataSetTestCase(TestCase):
    def setUp(self):
        self.csv_set = CSVDataSet.create()

    def test_csv_dataset_create(self):
        self.assertEqual(len(CSVDataSet.objects.all()), 1,
                         f"Must be 1 CSVDataSet instance but returned {len(CSVDataSet.objects.all())}")

    def test_csv_dataset_change_status(self):
        self.csv_set.change_status()
        self.assertEqual(self.csv_set.csv_dataset_status, 1,
                         f"Must be 1 but returned {self.csv_set.csv_dataset_status}")

    def test_csv_dataset_get_by_id(self):
        csv_set = CSVDataSet.get_by_id(self.csv_set.csv_dataset_id)
        self.assertEqual(csv_set, self.csv_set,
                         f"Must be {self.csv_set} but returned {csv_set}")

    def test_csv_file_field(self):
        csv_data = b"id,name,age\n1,John,30\n2,Jane,25\n3,Bob,40\n"
        csv_file = SimpleUploadedFile("test.csv", csv_data, content_type="text/csv")

        csv_set = CSVDataSet.create()

        # Test uploading a CSV file
        csv_set.csv_dataset_file.save("test.csv", csv_file)
        csv_set.save()

        # Test reading the uploaded CSV file
        with io.StringIO() as csv_buffer:
            csv_buffer.write(csv_set.csv_dataset_file.read().decode("utf-8"))
            csv_buffer.seek(0)
            csv_lines = [line.strip() for line in csv_buffer.readlines()]

        expected_csv_lines = ["id,name,age", "1,John,30", "2,Jane,25", "3,Bob,40"]
        self.assertListEqual(csv_lines, expected_csv_lines,
                             f"Must be {expected_csv_lines} but returned {csv_lines}")


class DataSetTestCase(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(username="test_user", password="12345")
        self.schema = Schema.create(self.user, 'test_schema', 0, 0)
        self.csv_dataset1 = CSVDataSet.create()
        self.csv_dataset2 = CSVDataSet.create()

    def test_create_dataset(self):
        dataset = DataSet.create(self.schema)
        self.assertEqual(dataset.dataset_schema, self.schema,
                         "The dataset schema does not match")
        self.assertEqual(dataset.dataset_csv.count(), 0,
                         "The number of CSV datasets in the dataset is incorrect")

    def test_add_csv_to_dataset(self):
        dataset = DataSet.create(self.schema)
        dataset.add_csv(self.csv_dataset1)
        dataset.add_csv(self.csv_dataset2)
        self.assertEqual(dataset.dataset_csv.count(), 2,
                         "The number of CSV datasets in the dataset is incorrect after adding them")

    def test_get_dataset_by_id(self):
        dataset = DataSet.create(self.schema)
        retrieved_dataset = DataSet.get_by_id(dataset.dataset_id)
        self.assertEqual(retrieved_dataset, dataset,
                         "The retrieved dataset is not the same as the original dataset")

    def test_get_dataset_by_schema_id(self):
        dataset = DataSet.create(self.schema)
        retrieved_dataset = DataSet.get_by_schema_id(self.schema.schema_id)
        self.assertEqual(retrieved_dataset, dataset,
                         "The retrieved dataset is not the same as the original dataset")

from django.test import TestCase
from ..models import Author

# create your tests here:

"""Um exemplo prático de teste:
class YourTestClass(TestCase):
    @classmethod
    def setUpTestData(cls):
        print('setUpTestData: execute uma vez para configurar dados não modificados para todos os métodos de classe.')
        pass

    def setUp(self):
        print('SetUp: execute uma vez para cada método de teste para configurar dados limpos.')
        pass

    def test_false_is_false(self):
        print('Método: test_false_is_false.')
        self.assertFalse(False)

    def test_false_is_true(self):
        print('Método: test_false_is_true.')
        self.assertTrue(False)

    def test_one_plus_one_equals_two(self):
        print('Method: test_one_plus_one_equals_two.')
        self.assertEqual(1 + 1, 2)"""


class AuthorModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Configura objetos não modificados usados por todos os métodos de teste.
        Author.objects.create(first_name='Big', last_name='Bob')

    def test_first_name_label(self):
        author = Author.objects.get(id=1)
        field_label = author._meta.get_field('first_name').verbose_name
        self.assertEquals(field_label, 'first name')

    def test_last_name_label(self):
        author = Author.objects.get(id=1)
        field_label = author._meta.get_field('last_name').verbose_name
        self.assertEquals(field_label, 'last name')

    def test_date_of_birth_label(self):
        author = Author.objects.get(id=1)
        field_label = author._meta.get_field('date_of_birth').verbose_name
        self.assertEquals(field_label, 'date of birth')

    def test_date_of_death_label(self):
        author = Author.objects.get(id=1)
        field_label = author._meta.get_field('date_of_death').verbose_name
        self.assertEquals(field_label, 'died')

    def test_first_name_max_length(self):
        author = Author.objects.get(id=1)
        max_length = author._meta.get_field('first_name').max_length
        self.assertEquals(max_length, 100)

    def test_last_name_max_length(self):
        author = Author.objects.get(id=1)
        max_length = author._meta.get_field('last_name').max_length
        self.assertEquals(max_length, 100)

    def test_object_name_is_last_name_comma_first_name(self):
        author = Author.objects.get(id=1)
        expected_object_name = f'{author.last_name}, {author.first_name}'
        self.assertEquals(expected_object_name, str(author))

    def test_get_absolute_url(self):
        author = Author.objects.get(id=1)
        # Isso irá falhar se o urlconf não estiver definido.
        self.assertEquals(author.get_absolute_url(), '/catalog/author/1')

import datetime, uuid
from ..models import Author, BookInstance, Book, Genre, Language
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
# Necessário para atribuir o usuário como um mutuário:
from django.contrib.auth.models import User

# Requerido para conceder a permissão necessária para definir um livro como retornado:
from django.contrib.auth.models import Permission


class AuthorListViewTest(TestCase):
    @classmethod
    def SetUpTestData(cls):
        # Cria 13 autores para os testes de paginação:
        number_of_authors = 13
        
        for author_id in range(number_of_authors):
            Author.objects.create(
                first_name=f'Christian {author_id}',
                last_name=f'Surname {author_id}',
            )
    
    def test_view_url_exists_at_desired_location(self):
        response = self.client.get('/catalog/authors/')
        self.assertEqual(response.status_code, 200)
    
    def test_view_url_acessible_by_name(self):
        response = self.client.get(reverse('authors'))
        self.assertEqual(response.status_code, 200)
    
    def test_view_uses_correct_template(self):
        response = self.client.get(reverse('authors'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'catalog/author_list.html')
    
    def test_pagination_is_ten(self):
        response = self.client.get(reverse('authors'))
        self.assertEqual(response.status_code, 200)
        self.assertTrue('is_paginated' in response.context)
        self.assertTrue(response.context['is_paginated'] == True)
        self.assertTrue(response.context['author_list'] == 10)
    
    def test_lists_all_authors(self):
        # Pega a segunda página e confirma se tem (exatamente) 3 itens restantes.
        response = self.client.get(reverse('authors') + '?page=2')
        self.assertEqual(response.status_code, 200)
        self.assertTrue('is_paginated' in response.context)
        self.assertTrue(response.context['is_paginated'] == True)
        self.assertTrue(len(response.context['author_list']) == 3)


class LoanedBookInstancesByUserListViewTest(TestCase):
    def setUp(self):
        # Cria dois usuários:
        test_user1 = User.objects.create_user(username='testuser1', password='1X<ISRUkw+tuK')
        test_user2 = User.objects.create_user(username='testuser2', password='2HJ1vRV0Z&3iD')
        
        test_user1.save()
        test_user2.save()
        
        # Cria um livro:
        test_author = Author.objects.create(first_name='John', last_name='Smith')
        test_genre = Genre.objects.create(name='Fantasy')
        test_language = Language.objects.create(name='English')
        test_book = Book.objects.create(
            title='Book Title',
            summary='My book summary',
            isbn='ABCDEFG',
            author=test_author,
            language=test_language,
        )
        
        # Cria o gênero como um post-step (pós-passo):
        genre_objects_for_book = Genre.objects.all()
        test_book.genre.set(genre_objects_for_book)  # Atribuição direta de tipos muitos-para-muitos não é permitida.
        test_book.save()
        
        # Cria 30 objetos BookInstance:
        number_of_book_copies = 30
        for book_copy in range(number_of_book_copies):
            return_date = timezone.localtime() + datetime.timedelta(days=book_copy % 5)
            the_borrower = test_user1 if book_copy % 2 else test_user2
            status = 'm'
            BookInstance.objects.create(
                book=test_book,
                imprint='Unlikely Imprint, 2016',
                due_back=return_date,
                borrower=the_borrower,
                status=status,
            )
    
    def test_redirect_if_not_logged_in(self):
        response = self.client.get(reverse('my-borrowed'))
        self.assertRedirects(response, '/accounts/login/?next=/catalog/mybooks/')
    
    def test_logged_in_uses_correct_template(self):
        login = self.client.login(username='testuser1', password='1X<ISRUkw+tuK')
        response = self.client.get(reverse('my-borrowed'))
        
        # Checa se o usuário está logado:
        self.assertEqual(str(response.context['user']), 'testuser1')
        
        # Checa se temos a response "success":
        self.assertEqual(response.status_code, 200)
        
        # Checa se foi usado o template correto:
        self.assertTemplateUsed(response, 'catalog/bookinstance_list_borrowed_user.html')
    
    def test_only_borrowed_books_in_list(self):
        login = self.client.login(username='testuser1', password='1X<ISRUkw+tuK')
        response = self.client.get(reverse('my-borrowed'))
        
        # Checa se o usuário está logado:
        self.assertEqual(str(response.context['user']), 'testuser1')
        # Checa se temos a response "success":
        self.assertEqual(response.status_code, 200)
        
        # Checa se inicialmente não temos quaisquer livros na lista (none, on loan)
        self.assertTrue('bookinstance_list' in response.context)
        self.assertEqual(len(response.context['bookinstance_list']), 0)
        
        # Agora mude todos os livros para 'on loan':
        books = BookInstance.objects.all()[:10]
        
        for book in books:
            book.status = 'o'
            book.save()
        
        # Checa se agora temos livros emprestados na lista:
        response = self.client.get(reverse('my-borrowed'))
        # Checa se o usuário está logado:
        self.assertEqual(str(response.context['user']), 'testuser1')
        # Checa se temos a response "success":
        self.assertEqual(response.status_code, 200)
        
        self.assertTrue('bookinstance_list' in response.context)
        
        # Confirma se todos os livros pertencem ao testuser1 e estão por empréstimo:
        for bookitem in response.context['bookinstance_list']:
            self.assertEqual(response.context['user'], bookitem.borrower)
            self.assertEqual('o', bookitem.status)
    
    def test_pages_ordered_by_due_date(self):
        # Muda todos os livros para 'on loan':
        for book in BookInstance.objecte.all():
            book.status = 'o'
            book.save()
        
        login = self.client.login(username='testuser1', password='1X<ISRUkw+tuK')
        response = self.client.get(reverse('my-borrowed'))
        
        # Checa se o usuário está logado:
        self.assertEqual(str(response.context['user']), 'testuser1')
        # Checa se temos a response "success":
        self.assertEqual(response.status_code, 200)
        
        # Confirma se dentre os itens, apenas 10 estão sendo mostrados na paginação:
        self.assertEqual(len(response.context['bookinstance_list']), 10)
        
        last_date = 0
        for book in response.context['bookinstance_list']:
            if last_date == 0:
                last_date = book.due_back
            
            else:
                self.assertTrue(last_date <= book.due_back)
                last_date = book.due_back


class RenewBookInstanceViewTest(TestCase):
    def setUp(self):
        # Cria um usuário:
        test_user1 = User.objects.create_user(username='testuser1', password='1X<ISRUkw+tuK')
        test_user2 = User.objects.create_user(username='testuser2', password='2HJ1vRV0Z&3iD')
        
        test_user1.save()
        test_user2.save()
        
        permission = Permission.objects.get(name='Set book as returned')
        test_user2.user_permissions.add(permission)
        test_user2.save()
        
        # Cria um livro:
        test_author = Author.objects.create(first_name='John', last_name='Smith')
        test_genre = Genre.objects.create(name='Fantasy')
        test_language = Language.objects.create(name='English')
        test_book = Book.objects.create(
            title='Book Title',
            summary='My book summary',
            isbn='ABCDEFG',
            author=test_author,
            language=test_language,
        )
        
        # Cria um gênero como um post-step (pós-passo):
        genre_objects_for_book = Genre.objects.all()
        test_book.genre.set(genre_objects_for_book)  # Atribuição direta de tipos muitos-para-muitos não é permitida.
        test_book.save()
        
        # Cria um objeto BookInstance para o test_user1:
        return_date = datetime.date.today() + datetime.timedelta(days=5)
        self.test_bookinstance1 = BookInstance.objects.create(
            book=test_book,
            imprint='Unlikely Imprint, 2016',
            due_back=return_date,
            borrower=test_user1,
            status='o'
        )
        
        # Cria um objeto BookInstance para o test_user2:
        return_date = datetime.date.today() + datetime.timedelta(days=5)
        self.test_bookinstance2 = BookInstance.objects.create(
            book=test_book,
            imprint='Unlikely Imprint, 2016',
            due_back=return_date,
            borrower=test_user2,
            status='o'
        )

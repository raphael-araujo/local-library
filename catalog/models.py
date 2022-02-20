from django.db import models
from django.urls import reverse  # Usado para gerar URLs revertendo os padrões de URL.
from django.contrib.auth.models import User
from datetime import date
import uuid  # Necessário para gerar instâncias únicas de livros (id em BookInstance).

# Create your models here.


class Genre(models.Model):
    """Modelo representando um gênero de livro."""
    name = models.CharField(max_length=200, help_text='Insira um gênero de livro (ex: Ficção Científica)')
    
    def __str__(self):
        """String para representar o objeto Model."""
        return self.name


class Language(models.Model):
    """Modelo representando a Línguagem do livro (ex: Inglês, Japonês, Francês, etc.)"""
    name = models.CharField(max_length=200, help_text='Insira a línguagem natural do livro (ex: Inglês, Japonês, etc)')
    
    def __str__(self):
        """String para representar o objeto Model (no site Admin, etc.)"""
        return self.name


class Book(models.Model):
    """Modelo representando um livro (mas não especifica a cópia de um livro)."""
    title = models.CharField(max_length=200)
    
    # ForeignKey sendo usada pois um livro pode ter somente um autor, mas os autores podem ter vários livros:
    # Author é uma string ao invés de um objeto porque ainda não foi declarado no arquivo.
    author = models.ForeignKey('Author', on_delete=models.SET_NULL, null=True)
    
    summary = models.TextField(max_length=1000, help_text='Entre com uma descrição do livro')
    isbn = models.CharField(
        'ISBN',
        max_length=13,
        help_text='13 Character <a href="https://www.isbn-international.org/content/what-isbn">ISBN number</a>'
    )
    
    # ManyToManyField usado porque um gênero pode conter vários livros e um livro pode conter vários gêneros.
    # A classe Genre já foi definida, então podemos especificar o objeto acima.
    genre = models.ManyToManyField(Genre, help_text='Selecione um gênero para este livro')
    
    language = models.ForeignKey('Language', on_delete=models.SET_NULL, null=True)
    
    def __str__(self):
        """String para representar o objeto Model."""
        return self.title
    
    def get_absolute_url(self):
        """Retorna a URL para acessar um registro de detalhes para este livro"""
        return reverse('book-detail', args=[str(self.id)])
    
    def display_genre(self):
        """Cria uma string para o gênero. Isso é necessário para mostrar o gênero no model localizado em Admin.py"""
        return ', '.join(genre.name for genre in self.genre.all()[:3])
    
    display_genre.short_description = 'Genre'
    

class BookInstance(models.Model):
    """Modelo representando uma cópia específica de um livro (ex: que pode ser pego emprestado da biblioteca)."""
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        help_text='ID único deste livro partícular em toda a biblioteca'
    )
    book = models.ForeignKey('Book', on_delete=models.SET_NULL, null=True)
    imprint = models.CharField(max_length=200)
    due_back = models.DateField(null=True, blank=True)
    borrower = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    
    LOAN_STATUS = (
        ('m', 'Maintenance'),
        ('o', 'On loan'),
        ('a', 'Available'),
        ('r', 'Reserved'),
    )

    status = models.CharField(
        max_length=1,
        choices=LOAN_STATUS,
        blank=True,
        default='m',
        help_text='Disponibilidade do livro',
    )

    class Meta:
        ordering = ['due_back']
        permissions = (('can_mark_returned', 'Set book as returned'),)

    def __str__(self):
        """String para rebresentar o objeto Model"""
        return f'{self.id} ({self.book.title})'

    @property
    def is_overdue(self):
        """Verifica se uma instância está atrasada"""
        if self.due_back and date.today() > self.due_back:
            return True
        return False
    
    
class Author(models.Model):
    """Modelo representando um autor."""
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    date_of_birth = models.DateField(null=True, blank=True)
    date_of_death = models.DateField('died', null=True, blank=True)
    
    class Meta:
        ordering = ['last_name', 'first_name']
    
    def get_absolute_url(self):
        """Retorna a URL para acessar uma instância de autor em particular."""
        return reverse('author-detail', args=[str(self.id)])
    
    def __str__(self):
        """String para representar o objeto Model."""
        return f'{self.last_name}, {self.first_name}'


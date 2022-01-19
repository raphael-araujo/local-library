from django.shortcuts import render
from .models import Book, Author, BookInstance, Genre

# Create your views here.


def index(request):
    """View function para a home page do site."""
    
    # Gera a contagem de alguns dos objetos principais
    num_books = Book.objects.all().count()
    num_instances = Book.objects.all().count()
    
    # Livros disponíveis (status = 'a')
    num_instances_avaiable = BookInstance.objects.filter(status__exact='a').count()
    
    # O 'all()' fica implícito como padrão.
    num_autors = Author.objects.count()
    
    context = {
        'num_books': num_books,
        'num_instances': num_instances,
        'num_instances_avaiable': num_instances_avaiable,
        'num_autors': num_autors
    }
    
    # Renderiza o template HTML (index.html) com os dados da variável 'context':
    return render(request, 'index.html', context=context)

import datetime
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib.auth.decorators import permission_required
from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.urls import reverse, reverse_lazy
from .forms import RenewBookForm
from .models import Book, Author, BookInstance, Genre
from django.views import generic
from django.views.generic.edit import CreateView, UpdateView, DeleteView


# Create your views here.


def index(request):
    """View function para a home page do site."""
    
    # Gera a contagem de alguns dos objetos principais
    num_books = Book.objects.all().count()
    num_instances = Book.objects.all().count()
    num_genres = Genre.objects.all().count()
    
    # Livros disponíveis (status = 'a')
    num_instances_available = BookInstance.objects.filter(status__exact='a').count()
    
    # Livro com alguma palavra específica:
    word = 'Outro'
    filter_books_by = Book.objects.filter(title__icontains=word)
    
    # O 'all()' fica implícito como padrão.
    num_authors = Author.objects.count()
    
    #  Número de visitas para esta view, é contado na variável session:
    num_visits = request.session.get('num_visits', 0)
    request.session['num_visits'] = num_visits + 1
    
    context = {
        'num_books': num_books,
        'num_instances': num_instances,
        'num_instances_available': num_instances_available,
        'num_authors': num_authors,
        'num_genres': num_genres,
        'word': word,
        'filter_books_by': filter_books_by,
        'num_visits': num_visits
    }
    
    # Renderiza o template HTML (index.html) com os dados da variável 'context':
    return render(request, 'index.html', context=context)


class BookListView(generic.ListView):
    model = Book
    context_object_name = 'book_list'  # <- variável de template
    # queryset = Book.objects.filter(title__icontains='Livro')[:5]  # Pega 5 livros que contém a palavra filtrada.
    template_name = 'books/book_list.html'  # Especifica o nome/localização do template
    paginate_by = 10


class BookDetailView(generic.DetailView):
    model = Book


class AuthorListView(generic.ListView):
    model = Author
    paginate_by = 10


# class AuthorDetailView(generic.DetailView): (Irei tentar depois)
#     model = Book
# pk_url_kwarg = Author.pk
# books = Book.objects.all()
# authors = Author.objects.all()
# context_object_name = 'books'
# extra_context = {'books': books}
# queryset = Book.objects.all()
# template_name = 'catalog/author_detail.html'  # Especifica o nome/localização do template


# class BookInstanceDetailView(generic.DetailView):
#     model = BookInstance
#     template_name = 'catalog/author_detail.html'  # Especifica o nome/localização do template


def author_detail_view(request, pk):
    authors = Author.objects.filter(pk=pk)
    books = Book.objects.filter(author=pk).order_by('title')
    instances = BookInstance.objects.filter(book__author__id=pk)
    context = {
        'authors': authors,
        'books': books,
        'instances': instances
    }
    return render(request, 'catalog/author_detail.html', context)


# Para criar usuários:
# from django.contrib.auth.models import User
#
# # Create user and save to the database
# user = User.objects.create_user('myusername', 'myemail@crazymail.com', 'mypassword')
#
# # Update fields and then save again
# user.first_name = 'John'
# user.last_name = 'Citizen'
# user.save()


class LoanedBooksByUserListView(LoginRequiredMixin, generic.ListView):
    """class-based view genérica que lista os livros emprestados para o usuário atual."""
    
    model = BookInstance
    template_name = 'catalog/bookinstance_list_borrowed_user.html'
    paginate_by = 10
    
    def get_queryset(self):
        return BookInstance.objects.filter(borrower=self.request.user).filter(status__exact='o').order_by('due_back')


class OnLoanBooksListView(PermissionRequiredMixin, generic.ListView):
    """class-based view genérica que lista quais usuários pegaram livros emprestados"""
    model = BookInstance
    template_name = 'catalog/bookinstance_list_borrowed_staff.html'
    paginate_by = 10
    permission_required = 'catalog.can_mark_returned'
    
    def get_queryset(self):
        return BookInstance.objects.filter(status__exact='o').order_by('due_back')


@permission_required('catalog.can_mark_returned')
def renew_book_librarian(request, pk):
    """View function para renovação de BookInstance específico por um bibliotecário."""
    book_instance = get_object_or_404(BookInstance, pk=pk)
    
    # Se for uma requisição POST, será processado os dados do Form
    if request.method == 'POST':
        
        # Cria uma instância de formulário e preenche ela com os dados da requisição (binding):
        form = RenewBookForm(request.POST)
        
        # Checa se o formulário é válido:
        if form.is_valid():
            # Processa os em form.cleaned_data conforme necessário (aqui apenas escrevemos no campo modelo due_back)
            book_instance.due_back = form.cleaned_data['renewal_date']
            book_instance.save()
            
            # Rediceciona para a nova URL:
            return HttpResponseRedirect(reverse('all-borrowed'))
    
    # Se for uma requisição GET (ou qualquer outro método) cria um formulário padrão.
    else:
        proposed_renewal_date = datetime.date.today() + datetime.timedelta(weeks=3)
        form = RenewBookForm(initial={'renewal_date': proposed_renewal_date})
    
    context = {
        'form': form,
        'book_instance': book_instance
    }
    
    return render(request, 'catalog/book_renew_librarian.html', context)


# Formulários para criar, alterar e deletar autores:
class AuthorCreate(PermissionRequiredMixin, CreateView):
    model = Author
    fields = '__all__'
    initial = {'date_of_death': '05/01/2018'}
    permission_required = 'catalog.can_mark_returned'


class AuthorUpdate(PermissionRequiredMixin, UpdateView):
    model = Author
    fields = ['first_name', 'last_name', 'date_of_birth', 'date_of_death']
    permission_required = 'catalog.can_mark_returned'


class AuthorDelete(PermissionRequiredMixin, DeleteView):
    model = Author
    success_url = reverse_lazy('authors')
    permission_required = 'catalog.can_mark_returned'


# Formulários para criar, alterar e deletar livros:
class BookCreate(PermissionRequiredMixin, CreateView):
    model = Book
    fields = '__all__'
    permission_required = 'catalog.can_mark_returned'


class BookUpdate(PermissionRequiredMixin, UpdateView):
    model = Book
    fields = '__all__'
    permission_required = 'catalog.can_mark_returned'


class BookDelete(PermissionRequiredMixin, DeleteView):
    model = Book
    success_url = reverse_lazy('books')
    permission_required = 'catalog.can_mark_returned'

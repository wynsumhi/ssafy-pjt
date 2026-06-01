from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from .forms import BookForm, UpdateBookForm
from .models import Book


# F12
@login_required
def index(request):
    books = Book.objects.all()
    context = {
        "books": books,
    }
    return render(request, "books/index.html", context)


# F13
@login_required
def create(request):
    if request.method == "POST":
        form = BookForm(request.POST)
        if form.is_valid():
            book = form.save()
            return redirect("books:index")
    else:
        form = BookForm()
    context = {
        "form": form,
    }
    return render(request, "books/create.html", context)


# F14
@login_required
def detail(request, pk):
    if request.method == "GET":
        book = Book.objects.get(pk=pk)

        context = {
            "book": book,
        }

        return render(request, "books/detail.html", context)


# F15
@login_required
def update(request, pk):
    book = Book.objects.get(pk=pk)
    if request.method == "POST":
        form = UpdateBookForm(request.POST, instance=book)
        if form.is_valid():
            form.save()
            return redirect("books:detail", pk=pk)
    else:
        form = UpdateBookForm(instance=book)
    context = {
        "form": form,
        "book": book,
    }
    return render(request, "books/update.html", context)


# F16
@login_required
def delete(request, pk):
    book = Book.objects.get(pk=pk)
    if request.method == "POST":
        book.delete()
    return redirect("books:index")

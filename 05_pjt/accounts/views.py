from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth import login as auth_login
from django.contrib.auth import logout as auth_logout
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from books.models import Book

from .forms import (
    CustomAuthenticationForm,
    CustomPasswordChangeForm,
    CustomUserChangeForm,
    CustomUserCreationForm,
)

# F06
def login(request):
    if request.user.is_authenticated:
        return redirect("books:index")

    if request.method == "POST":
        form = CustomAuthenticationForm(request, request.POST)
        if form.is_valid():
            auth_login(request, form.get_user())
            return redirect("books:index")
    else:
        form = CustomAuthenticationForm()
    context = {
        "form": form,
    }
    return render(request, "accounts/login.html", context)

# F07
def logout(request):
    if request.method == "POST":
        auth_logout(request)
    return redirect("books:index")

# F08
def signup(request):
    if request.user.is_authenticated:
        return redirect("books:index")

    if request.method == "POST":
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            auth_login(request, user)
            return redirect("books:index")
    else:
        form = CustomUserCreationForm()
    context = {
        "form": form,
    }
    return render(request, "accounts/signup.html", context)

# F09
@login_required
def update(request):
    if request.method == "POST":
        form = CustomUserChangeForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect("accounts:profile", request.user.username)
    else:
        form = CustomUserChangeForm(instance=request.user)
    context = {
        "form": form,
    }
    return render(request, "accounts/update.html", context)


@login_required
def delete(request):
    if request.method == "POST":
        request.user.delete()
        auth_logout(request)
    return redirect("books:index")


@login_required
def change_password(request):
    if request.method == "POST":
        form = CustomPasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, "Password changed successfully")
            return redirect("accounts:profile", request.user.username)
    else:
        form = CustomPasswordChangeForm(request.user)
    context = {
        "form": form,
    }
    return render(request, "accounts/change_password.html", context)


@login_required
def profile(request, username):
    User = get_user_model()
    user = User.objects.get(username=username)
    # user와 books 간의 관계가 없으므로 모든 books를 표시
    books = Book.objects.all()
    context = {
        "user_profile": user,
        "books": books,
    }
    return render(request, "accounts/profile.html", context)

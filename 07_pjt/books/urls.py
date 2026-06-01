from django.urls import path
from . import views

app_name = "books"

urlpatterns = [
    path("categories/", views.category_list, name="category_list"),
    path("", views.book_list, name="book_list"),
    path("<int:book_pk>/", views.book_detail, name="book_detail"),
    path("threads/", views.thread_list, name="thread_list"),
    path("threads/<int:thread_pk>/", views.thread_detail, name="thread_detail"),
    path("<int:book_pk>/threads/create/", views.create_thread, name="create_thread"),
    path("threads/<int:thread_pk>/comments/", views.create_comment, name="create_comment"),
    path("comments/<comment_pk>/", views.comment_detail, name="comment_detail"),
]

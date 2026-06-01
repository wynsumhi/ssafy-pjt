from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.views.decorators.http import (
    require_http_methods,
    require_safe,
    require_POST,
)
from django.contrib.auth.decorators import login_required

from accounts.models import Category
from .models import Book, Thread, Comment
from .forms import ThreadForm, CommentForm
from .utils import (
    generate_image_with_openai,
)


# Index 페이지
def index(request):
    books = Book.objects.all()
    categories = Category.objects.all()
    context = {
        "books": books,
        "categories": categories,
    }
    return render(request, "books/index.html", context)

# 장르별 필터링
def filter_category(request):
    category_name = request.GET.get('category', '')
    
    if category_name:
        # 특정 카테고리의 도서만 필터링
        books = Book.objects.filter(category__name=category_name)
    else:
        # 전체 도서 조회
        books = Book.objects.all()
    
    # JSON 형태로 도서 데이터 변환
    books_data = []
    for book in books:
        books_data.append({
            'id': book.pk,
            'title': book.title,
            'description': book.description,
            'cover': book.cover if book.cover else '',
        })
    
    return JsonResponse({'books': books_data})

@require_safe
def detail(request, book_pk):
    book = Book.objects.get(pk=book_pk)
    context = {
        "book": book,
    }
    return render(request, "books/detail.html", context)

@login_required
@require_http_methods(["GET", "POST"])
def thread_create(request, book_pk):
    book = Book.objects.get(pk=book_pk)
    if request.method == "POST":
        form = ThreadForm(request.POST, request.FILES)
        if form.is_valid():
            thread = form.save(commit=False)
            thread.book = book
            thread.user = request.user
            thread.save()

            generated_image_path = generate_image_with_openai(thread.title, thread.content, book.title, book.author)
            if generated_image_path:
                thread.cover_img = generated_image_path
                thread.save()
                
            return redirect("books:thread_detail", book.pk, thread.pk)
    else:
        form = ThreadForm()
    context = {
        "form": form,
        "book": book,
    }
    return render(request, "books/thread_create.html", context)


@login_required
@require_safe
def thread_detail(request, book_pk, thread_pk):
    book = Book.objects.get(pk=book_pk)
    thread = Thread.objects.get(pk=thread_pk)
    comment_form = CommentForm()
    context = {
        "book" : book,
        "thread": thread,
        "comment_form" : comment_form,
    }
    return render(request, "books/thread_detail.html", context)



@login_required
@require_http_methods(["GET", "POST"])
def thread_update(request, book_pk, thread_pk):
    book = Book.objects.get(pk=book_pk)
    thread = Thread.objects.get(pk=thread_pk)
    comment_form = CommentForm(request.POST)
    if thread.user == request.user:
        if request.method == "POST":
            form = ThreadForm(request.POST, request.FILES, instance=thread)
            if form.is_valid():
                form.save()  
                return redirect('books:thread_detail', book_pk=book.pk, thread_pk=thread.pk)
        else:
            form = ThreadForm(instance=thread)
    else :
        return redirect('books:index') 
    context = {
        "form": form,
        "book": book,
        "comment_form" : comment_form,
    }
    return render(request, "books/thread_update.html", context)


@login_required
@require_POST
def thread_delete(request, book_pk, thread_pk):
    thread = Thread.objects.get(pk=thread_pk)
    if thread.user == request.user:
        thread.delete()
    return redirect("books:detail", book_pk)


# 쓰레드 좋아요 비동기 처리
@login_required
@require_POST
def likes(request, book_pk, thread_pk):
    thread = Thread.objects.get(pk=thread_pk)
    
    # 좋아요 토글
    if request.user in thread.likes.all():
        thread.likes.remove(request.user)
        is_liked = False
    else:
        thread.likes.add(request.user)
        is_liked = True
    
    return JsonResponse({
        'success': True,
        'is_liked': is_liked,
        'likes_count': thread.likes.count(),
    })

# 쓰레드 댓글 비동기 처리
@login_required
@require_POST
def create_comment(request, book_pk, thread_pk):
    thread = Thread.objects.get(pk=thread_pk)
    comment_form = CommentForm(request.POST)
    if comment_form.is_valid():
        comment = comment_form.save(commit=False)
        comment.thread = thread
        comment.user = request.user
        comment.save()
        return JsonResponse({
            'success': True,
            'comment_id': comment.pk,
            'content': comment.content,
            'username': comment.user.username,
        })
    return JsonResponse({'success': False}, status=400)

@login_required
@require_POST
def delete_comment(request, book_pk, comment_pk):
    try:
        comment = Comment.objects.get(pk=comment_pk)
        # 댓글 작성자 본인만 삭제 가능
        if comment.user == request.user:
            comment.delete()
            return JsonResponse({
                'success': True,
                'message': '댓글이 삭제되었습니다.'
            })
        else:
            return JsonResponse({
                'success': False,
                'message': '댓글 삭제 권한이 없습니다.'
            }, status=403)
    except Comment.DoesNotExist:
        return JsonResponse({
            'success': False,
            'message': '댓글을 찾을 수 없습니다.'
        }, status=404)
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view
from django.shortcuts import get_object_or_404, get_list_or_404
from django.db.models import Count
from .models import Book, Thread, Category, Comment
from .serializers import (
    CategorySerializer,
    ThreadListSerializer,
    CommentSerializer,
    BookListSerializer,
    BookDetailSerializer,
    ThreadDetailSerializer,
    ThreadCreateSerializer,
)


# F07
@api_view(["GET"])
def category_list(request):
    if request.method == "GET":
        # 전체 카테고리 데이터 조회
        categories = Category.objects.all()
        # Serialization 진행
        serializer = CategorySerializer(categories, many=True)
        # serializer 덩어리에서 데이터 추출 (.data 속성)한 것을 응답
        return Response(serializer.data)


# F08
@api_view(["GET"])
def book_list(request):
    if request.method == "GET":
        # 전체 카테고리 데이터 조회
        books = Book.objects.all()
        # Serialization 진행
        serializer = BookListSerializer(books, many=True)
        # serializer 덩어리에서 데이터 추출 (.data 속성)한 것을 응답
        return Response(serializer.data)


# F09
@api_view(["GET"])
def book_detail(request, book_pk):
    if request.method == "GET":
        # 특정 도서 데이터 조회
        book = get_object_or_404(
            Book.objects.annotate(num_of_threads=Count("thread")),
            pk=book_pk,
        )
        # Serialization 진행
        serializer = BookDetailSerializer(book)
        # serializer 덩어리에서 데이터 추출 (.data 속성)한 것을 응답
        return Response(serializer.data)


# F10
@api_view(["GET"])
def thread_list(request):
    if request.method == "GET":
        # 전체 카테고리 데이터 조회
        threads = Thread.objects.all()
        # Serialization 진행
        serializer = ThreadListSerializer(threads, many=True)
        # serializer 덩어리에서 데이터 추출 (.data 속성)한 것을 응답
        return Response(serializer.data)


# F11
@api_view(["GET", "PUT", "DELETE"])
def thread_detail(request, thread_pk):
    thread = get_object_or_404(
        Thread.objects.annotate(num_of_comments=Count("comment")),
        pk=thread_pk,
    )
    if request.method == "GET":
        serializer = ThreadDetailSerializer(thread)
        return Response(serializer.data)

    elif request.method == "PUT":
        # 1. 사용자 입력 데이터 + 기존 댓글 데이터를 함께 직렬화
        serializer = ThreadDetailSerializer(thread, data=request.data)
        # 2. 유효성 검사
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data)

    elif request.method == "DELETE":
        pk = thread.pk
        thread.delete()
        data = {"delete": f"thread {pk} is deleted."}
        return Response(data, status=status.HTTP_204_NO_CONTENT)


# F12
@api_view(["POST"])
def create_thread(request, book_pk):
    # 1. 단일 게시글 조회
    book = Book.objects.get(pk=book_pk)
    # 2. 사용자 입력 데이터를 받아서 직렬화
    serializer = ThreadCreateSerializer(data=request.data)
    # 3. 유효성 검사
    if serializer.is_valid(raise_exception=True):
        # 4. 외래키 데이터 추가
        serializer.save(book=book)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


# F13
@api_view(["POST"])
def create_comment(request, thread_pk):
    # 1. 단일 게시글 조회
    thread = Thread.objects.get(pk=thread_pk)
    # 2. 사용자 입력 데이터를 받아서 직렬화
    serializer = CommentSerializer(data=request.data)
    # 3. 유효성 검사
    if serializer.is_valid(raise_exception=True):
        # 4. 외래키 데이터 추가
        serializer.save(thread=thread)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


@api_view(["GET", "PUT", "DELETE"])
def comment_detail(request, comment_pk):
    # 1. 단일 댓글 조회
    comment = Comment.objects.get(pk=comment_pk)
    if request.method == "GET":
        # 2. 단일 댓글 데이터를 직렬화
        serializer = CommentSerializer(comment)
        # 3. 가공된 데이터 덩어리에서 json 데이터를 추출
        return Response(serializer.data)

    elif request.method == "PUT":
        # 1. 사용자 입력 데이터 + 기존 댓글 데이터를 함께 직렬화
        serializer = CommentSerializer(comment, data=request.data)
        # 2. 유효성 검사
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data)

    elif request.method == "DELETE":
        pk = comment.pk
        comment.delete()
        data = {"message": f"comment {pk} is deleted"}
        return Response(data, status=status.HTTP_204_NO_CONTENT)

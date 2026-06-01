from rest_framework import serializers
from .models import Book, Comment, Thread, Category


class BookSerializer(serializers.ModelSerializer):

    class CommentDetailSerializer(serializers.ModelSerializer):
        class Meta:
            model = Comment
            fields = (
                "id",
                "content",
            )

    # 역참조 매니저 이름으로 응답에 제공할 필드를 재정의
    # (주의! 역참조 매니저 이름이 아니면 동작하지 않음)

    # 만약 comment_set이 아닌 다른 이름으로 사용하고 싶다면
    # models.py에서 외래키 필드에서 related_name 설정으로 변경하고,
    # 여기서도 related_name의 값으로 변경해야 한다.
    comment_set = CommentDetailSerializer(many=True, read_only=True)

    # 댓글 개수를 제공할 새로운 읽기 전용 필드를 정의
    num_of_comments = serializers.SerializerMethodField()

    class Meta:
        model = Book
        fields = "__all__"

    def get_num_of_comments(self, obj):
        # 왜 이런 함수를 호출하는 구조로 되었을까?
        # gpt의 응답 결과를 받아서 반환
        # 여러가지
        # 코드들이
        # 작성 됨
        # 그 결과를 새로운 필드에 반환 하는 구조...
        return obj.num_of_comments


class BookListSerializer(serializers.ModelSerializer):

    class Meta:
        model = Book
        fields = (
            "id",
            "title",
            "content",
        )


class CommentSerializer(serializers.ModelSerializer):
    # 게시글의 제목만 직렬화 해주는 도구
    class ThreadTitleSerializer(serializers.ModelSerializer):
        class Meta:
            model = Thread
            fields = ("title",)

    # thread 필드에 대한 데이터 재정의(덮어쓰기)
    thread = ThreadTitleSerializer(read_only=True)

    class Meta:
        model = Comment
        fields = "__all__"
        # read_only_fields = ('Book',)


#################################
class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = "__all__"


class BookListSerializer(serializers.ModelSerializer):

    class Meta:
        model = Book
        fields = (
            "id",
            "title",
            "author",
            "isbn",
            "cover",
        )


class BookDetailSerializer(serializers.ModelSerializer):
    class ThreadDetailSerializer(serializers.ModelSerializer):
        class Meta:
            model = Thread
            fields = ("id", "title", "content", "reading_date")

    threads = ThreadDetailSerializer(source="thread", many=True, read_only=True)
    num_of_threads = serializers.SerializerMethodField()
    category = CategorySerializer(read_only=True)

    class Meta:
        model = Book
        fields = (
            "id",
            "category",
            "threads",
            "num_of_threads",
            "title",
            "description",
            "isbn",
            "cover",
            "publisher",
            "pub_date",
            "author",
            "customer_review_rank",
        )

    def get_num_of_threads(self, obj):
        return obj.num_of_threads


class BookTitleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Book
        fields = ("title",)


class ThreadListSerializer(serializers.ModelSerializer):
    book = BookTitleSerializer(read_only=True)

    class Meta:
        model = Thread
        fields = (
            "id",
            "title",
            "book",
        )


class ThreadDetailSerializer(serializers.ModelSerializer):
    book = BookTitleSerializer(read_only=True)
    comments = CommentSerializer(read_only=True, many=True, source='comment_set')

    num_of_comments = serializers.SerializerMethodField()

    class Meta:
        model = Thread
        fields = "__all__"

    def get_num_of_comments(self, obj):
        return obj.num_of_comments


class ThreadCreateSerializer(serializers.ModelSerializer):
    book = BookTitleSerializer(read_only=True)
    

    class Meta:
        model = Thread
        fields = "__all__"

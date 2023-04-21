import secrets

from django.conf import settings
from django.db.models import Avg
from django_filters.rest_framework import DjangoFilterBackend
from django.core.mail import send_mail
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import filters, viewsets, status
from rest_framework.generics import get_object_or_404
from rest_framework.pagination import LimitOffsetPagination

from reviews.models import Category, Genre, Review, Title
from users.models import User
from .mixins import CreateListDestroy
from .filters import TitleFilter
from .permissions import AdminOrReadOnly, UserOrReadOnly, IsAdmin
from .serializers import (CategorySerializer, CommentSerializer,
                          GenreSerializer, ReviewSerializer,
                          TitlePostSerializer, TitleSerializer,
                          RegisterSerializer, TokenSerializer,
                          UserSerializer
                          )


class TitleViewSet(viewsets.ModelViewSet):
    queryset = Title.objects.annotate(rating=Avg('reviews__score'))
    serializer_class = TitleSerializer
    permission_classes = (AdminOrReadOnly,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = TitleFilter
    pagination_class = LimitOffsetPagination

    def get_serializer_class(self):
        if self.request.method in ('POST', 'PATCH',):
            return TitlePostSerializer
        return TitleSerializer


class GenreViewSet(CreateListDestroy):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    permission_classes = (AdminOrReadOnly,)
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)
    lookup_field = "slug"
    pagination_class = LimitOffsetPagination


class CategoryViewSet(CreateListDestroy):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = (AdminOrReadOnly,)
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)
    lookup_field = "slug"
    pagination_class = LimitOffsetPagination


class ReviewViewSet(viewsets.ModelViewSet):
    serializer_class = ReviewSerializer
    permission_classes = (UserOrReadOnly, )
    pagination_class = LimitOffsetPagination

    def get_queryset(self):
        title_id = self.kwargs.get('title_id')
        title = get_object_or_404(Title, id=title_id)
        new_queryset = title.reviews.all()
        return new_queryset

    def perform_create(self, serializer):
        title_id = self.kwargs.get('title_id')
        title = get_object_or_404(Title, id=title_id)
        serializer.save(author=self.request.user, title=title)


class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer
    permission_classes = (UserOrReadOnly, )
    pagination_class = LimitOffsetPagination

    def get_queryset(self):
        title_id = self.kwargs.get('title_id')
        review_id = self.kwargs.get('review_id')
        review = get_object_or_404(Review, id=review_id, title_id=title_id)
        new_queryset = review.comments.all()
        return new_queryset

    def perform_create(self, serializer):
        title_id = self.kwargs.get('title_id')
        review_id = self.kwargs.get('review_id')
        review = get_object_or_404(Review, id=review_id, title_id=title_id)
        serializer.save(author=self.request.user, review=review)


class APIRegister(APIView):
    permission_classes = (AllowAny,)
    serializer_user = RegisterSerializer

    def mail(self, email, confirmation_code):
        send_mail('confirmation_code',
                  f'Cохраните этот код: {confirmation_code}',
                  settings.EMAIL_HOST_USER,
                  [email],
                  fail_silently=False)

    def post(self, request):
        validate_user = self.serializer_user(data=request.data)
        if validate_user.is_valid():
            username = validate_user.data['username']
            email = validate_user.data['email']
            if User.objects.filter(email=email).exists():
                confirmation_code = secrets.token_urlsafe()
                User.objects.filter(username=username).update(
                    confirmation_code=confirmation_code, is_active=True
                )
            else:
                confirmation_code = secrets.token_urlsafe()
                User.objects.get_or_create(
                    username=username,
                    email=email,
                    confirmation_code=confirmation_code,
                )
                self.mail(email, confirmation_code)
            return Response({'email': email, 'username': username})
        return Response(
            validate_user.errors,
            status=status.HTTP_400_BAD_REQUEST
        )


class APIToken(APIView):
    permission_classes = (AllowAny,)
    serializer_token = TokenSerializer

    def post(self, request):
        validate_token = self.serializer_token(data=request.data)
        validate_token.is_valid(raise_exception=True)
        user = get_object_or_404(
            User,
            username=validate_token.data['username']
        )
        confirmation_code = validate_token.data['confirmation_code']
        if confirmation_code == user.confirmation_code:
            User.objects.filter(
                username=validate_token.data['username']
            ).update(is_active=True)
        else:
            return Response(
                {'message': 'Код не прошёл проверку!'},
                status=status.HTTP_400_BAD_REQUEST
            )
        return Response(
            {'token': User.get_token(user)},
            status=status.HTTP_200_OK
        )


class UsersViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    lookup_field = 'username'
    permission_classes = (IsAdmin,)
    filter_backends = (filters.SearchFilter,)
    search_fields = ("username",)
    http_method_names = ['get', 'post', 'head', 'patch', 'delete']

    @action(detail=False, permission_classes=(IsAuthenticated,),
            methods=['get', 'patch'])
    def me(self, request):
        if request.method == 'PATCH':
            serializer = self.get_serializer(
                instance=request.user,
                data=request.data,
                partial=True,
            )
            serializer.is_valid(raise_exception=True)
            serializer.save(role=request.user.role)
            return Response(serializer.data)
        serializer = self.get_serializer(request.user, many=False)
        return Response(serializer.data)

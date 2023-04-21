from django.shortcuts import get_object_or_404
from django.conf import settings
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from reviews.models import Category, Comment, Genre, Review, Title
from users.models import User


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        fields = (
            'first_name',
            'last_name',
            'username',
            'bio',
            'email',
            'role',
        )
        model = User
        read_only_field = ('role',)


class RegisterSerializer(serializers.Serializer):
    email = serializers.EmailField(
        required=True,
    )
    username = serializers.RegexField(
        required=True,
        max_length=150,
        regex=r"^[^\W\d]\w*$",

    )

    def validate(self, data):
        if data['username'] == settings.METANAME:
            raise serializers.ValidationError(
                'Нельзя использовать имя me в качестве имени пользователя.'
            )
        if (
                User.objects.filter(username=data.get('username'))
                and not User.objects.filter(email=data.get('email'))
        ):
            raise serializers.ValidationError(
                'Пользователь с таким username имеет другой email'
            )
        if (
            not User.objects.filter(username=data['username']).exists()
            and User.objects.filter(email=data['email']).exists()
        ):
            raise serializers.ValidationError('email уже занят!')
        return data


class TokenSerializer(serializers.Serializer):
    username = serializers.RegexField(
        required=True,
        max_length=150,
        regex=r"^[^\W\d]\w*$",
    )
    confirmation_code = serializers.CharField()

    def validate(self, data):
        if data.get('username') == settings.METANAME:
            raise serializers.ValidationError(
                'Нельзя использовать имя me в качестве имени пользователя.'
            )
        return data


class GenreSerializer(serializers.ModelSerializer):

    class Meta:
        model = Genre
        fields = ('name', 'slug',)


class CategorySerializer(serializers.ModelSerializer):

    class Meta:
        model = Category
        fields = ('name', 'slug',)


class TitleSerializer(serializers.ModelSerializer):
    genre = GenreSerializer(required=True, many=True)
    category = CategorySerializer(required=True)
    rating = serializers.IntegerField(read_only=True)

    class Meta:
        model = Title
        fields = '__all__'


class TitlePostSerializer(serializers.ModelSerializer):
    genre = serializers.SlugRelatedField(
        queryset=Genre.objects.all(),
        slug_field='slug',
        many=True
    )
    category = serializers.SlugRelatedField(
        queryset=Category.objects.all(),
        slug_field='slug'
    )

    class Meta:
        model = Title
        fields = '__all__'

    def validate_name(self, value):
        if len(value) > 256:
            raise serializers.ValidationError(
                "Название не должно превышать 256 символов."
            )
        return value


class ReviewSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        read_only=True,
        slug_field='username'
    )

    class Meta:
        fields = ('id', 'author', 'text', 'score', 'pub_date',)
        model = Review

    def validate(self, data):
        request = self.context['request']
        author = request.user
        title_id = self.context['view'].kwargs.get('title_id')
        title = get_object_or_404(Title, pk=title_id)
        if request.method == 'POST':
            if Review.objects.filter(title=title, author=author).exists():
                raise ValidationError(
                    'Можно оставить только один отзыв'
                )
        return data


class CommentSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        read_only=True, slug_field='username',
    )
    review = serializers.SlugRelatedField(
        read_only=True, slug_field='text',
    )

    class Meta:
        fields = '__all__'
        model = Comment

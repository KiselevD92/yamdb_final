from datetime import datetime

from django.core.validators import (MaxValueValidator, MinValueValidator)
from django.db import models

from users.models import User


class Genre(models.Model):
    name = models.CharField(
        max_length=256,
        verbose_name='Наименование жанра'
    )
    slug = models.SlugField(
        max_length=50,
        verbose_name='Slug',
        unique=True
    )

    def __str__(self):
        return self.name


class Category(models.Model):
    name = models.CharField(
        max_length=256,
        verbose_name='Наименование категории произведения',
    )
    slug = models.SlugField(
        max_length=50,
        verbose_name='Slug',
        unique=True
    )

    def __str__(self):
        return self.name


class Title(models.Model):
    name = models.CharField(
        max_length=256,
        verbose_name='Название произведения',
    )
    year = models.PositiveIntegerField(
        verbose_name='Год создания',
        validators=[
            MinValueValidator(
                1000,
                message='Год должен быть числом'
            ),
            MaxValueValidator(
                datetime.now().year,
                message='Год произведения не может быть больше текущего'
            )
        ]
    )
    category = models.ForeignKey(
        Category,
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name='titles',
        verbose_name='Название категории',
    )
    description = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        verbose_name='Описание произведения',
    )
    genre = models.ManyToManyField(
        Genre,
        blank=True,
        db_index=True,
        through='GenreTitle',
        related_name='titles',
        verbose_name='Название жанра',
    )
    category = models.ForeignKey(
        Category,
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name='titles',
        verbose_name='Название жанра'
    )

    def __str__(self):
        return self.name


class GenreTitle(models.Model):
    genre = models.ForeignKey(
        Genre,
        on_delete=models.CASCADE,
        verbose_name='Жанр'
    )
    title = models.ForeignKey(
        Title,
        on_delete=models.CASCADE,
        verbose_name='Произведение'
    )


class Review(models.Model):
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='reviews',
        verbose_name='Автор отзыва',
    )
    title = models.ForeignKey(
        Title,
        on_delete=models.CASCADE,
        related_name='reviews',
        verbose_name='Отзыв_произведение',
    )
    text = models.TextField(verbose_name='Текст произведения',)
    score = models.PositiveSmallIntegerField(
        default=1,
        validators=[
            MinValueValidator(1),
            MaxValueValidator(10),
        ],
        verbose_name='Рейтинг произведения',
    )
    pub_date = models.DateTimeField(
        auto_now_add=True,
        db_index=True,
        verbose_name='Дата добавления отзыва',
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['title', 'author'],
                name='unique follow'
            )
        ]


class Comment(models.Model):
    review = models.ForeignKey(
        Review,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Комментарий к отзыву',
    )
    text = models.TextField(verbose_name='Текст комментария', )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Автор комментария',
    )
    pub_date = models.DateTimeField(
        auto_now_add=True,
        db_index=True,
        verbose_name='Дата добавления комментария',
    )

    def __str__(self):
        return self.text

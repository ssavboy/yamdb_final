from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from rest_framework import serializers

from users.models import User
from users.mixins import UsernameValidatorMixin
from reviews.models import (
    Category,
    Comment,
    Genre,
    Review,
    Title
)


class UserSerializer(serializers.ModelSerializer, UsernameValidatorMixin):
    class Meta:
        model = User
        fields = (
            'username', 'email', 'first_name',
            'last_name', 'bio', 'role')


class SignUpSerializer(serializers.Serializer, UsernameValidatorMixin):
    username = serializers.CharField(max_length=settings.RESTRICT_NAME)
    email = serializers.EmailField(max_length=settings.RESTRICT_EMAIL)

    class Meta:
        model = User
        fields = ('username', 'email')


class TokenSerializer(serializers.Serializer, UsernameValidatorMixin):
    username = serializers.CharField(
        required=True, max_length=settings.RESTRICT_NAME)
    confirmation_code = serializers.CharField(required=True)

    class Meta:
        model = User
        fields = ('username', 'confirmation_code')


class CategoriesSerializer(serializers.ModelSerializer):
    """Описание сериализатора для модели Category."""

    class Meta:
        model = Category
        exclude = ('id',)
        lookup_field = 'slug'
        extra_kwargs = {
            'url': {'lookup_field': 'slug'}
        }


class GenreSerializer(serializers.ModelSerializer):
    """Описание сериализатора для модели Genre."""

    class Meta:
        model = Genre
        exclude = ('id',)
        lookup_field = 'slug'
        extra_kwargs = {
            'url': {'lookup_field': 'slug'}
        }


class TitleSerializer(serializers.ModelSerializer):
    """Описание сериализатора для модели Title."""

    genre = serializers.SlugRelatedField(many=True, slug_field='slug',
                                         queryset=Genre.objects.all())
    category = serializers.SlugRelatedField(slug_field='slug',
                                            queryset=Category.objects.all())

    class Meta:
        model = Title
        fields = '__all__'

    def to_representation(self, instance):
        return ReadOnlyTitleSerializer(instance).data


class ReadOnlyTitleSerializer(serializers.ModelSerializer):
    """Описание сериализатора для 'list' и 'retrieve'"""
    rating = serializers.IntegerField(read_only=True)
    genre = GenreSerializer(many=True)
    category = CategoriesSerializer()

    class Meta:
        model = Title
        fields = '__all__'
        read_only_fields = ('__all__',)


class ReviewSerializer(serializers.ModelSerializer):
    """Описание сериализатора для модели Review."""

    author = serializers.SlugRelatedField(
        slug_field='username',
        read_only=True,
        default=serializers.CurrentUserDefault()
    )
    score = serializers.IntegerField(
        validators=[
            MinValueValidator(settings.MIN_SCORE_VALUE),
            MaxValueValidator(settings.MAX_SCORE_VALUE),
        ]
    )

    class Meta:
        model = Review
        fields = '__all__'
        read_only_fields = ('title',)

    def validate(self, data):
        """Проверка существования произведения."""
        if self.context['request'].method == 'POST':
            title_id = self.context['view'].kwargs.get('title_id')
            author = self.context['request'].user
            if Review.objects.filter(title=title_id, author=author).exists():
                raise serializers.ValidationError(
                    'Можно написать только одну рецензию на произведение.'
                )
        return data


class CommentSerializer(serializers.ModelSerializer):
    """Описание сериализатора для модели Comment."""

    author = serializers.SlugRelatedField(
        slug_field='username',
        read_only=True,
        default=serializers.CurrentUserDefault()
    )

    class Meta:
        model = Comment
        fields = '__all__'
        read_only_fields = ('review',)

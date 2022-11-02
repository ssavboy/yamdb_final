from django.conf import settings
from django.contrib.auth.tokens import default_token_generator
from django.db import IntegrityError
from django.core.mail import send_mail
from django.db.models import Avg
from django.shortcuts import get_object_or_404
from rest_framework import viewsets, filters
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import AccessToken
from rest_framework.views import APIView
from rest_framework.serializers import ValidationError

from .serializers import CategoriesSerializer, CommentSerializer
from .serializers import GenreSerializer, TitleSerializer
from .serializers import ReviewSerializer, ReadOnlyTitleSerializer
from .serializers import SignUpSerializer, TokenSerializer, UserSerializer
from reviews.models import Category, Genre, Title, Review
from .permissions import IsAuthorModeratorAdminOrReadOnly
from .permissions import IsAdminOrReadOnly
from .permissions import IsAdmin
from .filters import TitlesFilter
from .mixins import ListCreateDestroyViewSet
from users.models import User


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    permission_classes = (IsAdmin,)
    serializer_class = UserSerializer
    search_fields = ('username',)
    lookup_field = 'username'

    @action(
        detail=False,
        methods=('GET', 'PATCH'),
        permission_classes=(IsAuthenticated,))
    def me(self, request):
        serializer = UserSerializer(request.user)
        if request.method == 'PATCH':
            serializer = UserSerializer(
                request.user,
                data=request.data,
                partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save(role=request.user.role)
        return Response(serializer.data)


class SignUpView(APIView):
    def post(self, request):
        serializer = SignUpSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data.get('email')
        username = serializer.validated_data.get('username')
        try:
            user, is_created = User.objects.get_or_create(
                email=email,
                username=username)
        except IntegrityError:
            raise ValidationError(detail='Username или Email уже занят.')
        confirmation_code = default_token_generator.make_token(user)
        send_mail(
            subject='Ваш код под подтверждения: ',
            message=f'Код подтверждения - "{confirmation_code}".',
            from_email=settings.FROM_EMAIL,
            recipient_list=(email,))
        return Response(
            {'email': email, 'username': username},
            status=status.HTTP_200_OK)


class TokenView(APIView):
    permission_classes = (AllowAny,)

    def post(self, request):
        serializer = TokenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        confirmation_code = serializer.validated_data.get('confirmation_code')
        username = serializer.validated_data.get('username')
        user = get_object_or_404(User, username=username)

        if default_token_generator.check_token(user, confirmation_code):
            user.is_active = True
            user.save()
            token = AccessToken.for_user(user)
            return Response({'token': f'{token}'}, status=status.HTTP_200_OK)

        return Response(
            {'confirmation_code': ['Invalid token!']},
            status=status.HTTP_400_BAD_REQUEST)


class GenreViewSet(ListCreateDestroyViewSet):
    """Вьюсет для запросов к объектам Genre."""

    queryset = Genre.objects.all()
    serializer_class = GenreSerializer


class CategoriesViewSet(ListCreateDestroyViewSet):
    """Вьюсет для запросов к объектам Category."""

    queryset = Category.objects.all()
    serializer_class = CategoriesSerializer


class TitleViewSet(viewsets.ModelViewSet):
    """Вьюсет для запросов к объектам Title."""

    queryset = Title.objects.all().annotate(rating=Avg('reviews__score'))
    serializer_class = TitleSerializer
    permission_classes = (IsAdminOrReadOnly,)
    filterset_class = (filters.OrderingFilter,)
    ordering_fields = ('name',)
    filterset_class = TitlesFilter

    def get_serializer_class(self):
        if self.action in ('retrieve', 'list'):
            return ReadOnlyTitleSerializer
        return TitleSerializer


class ReviewViewSet(viewsets.ModelViewSet):
    """Вьюсет для запросов к объектам Review."""

    serializer_class = ReviewSerializer
    permission_classes = (
        IsAuthorModeratorAdminOrReadOnly,
    )

    def get_title(self):
        """Определение объекта Title, связанного с Review."""
        return get_object_or_404(Title, pk=self.kwargs.get('title_id'))

    def get_queryset(self):
        """Определение множества объектов Review."""
        return self.get_title().reviews.all()

    def perform_create(self, serializer):
        """Переопределение метода создания объекта Review."""
        serializer.save(
            author=self.request.user,
            title=self.get_title()
        )


class CommentViewSet(viewsets.ModelViewSet):
    """Вьюсет для запросов к объектам Comment."""

    serializer_class = CommentSerializer
    permission_classes = (
        IsAuthorModeratorAdminOrReadOnly,
    )

    def get_review(self):
        """Определение объекта Review, связанного с Comment."""

        return get_object_or_404(
            Review,
            pk=self.kwargs.get('review_id')
        )

    def get_queryset(self):
        """Определение множества объектов Comment."""
        return self.get_review().comments.all()

    def perform_create(self, serializer):
        """Переопределение метода создания объекта Comment."""
        serializer.save(
            author=self.request.user,
            review=self.get_review()
        )

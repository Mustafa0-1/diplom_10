from django.db import transaction
from django.db.models import QuerySet
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, permissions
from rest_framework.generics import CreateAPIView, ListAPIView, RetrieveUpdateDestroyAPIView

from todolist.goals.filters import GoalDateFilter
from todolist.goals.models import GoalCategory, Goal, GoalComment, BoardParticipant, Board
from todolist.goals.permissions import BoardPermissions, GoalCategoryPermissions, GoalPermissions, \
    GoalCommentsPermissions
from todolist.goals.serializers import GoalCategoryCreateSerializer, GoalCategorySerializer, GoalCreateSerializer, \
    GoalSerializer, GoalCommentCreateSerializer, GoalCommentSerializer, BoardCreateSerializer, BoardSerializer


class BoardCreateView(CreateAPIView):
    """Ручка для создания доски"""
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = BoardCreateSerializer

    def perform_create(self, serializer):
        """Метод создает из базы querysetи и сохраняет список досок"""
        BoardParticipant.objects.create(user=self.request.user, board=serializer.save())


class BoardListView(ListAPIView):
    """Ручка для отображения списка досок"""
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = BoardCreateSerializer
    filter_backends = [filters.OrderingFilter]
    ordering = ['title']

    def get_queryset(self):
        """Метод возвращает из базы queryset список досок"""
        return Board.objects.filter(
            participants__user_id=self.request.user.id,
            is_deleted=False
        )


class BoardView(RetrieveUpdateDestroyAPIView):
    """Ручка для отображения, редактирования и удаления доски"""
    permission_classes = [BoardPermissions]
    serializer_class = BoardSerializer

    def get_queryset(self):
        """Метод возвращает из базы queryset доски"""
        return Board.objects.filter(is_deleted=False)

    def perform_destroy(self, instance: Board) -> None:
        """
        Метод удаляет доску
        При удалении доски помечаем ее как is_deleted,
        "удаляем" категории, обновляем статус целей.
        """
        with transaction.atomic():
            instance.is_deleted = True
            instance.save(update_fields=('is_deleted',))
            instance.categories.update(is_deleted=True)
            Goal.objects.filter(category__board=instance).update(status=Goal.Status.archived)


class GoalCategoryCreateView(CreateAPIView):
    """Ручка для создания категории"""
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = GoalCategoryCreateSerializer


class GoalCategoryListView(ListAPIView):
    """Ручка для отображения списка категорий"""
    permission_classes = [GoalCategoryPermissions]
    serializer_class = GoalCategorySerializer
    filter_backends = [filters.OrderingFilter, filters.SearchFilter, ]
    ordering_fields = ['title', 'created']
    ordering = ['title']
    search_fields = ['title']

    def get_queryset(self):
        """Метод возвращает из базы queryset списка категорий"""
        return GoalCategory.objects.filter(
            user_id=self.request.user.id,
            is_deleted=False
        )


class GoalCategoryView(RetrieveUpdateDestroyAPIView):
    """Ручка для отображения, редактирования и удаления категории"""
    serializer_class = GoalCategorySerializer
    permission_classes = [GoalCategoryPermissions]

    def get_queryset(self):
        """Метод возвращает из базы queryset списка категорий"""
        return GoalCategory.objects.filter(
            user_id=self.request.user.id,
            is_deleted=False
        )

    def perform_destroy(self, instance: GoalCategory):
        """Метод удаляет категорию, а у всех целей в этой категории меняет статус на архивный"""
        with transaction.atomic():
            instance.is_deleted = True
            instance.save(update_fields=('is_deleted',))
            instance.goals.update(status=Goal.Status.archived)


class GoalCreateView(CreateAPIView):
    """Ручка для создания цели"""
    permission_classes = [GoalPermissions]
    serializer_class = GoalCreateSerializer


class GoalListView(ListAPIView):
    """Ручка для отображения списка целей"""
    permission_classes = [GoalPermissions]
    serializer_class = GoalSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter, filters.SearchFilter]
    filterset_class = GoalDateFilter
    ordering_fields = ['title', 'created']
    ordering = ['title']
    search_fields = ['title', 'description']

    def get_queryset(self) -> QuerySet[Goal]:
        """Метод возвращает из базы queryset списка целей"""
        return Goal.objects.filter(
            category__board__participants__user=self.request.user.id,
            category__is_deleted=False
        ).exclude(status=Goal.Status.archived)


class GoalView(RetrieveUpdateDestroyAPIView):
    """Ручка для отображения, редактирования и удаления цели"""
    permission_classes = [permissions.IsAuthenticated, GoalPermissions]
    serializer_class = GoalSerializer

    def get_queryset(self) -> QuerySet[Goal]:
        """Метод возвращает из базы queryset цели"""
        return (
            Goal.objects
            .filter(category__board__participants__user=self.request.user.id, category__is_deleted=False)
            .exclude(status=Goal.Status.archived)
        )

    def perform_destroy(self, instance: Goal) -> None:
        """Метод меняет статус цели как архивный"""
        instance.status = Goal.Status.archived
        instance.save(update_fields=('status',))


class GoalCommentCreateView(CreateAPIView):
    """Ручка для создания комментария"""
    serializer_class = GoalCommentCreateSerializer
    permission_classes = [GoalCommentsPermissions]


class GoalCommentListView(ListAPIView):
    """Ручка для отображения списка комментариев"""
    permission_classes = [GoalCommentsPermissions]
    serializer_class = GoalCommentSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['goal']
    ordering = ['-created']

    def get_queryset(self):
        """Метод возвращает из базы queryset списка комментариев"""
        return GoalComment.objects.filter(goal__category__board__participants__user_id=self.request.user.id)


class GoalCommentView(RetrieveUpdateDestroyAPIView):
    """Ручка для отображения, редактирования и удаления комментария"""
    permission_classes = [GoalCommentsPermissions]
    serializer_class = GoalCommentSerializer

    def get_queryset(self):
        """Метод возвращает из базы queryset комментарии"""
        return GoalComment.objects.select_related('user').filter(user_id=self.request.user.id)

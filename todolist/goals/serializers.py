from django.db import transaction
from django.utils.datetime_safe import date
from rest_framework import serializers
from rest_framework.exceptions import PermissionDenied, ValidationError

from todolist.core.models import User
from todolist.core.serializers import ProfileSerializer
from todolist.goals.models import GoalCategory, Goal, Board, GoalComment, BoardParticipant


class GoalCategoryCreateSerializer(serializers.ModelSerializer):
    """Класс модели сериализатора для создания категории целей"""
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        """Мета-класс для указания модели для сериализатора, полей модели сериализатора, и не изменяемых полей"""
        model = GoalCategory
        read_only_fields = ('id', 'created', 'updated', 'user', 'is_deleted')
        fields = '__all__'


class GoalCategorySerializer(serializers.ModelSerializer):
    """Класс модели сериализатора категории целей"""
    user = ProfileSerializer(read_only=True)

    class Meta:
        """Мета-класс для указания модели для сериализатора, полей модели сериализатора, и не изменяемых полей"""
        model = GoalCategory
        fields = '__all__'
        read_only_fields = ('id', 'created', 'updated', 'user', 'board')

    def validated_board(self, value: Board):
        """
        Метод для валидации данных доски. Метод проверяет не удалена ли доска
        и является ли пользователь участником с ролью owner или writer
        """
        if value.is_deleted:
            raise serializers.ValidationError('Not allowed to delete category')
        if not BoardParticipant.objects.filter(
                board=value,
                role__in=[BoardParticipant.Role.owner, BoardParticipant.Role.writer],
                user_id=self.context['request'].user.id
        ).exists():
            raise serializers.ValidationError('You must be owner or writer')
        return value


class GoalCreateSerializer(serializers.ModelSerializer):
    """Класс модели сериализатора для создания цели"""
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        """Мета-класс для указания модели для сериализатора, полей модели сериализатора, и не изменяемых полей"""
        model = Goal
        fields = '__all__'
        read_only_fields = ('id', 'created', 'updated', 'user')

    def validate_category(self, value: GoalCategory) -> GoalCategory:
        """
        Метод для валидации данных категории целей. Метод проверяет, является ли
        пользователь создателем категории, или является ли он участником доски с этой
        категорией в роли writer
        """
        if value.is_deleted:
            raise ValidationError('Category not found')
        if self.context['request'].user.id != value.user_id:
            raise PermissionDenied
        return value

    def validate_due_date(self, value: date) -> date:
        # if value and value < timezone.now().date():
        #     raise ValidationError('Failed to set due date in the past')
        return value


class GoalSerializer(serializers.ModelSerializer):
    """Класс модели сериализатора цели"""
    user = ProfileSerializer(read_only=True)

    class Meta:
        """Мета-класс для указания модели для сериализатора, полей модели сериализатора, и не изменяемых полей"""
        model = Goal
        fields = '__all__'
        read_only_fields = ('id', 'created', 'updated', 'user')

    def validate_category(self, value: GoalCategory) -> GoalCategory:
        """
        Метод для валидации данных категории целей.
        Метод проверяет, является ли пользователь создателем категории целей
        """
        if value.is_deleted:
            raise ValidationError('Category not found')
        if self.context['request'].user.id != value.user_id:
            raise PermissionDenied
        return value


class GoalCommentCreateSerializer(serializers.ModelSerializer):
    """Класс модели сериализатора для создания комментария"""
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())

    def validate_goal(self, value: Goal) -> Goal:
        if value.status == Goal.Status.archived:
            raise ValidationError('Goal not found')
        if not BoardParticipant.objects.filter(
            board_id=value.category.board_id,
            role__in=[BoardParticipant.Role.owner, BoardParticipant.Role.writer],
            user_id=self.context['request'].user.id
        ).exists():
            raise PermissionDenied
        return value

    class Meta:
        """Мета-класс для указания модели для сериализатора, полей модели сериализатора, и не изменяемых полей"""
        model = GoalComment
        fields = '__all__'
        read_only_fields = ('id', 'created', 'updated', 'user')


class GoalCommentSerializer(serializers.ModelSerializer):
    """Класс модели сериализатора комментария"""
    user = ProfileSerializer(read_only=True)

    def validate_goal(self, value: Goal) -> Goal:
        if value.status == Goal.Status.archived:
            raise ValidationError('Goal not found')
        if self.context['request'].user.id != value.user.id:
            raise PermissionDenied
        return value

    class Meta:
        """Мета-класс для указания модели для сериализатора, полей модели сериализатора, и не изменяемых полей"""
        model = GoalComment
        fields = '__all__'
        read_only_fields = ('id', 'created', 'updated', 'user', 'goal')


class BoardCreateSerializer(serializers.ModelSerializer):
    """Класс модели сериализатора для создания новой доски"""
    class Meta:
        """Мета-класс для указания модели для сериализатора, полей модели сериализатора, и не изменяемых полей"""
        model = Board
        read_only_fields = ('id', 'created', 'updated', 'is_deleted')
        fields = '__all__'


class BoardParticipantSerializer(serializers.ModelSerializer):
    """Класс модели сериализатора участников доски"""
    role = serializers.ChoiceField(required=True, choices=BoardParticipant.Role.choices[1:])
    user = serializers.SlugRelatedField(slug_field='username', queryset=User.objects.all())

    class Meta:
        """Мета-класс для указания модели для сериализатора, полей модели сериализатора, и не изменяемых полей"""
        model = BoardParticipant
        fields = '__all__'
        read_only_fields = ('id', 'created', 'updated', 'board')


class BoardSerializer(serializers.ModelSerializer):
    """Класс модели сериализатора доски"""
    participants = BoardParticipantSerializer(many=True)

    class Meta:
        """Мета-класс для указания модели для сериализатора, полей модели сериализатора, и не изменяемых полей"""
        model = Board
        fields = '__all__'
        read_only_fields = ('id', 'created', 'updated', 'is_deleted')

    def update(self, instance: Board, validated_data: dict) -> Board:
        """Метод для редактирования и добавления участников доски"""
        with transaction.atomic():
            BoardParticipant.objects.filter(board=instance).exclude(user=self.context['request'].user).delete()
            BoardParticipant.objects.bulk_create([
                BoardParticipant(
                    user=participant['user'],
                    role=participant['role'],
                    board=instance
                )
                for participant in validated_data.get('participants', [])
            ])

            if title := validated_data.get('title'):
                instance.title = title
                instance.save(update_fields=('title',))

            return instance

from rest_framework import permissions

from todolist.goals.models import BoardParticipant, Board, GoalCategory, Goal, GoalComment


class BoardPermissions(permissions.IsAuthenticated):
    """Класс permission для доски"""
    def has_object_permission(self, request, view, obj: Board):
        """
        Метод проверяет авторизацию пользователя и если метод из списка SAFE_METHODS,
        то метод проверяет, является ли пользователь участником доски. Также метод проверяет,
        является ли пользователь создателем доски для редактирования или удаления
        """
        _filters: dict = {'user_id': request.user.id, 'board_id': obj.id}

        if request.method not in permissions.SAFE_METHODS:
            _filters['role'] = BoardParticipant.Role.owner

        return BoardParticipant.objects.filter(**_filters).exists()


class GoalCategoryPermissions(permissions.IsAuthenticated):
    """Класс permission категорий"""
    def has_object_permission(self, request, view, obj: GoalCategory):
        """
        Метод проверяет авторизацию пользователя и если метод из списка SAFE_METHODS,
        то метод проверяет, является ли пользователь участником доски. Также метод проверяет,
        является ли пользователь создателем или участником доски с ролью редактор(writer)
        для редактирования или удаления категории
        """
        _filters: dict = {'user_id': request.user.id, 'board_id': obj.board_id}

        if request.method not in permissions.SAFE_METHODS:
            _filters['role__in'] = [BoardParticipant.Role.owner, BoardParticipant.Role.writer]

        return BoardParticipant.objects.filter(**_filters).exists()


class GoalPermissions(permissions.IsAuthenticated):
    """Класс permission целей"""
    def has_object_permission(self, request, view, obj: Goal):
        """
        Метод проверяет авторизацию пользователя и если метод из списка SAFE_METHODS,
        то метод проверяет, является ли пользователь участником доски. Также метод проверяет,
        является ли пользователь создателем или участником доски с ролью редактор(writer)
        для редактирования или удаления цели
        """
        _filters: dict = {'user_id': request.user.id, 'board_id': obj.category.board_id}

        if request.method not in permissions.SAFE_METHODS:
            _filters['role__in'] = [BoardParticipant.Role.owner, BoardParticipant.Role.writer]

        return BoardParticipant.objects.filter(**_filters).exists()


class GoalCommentsPermissions(permissions.IsAuthenticated):
    """Класс permission для комментария"""
    def has_object_permission(self, request, view, obj: GoalComment):
        """
        Метод проверяет авторизацию пользователя и что пользователь является создателем комментария
        """
        return any((
            request.method in permissions.SAFE_METHODS,
            obj.user_id == request.user.id
        ))

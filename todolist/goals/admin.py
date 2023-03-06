from django.contrib import admin

from todolist.goals.models import GoalCategory, Goal, GoalComment


@admin.register(GoalCategory)
class GoalCategoryAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'created', 'updated')
    search_fields = ('title',)


@admin.register(Goal)
class GoalAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'created', 'updated')
    search_fields = ('title', 'description')


@admin.register(GoalComment)
class GoalCommentsAdmin(admin.ModelAdmin):
    list_display = ('text', 'user', 'created', 'updated')
    search_fields = ('text',)

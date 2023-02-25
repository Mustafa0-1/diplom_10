from django.contrib import admin

from todolist.goals.models import GoalCategory


class GoalCategoryAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'created', 'updated')
    search_fields = ('title',)


admin.site.register(GoalCategory, GoalCategoryAdmin)

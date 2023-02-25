from django.urls import path

from todolist.core.views import SignupView

urlpatterns = [
    path('signup', SignupView.as_view(), name='signup'),
]

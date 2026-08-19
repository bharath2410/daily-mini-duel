from django.urls import path
from . import views

app_name = 'duel'

urlpatterns = [
    path('', views.home_view, name='home'),
    path('play/', views.play_view, name='play'),
    path('submit/', views.submit_attempt, name='submit'),
    path('result/<int:attempt_id>/', views.result_view, name='result'),
]
from django.urls import path
from . import views

urlpatterns = [
    path('cadastro/', views.cadastro, name='cadastro'),
    path('login/', views.login, name='login'),
    path('questoes/', views.questoes, name='questoes'),
    path('conteudos/', views.conteudos, name='conteudos'),
    path('ranking/', views.ranking, name='ranking'),
    path('sobre/', views.sobre, name='sobre'),
    path('logout/', views.logout_view, name='logout'),
]
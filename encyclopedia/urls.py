from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("wiki/<str:title>", views.page, name="page"),
    path("random-page", views.random_page, name="random-page"),
    path("new/", views.new_page, name="new-page"),
    path("new/<str:title>", views.new_page, name="new-page"),
    path("edit/", views.edit_page, name="edit-page"),
    path("edit/<str:title>", views.edit_page, name="edit-page"),
    path("search", views.search, name="search")
]
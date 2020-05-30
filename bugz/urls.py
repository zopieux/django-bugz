from django.urls import path

from bugz import views

app_name = "bugz"

urlpatterns = [
    path("", views.ListTicketView.as_view(), name="home"),
    path("new", views.CreateTicketView.as_view(), name="new"),
    path("ticket/<int:pk>", views.DetailTicketView.as_view(), name="ticket"),
    path("ticket/<int:pk>/comment", views.CommentTicketView.as_view(), name="comment"),
]

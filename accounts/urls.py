from django.urls import include, path
from knox import views as knox_views

from .views import LoginView

urlpatterns = [
    path("login/", LoginView.as_view(), name="knox_login"),
    path("logout/", knox_views.LogoutView.as_view(), name="knox_logout"),
    path("logoutall/", knox_views.LogoutAllView.as_view(), name="knox_logoutall"),
    path("browsable-api-auth/", include("rest_framework.urls")),
]

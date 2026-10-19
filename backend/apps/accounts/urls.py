from django.urls import path
from rest_framework.routers import DefaultRouter

from apps.accounts.views import (
    InvitationViewSet,
    LoginView,
    RefreshView,
    RegisterView,
    accept_invitation,
    invitation_preview,
    me_view,
)

router = DefaultRouter()
router.register("invitations", InvitationViewSet, basename="invitations")

urlpatterns = [
    path("login/", RefreshView.as_view(), name="login"),
    path("refresh/", RefreshView.as_view(), name="refresh"),
    path("register/", RegisterView.as_view(), name="register"),
    path("me/", me_view, name="me"),
    path("invitations/accept/", accept_invitation, name="accept-invitation"),
    path("invitations/preview/<uuid:token>/", invitation_preview, name="invitation-preview"),
] + router.urls

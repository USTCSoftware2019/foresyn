from django.urls import path
from django.views.generic import TemplateView

from . import views

app_name = 'accounts'
urlpatterns = [
    path('signup/', views.UserSignUp.as_view(), name='signup'),
    path('signup/done', TemplateView.as_view(template_name="accounts/signup_done.html"), name="signup_done"),
    path('activate/<str:uidb64>/<str:token>', views.UserActivation.as_view(), name='activate'),
    path('profile/', views.UserProfile.as_view(), name='profile'),
    # path('guide/', TemplateView.as_view(template_name="accounts/guide_book.html"), name="guide"),
    path('pack/', views.UserPack.as_view(), name='pack')
]

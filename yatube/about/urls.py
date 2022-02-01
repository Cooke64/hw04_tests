from django.urls import path
from .views import AboutTechView, AboutAuthorView

app_name = 'about'

urlpatterns = [
    path('author/', AboutAuthorView.as_view(), name='author'),
    path('tech/', AboutTechView.as_view(), name='tech'),
]

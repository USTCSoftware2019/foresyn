"""bigg_database URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path

from . import views

app_name = 'bigg_database'
urlpatterns = [
    path('admin/', admin.site.urls),
    path('search/reaction', views.ReactionSearchView.as_view(),
         name='search_reaction'),
    path('search/metabolite', views.MetaboliteSearchView.as_view(),
         name='search_metabolite'),
    path('search/model', views.ModelSearchView.as_view(),
         name='search_model'),
    path('model/<int:pk>', views.ModelDetailView.as_view(),
         name='model_detail'),
    path('reaction/<int:pk>', views.ReactionDetailView.as_view(),
         name='reaction_detail'),
    path('metabolite/<int:pk>', views.MetaboliteDetailView.as_view(),
         name='metabolite_detail'),
]

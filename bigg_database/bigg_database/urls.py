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
urlpatterns = [
    path('admin/', admin.site.urls),
    path('search/reaction/id', views.GetReactionFromId.as_view(),
         name='search_reaction_by_id'),
    path('search/metabolite/id', views.GetMetaboliteFromId.as_view(),
         name='search_metabolite_by_id'),
    path('search/model/id', views.GetModelFromId.as_view(),
         name='search_model_by_id'),
    path('search/reaction/name', views.GetReactionFromName.as_view(),
         name='search_reaction_by_name'),
    path('search/metabolite/name', views.GetMetaboliteFromName.as_view(),
         name='search_metabolite_by_name')
]

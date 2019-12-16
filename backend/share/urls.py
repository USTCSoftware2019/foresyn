from django.urls import path

from . import views

app_name = 'share'
urlpatterns = [
    path('create/', views.CreateShareLinkView.as_view(), name='create_share'),
    path('model/<int:pk>', views.ModelShareView.as_view(), name='shared_cobra_model'),
    path('addToModel/', views.AddToMyModel.as_view(), name='add_to_model')
    # path('reaction/<int:pk>', views.ReactionShareView.as_view(), name='shared_cobra_reaction'),
    # path('metabolite/<int:pk>', views.MetaboliteShareView.as_view(), name='shared_cobra_metabolite'),
]

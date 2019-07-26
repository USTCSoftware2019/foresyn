from django.urls import path

from . import views

app_name = 'cobra'
urlpatterns = [
    path('metabolites/', views.CobraMetaboliteSetApi.as_view(), name='metabolite_set'),
    path('metabolites/<int:metabolite_id>/', views.CobraMetaboliteObjectApi.as_view(), name='metabolite_object'),
    path('reactions/', views.CobraReactionSetApi.as_view(), name='reaction_set'),
    path('reactions/<int:reaction_id>/', views.CobraReactionObjectApi.as_view(), name='reaction_object'),
    path('models/', views.CobraModelSetApi.as_view(), name='model_set'),
    path('models/<int:model_id>/', views.CobraModelObjectApi.as_view(), name='model_object'),
    path(
        'models/<int:model_id>/<str:method>/',
        views.CobraModelObjectComputeApi.as_view(),
        name='model_object_computation'
    ),
]

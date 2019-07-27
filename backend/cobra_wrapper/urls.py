from django.urls import path

from . import api, views

ENABLE_API = False

app_name = 'cobra'
urlpatterns = [
    *([
        path('api/metabolites/', api.CobraMetaboliteSetApi.as_view(), name='api_metabolite_set'),
        path('api/metabolites/<int:model_id>/', api.CobraMetaboliteObjectApi.as_view(), name='api_metabolite_object'),
        path('api/reactions/', api.CobraReactionSetApi.as_view(), name='api_reaction_set'),
        path('api/reactions/<int:model_id>/', api.CobraReactionObjectApi.as_view(), name='api_reaction_object'),
        path('api/models/', api.CobraModelSetApi.as_view(), name='api_model_set'),
        path('api/models/<int:model_id>/', api.CobraModelObjectApi.as_view(), name='api_model_object'),
        path(
            'api/models/<int:model_id>/<str:method>/',
            api.CobraModelObjectComputeApi.as_view(),
            name='api_model_object_computation'
        )
    ] if ENABLE_API else []),
    path('metabolites/', views.CobraMetaboliteSetView.as_view(), name='metabolite_set'),
    path('metabolites/<int:model_id>/', views.CobraMetaboliteObjectView.as_view(), name='metabolite_object'),
    path('reactions/', views.CobraReactionSetView.as_view(), name='reaction_set'),
    path('reactions/<int:model_id>/', views.CobraReactionObjectView.as_view(), name='reaction_object'),
    path('models/', views.CobraModelSetView.as_view(), name='model_set'),
    path('models/<int:model_id>/', views.CobraModelObjectView.as_view(), name='model_object'),
    # path(
    #     'models/<int:model_id>/<str:method>/',
    #     views.CobraModelObjectComputeApi.as_view(),
    #     name='model_object_computation'
    # ),
]

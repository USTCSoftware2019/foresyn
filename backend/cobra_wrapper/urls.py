from django.urls import path

from . import api, views

ENABLE_API = False

app_name = 'cobra_wrapper'
urlpatterns = [
    *([
        path('api/metabolites/', api.CobraMetaboliteListApi.as_view(), name='api_metabolite_list'),
        path('api/metabolites/<int:pk>/', api.CobraMetaboliteDetailApi.as_view(), name='api_metabolite_detail'),
        path('api/reactions/', api.CobraReactionListApi.as_view(), name='api_reaction_list'),
        path('api/reactions/<int:pk>/', api.CobraReactionDetailApi.as_view(), name='api_reaction_detail'),
        path('api/models/', api.CobraModelListApi.as_view(), name='api_model_list'),
        path('api/models/<int:pk>/', api.CobraModelDetailApi.as_view(), name='api_model_detail'),
        path(
            'api/models/<int:pk>/<str:method>/',
            api.CobraModelDetailComputeApi.as_view(),
            name='api_model_detail_computation'
        )
    ] if ENABLE_API else []),
    path('metabolites/', views.CobraMetaboliteListView.as_view(), name='metabolite_list'),
    path('metabolites/<int:pk>/', views.CobraMetaboliteDetailView.as_view(), name='metabolite_detail'),
    path('reactions/', views.CobraReactionListView.as_view(), name='reaction_list'),
    path('reactions/<int:pk>/', views.CobraReactionDetailView.as_view(), name='reaction_detail'),
    path('models/', views.CobraModelListView.as_view(), name='model_list'),
    path('models/<int:pk>/', views.CobraModelDetailView.as_view(), name='model_detail'),
    # path(
    #     'models/<int:pk>/<str:method>/',
    #     views.CobraModelDetailComputeApi.as_view(),
    #     name='model_detail_computation'
    # ),
]

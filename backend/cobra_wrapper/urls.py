from django.urls import path

from . import views

app_name = 'cobra_wrapper'
urlpatterns = [
    path('metabolites/', views.CobraMetaboliteListView.as_view(), name='cobrametabolite_list'),
    path('metabolites/<int:pk>/', views.CobraMetaboliteDetailView.as_view(), name='cobrametabolite_detail'),
    path('metabolites/create/', views.CobraMetaboliteCreateView.as_view(), name='cobrametabolite_create_form'),
    path(
        'metabolites/<int:pk>/delete/',
        views.CobraMetaboliteCreateView.as_view(),
        name='cobrametabolite_confirm_delete'
    ),
    path(
        'metabolites/<int:pk>/update/',
        views.CobraMetaboliteCreateView.as_view(),
        name='cobrametabolite_update_form'
    ),

    path('reactions/', views.CobraReactionListView.as_view(), name='cobrareaction_list'),
    path('reactions/<int:pk>/', views.CobraReactionDetailView.as_view(), name='cobrareaction_detail'),
    path('reactions/create/', views.CobraReactionCreateView.as_view(), name='cobrareaction_create_form'),
    path(
        'reactions/<int:pk>/delete/',
        views.CobraReactionDeleteView.as_view(),
        name='cobrametabolite_confirm_delete'
    ),
    path(
        'reactions/<int:pk>/update/',
        views.CobraReactionUpdateView.as_view(),
        name='cobrametabolite_update_form'
    ),

    path('models/', views.CobraModelListView.as_view(), name='cobramodel_list'),
    path('models/<int:pk>/', views.CobraModelDetailView.as_view(), name='cobramodel_detail'),
    path('models/create/', views.CobraModelCreateView.as_view(), name='cobramodel_create_form'),
    path(
        'models/<int:pk>/delete/',
        views.CobraModelDeleteView.as_view(),
        name='cobrametabolite_confirm_delete'
    ),
    path(
        'models/<int:pk>/update/',
        views.CobraModelUpdateView.as_view(),
        name='cobrametabolite_update_form'
    ),
    # path(
    #     'models/<int:pk>/<str:method>/',
    #     views.CobraModelDetailComputeView.as_view(),
    #     name='cobramodel_detail_computation'
    # ),
]

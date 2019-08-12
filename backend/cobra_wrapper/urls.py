from django.urls import path

from . import views

app_name = 'cobra_wrapper'
urlpatterns = [
    path('metabolites/', views.CobraMetaboliteListView.as_view(), name='cobrametabolite_list'),
    path('metabolites/<int:pk>/', views.CobraMetaboliteDetailView.as_view(), name='cobrametabolite_detail'),
    path('metabolites/create/', views.CobraMetaboliteCreateView.as_view(), name='cobrametabolite_create_form'),
    path(
        'metabolites/<int:pk>/delete/',
        views.CobraMetaboliteDeleteView.as_view(),
        name='cobrametabolite_confirm_delete'
    ),
    path(
        'metabolites/<int:pk>/update/',
        views.CobraMetaboliteUpdateView.as_view(),
        name='cobrametabolite_update_form'
    ),

    path('reactions/', views.CobraReactionListView.as_view(), name='cobrareaction_list'),
    path('reactions/<int:pk>/', views.CobraReactionDetailView.as_view(), name='cobrareaction_detail'),
    path('reactions/create/', views.CobraReactionCreateView.as_view(), name='cobrareaction_create_form'),
    path(
        'reactions/<int:pk>/delete/',
        views.CobraReactionDeleteView.as_view(),
        name='cobrareaction_confirm_delete'
    ),
    path(
        'reactions/<int:pk>/update/',
        views.CobraReactionUpdateView.as_view(),
        name='cobrareaction_update_form'
    ),

    path('models/', views.CobraModelListView.as_view(), name='cobramodel_list'),
    path('models/<int:pk>/', views.CobraModelDetailView.as_view(), name='cobramodel_detail'),
    path('models/create/', views.CobraModelCreateView.as_view(), name='cobramodel_create_form'),
    path(
        'models/<int:pk>/delete/',
        views.CobraModelDeleteView.as_view(),
        name='cobramodel_confirm_delete'
    ),
    path(
        'models/<int:pk>/update/',
        views.CobraModelUpdateView.as_view(),
        name='cobramodel_update_form'
    ),

    path('models/<int:model_pk>/fba/', views.CobraFbaListView.as_view(), name='cobrafba_list'),
    path('models/<int:model_pk>/fba/<int:pk>/', views.CobraFbaDetailView.as_view(), name='cobrafba_detail'),
    path(
        'models/<int:model_pk>/fba/<int:pk>/create/',
        views.CobraFbaCreateView.as_view(),
        name='cobrafba_create_form'
    ),
    path(
        'models/<int:model_pk>/fba/<int:pk>/delete/',
        views.CobraFbaDeleteView.as_view(),
        name='cobrafba_confirm_delete'
    ),

    path('models/<int:model_pk>/fva/', views.CobraFvaListView.as_view(), name='cobrafva_list'),
    path('models/<int:model_pk>/fva/<int:pk>/', views.CobraFvaDetailView.as_view(), name='cobrafva_detail'),
    path(
        'models/<int:model_pk>/fva/<int:pk>/create/',
        views.CobraFvaCreateView.as_view(),
        name='cobrafva_create_form'
    ),
    path(
        'models/<int:model_pk>/fva/<int:pk>/delete/',
        views.CobraFvaDeleteView.as_view(),
        name='cobrafva_confirm_delete'
    ),
]

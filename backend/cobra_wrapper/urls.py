from django.urls import path

from . import views, api_views

app_name = 'cobra_wrapper'
urlpatterns = [
    path('models/', views.CobraModelListView.as_view(), name='cobramodel_list'),
    path('models/<int:pk>/', views.CobraModelDetailView.as_view(), name='cobramodel_detail'),
    path('models/<int:pk>/json/', api_views.CobraModelDetailJsonView.as_view(), name='cobramodel_detail_json'),
    path('models/create/', views.CobraModelCreateView.as_view(), name='cobramodel_create_form'),
    path('models/<int:pk>/delete/', views.CobraModelDeleteView.as_view(), name='cobramodel_confirm_delete'),
    path('models/<int:pk>/update/', views.CobraModelUpdateView.as_view(), name='cobramodel_update_form'),

    path('models/<int:model_pk>/fba/', views.CobraFbaListView.as_view(), name='cobrafba_list'),
    path('models/<int:model_pk>/fba/<int:pk>/', views.CobraFbaDetailView.as_view(), name='cobrafba_detail'),
    path('models/<int:model_pk>/fba/create/', views.CobraFbaCreateView.as_view(), name='cobrafba_create_form'),
    path('models/<int:model_pk>/fba/<int:pk>/delete/', views.CobraFbaDeleteView.as_view(),
         name='cobrafba_confirm_delete'),
    path('models/<int:model_pk>/fva/', views.CobraFvaListView.as_view(), name='cobrafva_list'),
    path('models/<int:model_pk>/fva/<int:pk>/', views.CobraFvaDetailView.as_view(), name='cobrafva_detail'),
    path('models/<int:model_pk>/fva/create/', views.CobraFvaCreateView.as_view(), name='cobrafva_create_form'),
    path('models/<int:model_pk>/fva/<int:pk>/delete/', views.CobraFvaDeleteView.as_view(),
         name='cobrafva_confirm_delete'),
]

from django.urls import path
from . import views

app_name = 'models_demo'

urlpatterns = [
    path('', views.index, name='index'),
    path('categories/', views.category_list, name='category_list'),
    path('products/', views.product_list, name='product_list'),
    path('products/<int:pk>/', views.product_detail, name='product_detail'),
    path('reviews/', views.review_list, name='review_list'),
    path('tags/', views.tag_list, name='tag_list'),
    path('orders/', views.order_list, name='order_list'),
] 
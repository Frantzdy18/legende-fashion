from django.urls import path
from . import views

urlpatterns = [
    path("admin-users/", views.admin_users, name="admin_users"),
    path("admin-user/<int:user_id>/", views.admin_user_profile, name="admin_user_profile"),
    path('signup/', views.signup_view, name='signup'),
    path('products/buy/<int:pk>/', views.buy_product, name='buy_product'),
    path('', views.product_list, name='product_list'),
    path('create/', views.product_create, name='product_create'),
    path('update/<int:pk>/', views.product_update, name='product_update'),
    path('delete/<int:pk>/', views.product_delete, name='product_delete'),
    path('buy/<int:pk>/', views.buy_product, name='buy_product'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('demo-topup/', views.demo_topup, name='demo_topup'),
    path('demo-withdraw/', views.demo_withdraw, name='demo_withdraw'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('orders/', views.orders, name='orders'),
    path("cart/", views.cart_view, name="cart"),
    path("add-to-cart/<int:product_id>/", views.add_to_cart, name="add_to_cart"),
    path("checkout/", views.checkout, name="checkout"),
    path('livrer/<int:order_id>/', views.mark_as_delivered, name='mark_as_delivered'),
    path('update-purchase/<int:purchase_id>/<str:status>/', views.update_purchase_status, name='update_purchase_status'),
    path('search/', views.product_search, name='product_search'),
    path('profile/', views.profile, name='profile'),
    path('remove-from-cart/<int:product_id>/', views.remove_from_cart, name='remove_from_cart'),
]  
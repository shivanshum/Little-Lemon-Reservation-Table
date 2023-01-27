from django.urls import path
from . import views

urlpatterns = [
    path('categories', views.CategoriesView.as_view()),
    path('menu-items', views.MenuItemsView.as_view()),
    path('menu-items/<int:pk>', views.single_item_view),
    path('groups/manager/users', views.managers),
    path('groups/delivery-crew/users', views.delivery_crew),
    path('cart/menu-items', views.cart_items),
    path('orders', views.orders_items),
    path('orders/<int:pk>', views.delivery_order),
]

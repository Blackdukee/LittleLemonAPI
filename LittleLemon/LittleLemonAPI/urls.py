from django.urls import path
from . import views


urlpatterns = [
    path("categories/", views.Categories.as_view({"get": "list", "post": "create"})),
    path("menu-items/", views.MenuItems.as_view({"get": "list", "post": "create"})),
    path("menu-items/<int:pk>/", views.MenuItems.as_view({"get": "retrieve",
                                                            "put": "update",
                                                            "delete": "destroy",
                                                            "patch": "partial_update"})),
    path("cart/menu-items/", views.CartMenuItems.as_view({"get": "list", "post": "create", "delete": "destroy"})),
    path("orders/", views.Orders.as_view({"get": "list", "post": "create"})),
    path("orders/<int:pk>/", views.Orders.as_view({"get": "retrieve",
                                                   "delete": "destroy",
                                                   "put": "update",
                                                   "patch": "partial_update"})),
    path("groups/manager/users/", views.ManagerUsers.as_view({"get": "list", "post": "create"})),
    path("groups/manager/users/<int:pk>/", views.ManagerUsers.as_view({"get": "retrieve", "delete": "destroy"})),
    path("groups/delivery-crew/users/", views.DeliveryCrewUsers.as_view({"get": "list", "post": "create"})),
    path("groups/delivery-crew/users/<int:pk>/", views.DeliveryCrewUsers.as_view({"get": "retrieve", "delete": "destroy"})),    
    
]



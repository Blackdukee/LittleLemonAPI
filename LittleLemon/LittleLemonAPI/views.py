from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User, Group
from rest_framework.response import Response
from rest_framework import status
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from rest_framework.throttling import UserRateThrottle, AnonRateThrottle
from .models import *
from .serializers import *
from .utils import IsManagerOrAdmin
from datetime import datetime

class Categories(viewsets.ModelViewSet):
    """
    A viewset for viewing and editing category instances.
    """
    queryset = Category.objects.all()
    authentication_classes = [TokenAuthentication]
    serializer_class = CategorySerializer
    
    def get_permissions(self):
        """
        Assign permissions based on the request method.
        """
        permission_classes = []
        if self.request.method != 'GET':
            permission_classes = [IsManagerOrAdmin]
        if permission_classes:
            return [permission() for permission in permission_classes]
        return []

class MenuItems(viewsets.ModelViewSet):
    """
    A viewset for viewing and editing menu item instances.
    """
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    throttle_classes = [UserRateThrottle, AnonRateThrottle]
    queryset = MenuItem.objects.all()
    serializer_class = MenuItemSerializer
    ordering_fields = ["price", "title"]
    search_fields = ['title', 'category__title']
    
    def list(self, request, *args, **kwargs):
        """
        List all menu items. Only authenticated users or delivery crew can view.
        """
        if request.user.is_authenticated or request.user.groups.filter(name='Delivery Crew').exists():
            request.status_code = status.HTTP_200_OK
            return super().list(request, *args, **kwargs)
        return Response(status=status.HTTP_403_FORBIDDEN, data={"message": "You need to login to view this page"})
        
    def retrieve(self, request, *args, **kwargs):
        """
        Retrieve a menu item. Only managers or superusers can view.
        """
        if request.user.groups.filter(name='Manager').exists() or request.user.is_superuser:
            if request.method == 'POST':
                request.status_code = status.HTTP_201_CREATED
            return super().retrieve(request, *args, **kwargs)
        return Response(status=status.HTTP_403_FORBIDDEN, data={"message": "You are not authorized to view this page"})

    def create(self, request, *args, **kwargs):
        """
        Create a new menu item. Only managers or superusers can create.
        """
        if request.user.groups.filter(name='Manager').exists() or request.user.is_superuser:
            return super().create(request, *args, **kwargs)
        return Response(status=status.HTTP_401_UNAUTHORIZED)
   
    def destroy(self, request, *args, **kwargs):
        """
        Delete a menu item. Only managers or superusers can delete.
        """
        if request.user.groups.filter(name='Manager').exists() or request.user.is_superuser:
            return super().destroy(request, *args, **kwargs)
        return Response(status=status.HTTP_401_UNAUTHORIZED)
    
    def update(self, request, *args, **kwargs):
        """
        Update a menu item. Only managers or superusers can update.
        """
        if request.user.groups.filter(name='Manager').exists() or request.user.is_superuser:
            return super().update(request, *args, **kwargs)
        Response(status=status.HTTP_401_UNAUTHORIZED)
        
    def partial_update(self, request, *args, **kwargs):
        """
        Partially update a menu item.
        """
        return super().partial_update(request, *args, **kwargs)

class CartMenuItems(viewsets.ModelViewSet):
    """
    A viewset for viewing and editing cart instances.
    """
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    throttle_classes = [UserRateThrottle, AnonRateThrottle]
    queryset = Cart.objects.all()
    serializer_class = CartSerializer
    ordering_fields = ["price", "quantity"]
    search_fields = ['menuitem__title']
    
    def list(self, request):
        """
        List all cart items for the current user.
        """
        current_user = request.user
        if current_user.is_authenticated:
            queryset = Cart.objects.filter(user=current_user)
            serializer = CartSerializer(queryset, many=True)
            return Response(serializer.data)
        return Response(status=status.HTTP_403_FORBIDDEN)
        
    def create(self, request, *args, **kwargs):
        """
        Add a menu item to the cart. Only authenticated users, delivery crew, superusers, or managers can add.
        """
        current_user = request.user
        if (not current_user.is_authenticated and
            not current_user.groups.filter(name='Delivery Crew').exists()
            or not current_user.is_superuser
            or not current_user.groups.filter(name='Manager').exists() or request.user.is_superuser):
            return Response(status=status.HTTP_403_FORBIDDEN)
        menuitem = MenuItem.objects.get(title=request.data.get('title'))
        quantity = request.data.get('quantity')
        unit_price = menuitem.price
        price = unit_price * Decimal(quantity)
        cart = Cart(user=current_user, menuitem=menuitem, quantity=quantity, unit_price=unit_price, price=price)
        cart.save()
        return Response(status=status.HTTP_201_CREATED)
        
    def destroy(self, request, *args, **kwargs):
        """
        Delete all cart items for the current user.
        """
        current_user = request.user
        if current_user.is_authenticated:
            carts = Cart.objects.filter(user=current_user)
            if not carts:
                return Response(status=status.HTTP_404_NOT_FOUND, data={"message": "Cart is empty"})
            carts.delete()
            return Response(status=status.HTTP_200_OK)

class Orders(viewsets.ModelViewSet):
    """
    A viewset for viewing and editing order instances.
    """
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    throttle_classes = [UserRateThrottle, AnonRateThrottle]
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    ordering_fields = ["date", "total"]
    search_fields = ['date', 'total', 'status', 'user__username']
    
    def list(self, request, *args, **kwargs):
        """
        List all orders. Managers and superusers can view all orders. Delivery crew can view their orders. Users can view their own orders.
        """
        current_user = request.user
        if current_user.groups.filter(name='Manager').exists() or request.user.is_superuser:
            Orders.queryset = Order.objects.all()
            return super().list(request, *args, **kwargs)
        if current_user.groups.filter(name='Delivery crew').exists():
            Orders.queryset = Order.objects.filter(delivery_crew=current_user)
            return super().list(request, *args, **kwargs)
        if current_user.is_authenticated:
            Orders.queryset = Order.objects.filter(user=current_user)
            return super().list(request, *args, **kwargs)
        
    def retrieve(self, request, *args, **kwargs):
        """
        Retrieve an order. Only the user who placed the order can view it.
        """
        order_id = kwargs.get('pk')
        order = get_object_or_404(Order, id=kwargs.get('pk'))
        if order.user != request.user:
            return Response(status=status.HTTP_403_FORBIDDEN, data={"message": "You are not authorized to view this order"})
        return super().retrieve(request, *args, **kwargs)
        
    def create(self, request, *args, **kwargs):
        """
        Create a new order from the user's cart. Only authenticated users can create.
        """
        current_user = request.user
        if not current_user.is_authenticated:
            return Response(status=status.HTTP_403_FORBIDDEN)
        total = 0
        user_cart = Cart.objects.filter(user=current_user)
        for cart in user_cart:
            total += cart.price
        order = Order(user=current_user, total=total, date=datetime.now())
        order.save()
        for cart in user_cart:
            order_item = OrderItem(order=current_user, menuitem=cart.menuitem, quantity=cart.quantity, unit_price=cart.unit_price, price=cart.price)
            order_item.save()
        user_cart.delete()
        return Response(status=status.HTTP_201_CREATED)
        
    def update(self, request, *args, **kwargs):
        """
        Update an order. Only managers or superusers can update.
        """
        if request.user.groups.filter(name='Manager').exists() or request.user.is_superuser:
            return super().update(request, *args, **kwargs)
        return Response(status=status.HTTP_403_FORBIDDEN)
        
    def destroy(self, request, *args, **kwargs):
        """
        Delete an order. Only managers or superusers can delete.
        """
        if request.user.groups.filter(name='Manager').exists() or request.user.is_superuser:
            order = Order.objects.get(id=kwargs.get('pk'))
            if order:
                order.delete()
                return Response(status=status.HTTP_200_OK)
            return Response(status=status.HTTP_404_NOT_FOUND)
        return Response(status=status.HTTP_403_FORBIDDEN)
        
    def partial_update(self, request, *args, **kwargs):
        """
        Partially update an order. Managers can assign delivery crew. Delivery crew can update order status.
        """
        if request.user.groups.filter(name='Manager').exists() or request.user.is_superuser:
            user_id = request.data.get('delivery_crew')
            orders = Order.objects.filter(user__id=kwargs.get('pk'))
            if orders:
                for order in orders:
                    order.delivery_crew = User.objects.get(id=user_id)
                    order.save()
                return Response(status=status.HTTP_200_OK)
            return Response(status=status.HTTP_404_NOT_FOUND)
        elif request.user.groups.filter(name='Delivery crew').exists():
            orders = Order.objects.filter(user_id=kwargs.get('pk'))
            if orders:
                for order in orders:
                    order.status = request.data.get('status')
                    order.save()
                return Response(status=status.HTTP_200_OK)
            return Response(status=status.HTTP_404_NOT_FOUND)
        return Response(status=status.HTTP_403_FORBIDDEN)

class ManagerUsers(viewsets.ModelViewSet):
    """
    A viewset for viewing and editing manager user instances.
    """
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    throttle_classes = [UserRateThrottle, AnonRateThrottle]
    queryset = User.objects.all().filter(groups__name='Manager')
    serializer_class = ManagerSerializer
    ordering_fields = ["username"]
    search_fields = ['username', 'email']
    
    def list(self, request, *args, **kwargs):
        """
        List all manager users. Only managers or superusers can view.
        """
        if request.user.groups.filter(name='Manager').exists() or request.user.is_superuser:
            return super().list(request, *args, **kwargs)
        return Response(status=status.HTTP_403_FORBIDDEN)
    
    def retrieve(self, request, *args, **kwargs):
        """
        Retrieve a manager user. Only managers or superusers can view.
        """
        if request.user.groups.filter(name='Manager').exists() or request.user.is_superuser:
            return super().retrieve(request, *args, **kwargs)
        return Response(status=status.HTTP_403_FORBIDDEN)
        
    def create(self, request, *args, **kwargs):
        """
        Add a user to the manager group. Only managers or superusers can add.
        """
        if request.user.groups.filter(name='Manager').exists() or request.user.is_superuser:
            username = request.data.get('username')
            user = User.objects.get(username=username)
            user.groups.add(Group.objects.get(name='Manager'))
            return Response(status=status.HTTP_201_CREATED, data={"message": "User is added to Managers"})
        return Response(status=status.HTTP_403_FORBIDDEN)
        
    def destroy(self, request, pk, *args, **kwargs):
        """
        Remove a user from the manager group. Only managers or superusers can remove.
        """
        if request.user.groups.filter(name='Manager').exists() or request.user.is_superuser:
            user = User.objects.get(id=pk)
            if user and user.groups.filter(name='Manager').exists() or request.user.is_superuser:
                user.groups.remove(Group.objects.get(name='Manager'))
                return Response(status=status.HTTP_200_OK, data={"message": "User is removed from Managers"})
            else:
                return Response(status=status.HTTP_404_NOT_FOUND)
        return Response(status=status.HTTP_403_FORBIDDEN)
        
    def partial_update(self, request, *args, **kwargs):
        """
        Partially update a manager user. Only managers or superusers can update.
        """
        if request.user.groups.filter(name='Manager').exists() or request.user.is_superuser:
            return super().list(request, *args, **kwargs)
        return Response(status=status.HTTP_403_FORBIDDEN)

class DeliveryCrewUsers(viewsets.ModelViewSet):
    """
    A viewset for viewing and editing delivery crew user instances.
    """
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    throttle_classes = [UserRateThrottle, AnonRateThrottle]
    queryset = User.objects.all().filter(groups__name='Delivery crew')
    serializer_class = DeliveryCrewSerializer
    ordering_fields = ["username"]
    search_fields = ['username', 'email']
    
    def list(self, request, *args, **kwargs):
        """
        List all delivery crew users. Only managers or superusers can view.
        """
        if request.user.groups.filter(name='Manager').exists() or request.user.is_superuser:
            return super().list(request, *args, **kwargs)
        return Response({"messages": "not allowed"}, status=status.HTTP_403_FORBIDDEN)
        
    def create(self, request, *args, **kwargs):
        """
        Add a user to the delivery crew group. Only managers or superusers can add.
        """
        if request.user.groups.filter(name='Manager').exists() or request.user.is_superuser:
            username = request.data.get('username')
            user = User.objects.get(username=username)
            user.groups.add(Group.objects.get(name='Delivery crew'))
            return Response(status=status.HTTP_201_CREATED, data={"message": "User is added to Delivery Crew"})
        return Response({"messages": "not allowed"}, status=status.HTTP_403_FORBIDDEN)
        
    def destroy(self, request, pk, *args, **kwargs):
        """
        Remove a user from the delivery crew group. Only managers or superusers can remove.
        """
        if request.user.groups.filter(name='Manager').exists() or request.user.is_superuser:
            user = User.objects.get(id=pk)
            if not user:
                return Response(status=status.HTTP_404_NOT_FOUND)
            user.groups.remove(Group.objects.get(name='Delivery crew'))
            return Response(status=status.HTTP_200_OK, data={"message": "User is removed from Delivery Crew"})
        return Response({"messages": "not allowed"}, status=status.HTTP_403_FORBIDDEN)
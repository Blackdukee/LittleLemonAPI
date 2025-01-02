from rest_framework import serializers
from rest_framework.validators import UniqueValidator, UniqueTogetherValidator
from decimal import Decimal
from .models import *
from django.contrib.auth.models import User

class ManagerSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username", "email", "first_name", "last_name", "is_staff"]

class DeliveryCrewSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username", "email", "first_name", "last_name", "is_staff"]


class CategorySerializer(serializers.ModelSerializer):

    class Meta:
        model = Category
        fields = ["id", "slug", "title"]


# MenuItem Serializer
class MenuItemSerializer(serializers.ModelSerializer):
   

    price_after_tax = serializers.SerializerMethodField(method_name="calculate_tax")
    category = CategorySerializer(read_only=True)
    category_id = serializers.IntegerField(write_only=True)

    def validate(self, attrs):
      
        if attrs["price"] < 0:
            raise serializers.ValidationError("Price must be greater than 0.")

        return super().validate(attrs)

    class Meta:
        model = MenuItem
        fields = [
            "id",
            "title",
            "price",
            "price_after_tax",
            "featured",
            "category",
            "category_id",
        ]
        extra_kwargs = {    
            "title": {"validators": [UniqueValidator(queryset=MenuItem.objects.all())]}
        }

    def calculate_tax(self, product: MenuItem):
        
        return product.price * Decimal(1.1)

class CartSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cart
        fields = ["id", "user", "menuitem", "quantity", "unit_price", "price"]

class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ["id", "user", "delivery_crew", "status", "total", "date"]

class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = ["id", "order", "menuitem", "quantity", "unit_price", "price"]
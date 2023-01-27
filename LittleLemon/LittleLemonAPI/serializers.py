from rest_framework import serializers
from .models import Category, MenuItem, Cart, Order, OrderItem
from rest_framework.validators import UniqueTogetherValidator
from django.contrib.auth.models import User, Group

class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = ['name']

class UserSerializer(serializers.ModelSerializer):
    groups = GroupSerializer(many=True)
    class Meta:
        model = User
        fields = ['username', 'groups']

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'slug', 'title']

class MenuItemSerializer(serializers.ModelSerializer):
    category_id = serializers.IntegerField(write_only=True)
    category = CategorySerializer(read_only=True)

    class Meta:
        model = MenuItem
        fields = ['id', 'title', 'price', 'featured', 'category', 'category_id']
        extra_kwargs = {
            'price': {'min_value': 2},
        }

class CartSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        default=serializers.CurrentUserDefault()
    )

    class Meta:
        model = Cart
        fields = ['user', 'menuitem', 'quantity', 'unit_price', 'price']
        extra_kwargs = {
            'quantity': {'min_value': 1},
            'unit_price': {'min_value': 2},
            'price': {'min_value': 2},
        }

        validators = [
            UniqueTogetherValidator(
                queryset=Cart.objects.all(),
                fields=['user', 'menuitem']
                ),
            ]

class OrderSerializer(serializers.ModelSerializer):
    order = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        default=serializers.CurrentUserDefault()
    )
    delivery_crew = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        default=serializers.CurrentUserDefault()
    )

    class Meta:
        model = Order
        fields = ['order', 'delivery_crew', 'status', 'total', 'date']

class OrderItemSerializer(serializers.ModelSerializer):
    order = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        default=serializers.CurrentUserDefault()
    )

    menuitem = serializers.PrimaryKeyRelatedField(
        queryset=MenuItem.objects.all()
    )

    class Meta:
        model = OrderItem
        fields = ['order', 'menuitem', 'quantity', 'unit_price', 'price']
        extra_kwargs = {
            'quantity': {'min_value': 1},
            'unit_price': {'min_value': 2},
            'price': {'min_value': 2},
        }

        validators = [
            UniqueTogetherValidator(
                queryset=OrderItem.objects.all(),
                fields=['order', 'menuitem']
                ),
            ]

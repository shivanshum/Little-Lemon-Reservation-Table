from rest_framework import generics
from django.core import serializers
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from .models import Category, MenuItem, Cart, Order, OrderItem
from .serializers import CategorySerializer, MenuItemSerializer, CartSerializer, OrderSerializer, UserSerializer, OrderItemSerializer
from django.contrib.auth.models import User, Group
from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from datetime import date

class LittleLemonPermission(IsAdminUser):
    def has_permission(self, request, view):
        if request.method == 'GET':
            return True
        else:
            return super().has_permission(request, view)

class CategoriesView(generics.ListCreateAPIView):
    permission_classes = [LittleLemonPermission]
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

class MenuItemsView(generics.ListCreateAPIView):
    permission_classes = [LittleLemonPermission]
    queryset = MenuItem.objects.select_related('category').all()
    serializer_class = MenuItemSerializer
    ordering_fields = ['price']
    filterset_fields = ['category']

@api_view(['GET','POST'])
@permission_classes([IsAuthenticated])
def cart_items(request):
    user = request.user
    if request.method == 'GET':
        cart = Cart.objects.get(user=user)
        serializer = CartSerializer(cart)
        return JsonResponse(serializer.data, safe=False)
    if(request.method=='POST'):
        user = request.user
        name = request.data['menuitem']
        quantity = int(request.data['quantity'])
        menuitem = MenuItem.objects.get(title=name)
        unit_price = MenuItem.objects.get(title=name).price
        cart_items = Cart.objects.create(
            user = user,
            menuitem = menuitem,
            quantity = quantity,
            unit_price = unit_price,
            price = quantity * unit_price
            )
        cart = CartSerializer(cart_items, data=cart_items)
        if cart.is_valid():
            cart.save(cart_items)
        return Response({"message": "Successfully updated cart!"}, 201)

@api_view(['PUT','PATCH'])
@permission_classes([IsAuthenticated])
def delivery_order(request, pk):
    if request.user.groups.filter(name='Delivery Crew' or 'Manager').exists():
        order = Order.objects.get(pk=pk)
        serializer = OrderSerializer(order, data=request.data, context={'request': request}, partial=True)
        if serializer.is_valid():
            serializer.save()
        return Response({"message": "Successfully updated the order!"}, 201)
    else:
        return Response({"message": "You are not authorized"}, 403)

@api_view(['GET','POST'])
@permission_classes([IsAuthenticated])
def orders_items(request):
    if request.method == 'GET':
        user = request.user
        if request.user.groups.filter(name='Delivery Crew').exists():
            order = Order.objects.get(delivery_crew=user)
        else:
            order = Order.objects.get(user=user)
        serializer = OrderSerializer(order, context={'request': request})
        return JsonResponse(serializer.data, safe=False)
    if(request.method=='POST'):
        user = request.user
        menuitem = Cart.objects.get(user=user).menuitem.id
        quantity = Cart.objects.get(user=user).quantity
        unit_price = Cart.objects.get(user=user).unit_price
        price = Cart.objects.get(user=user).price
        order_items = OrderItem.objects.create(
            order = user,
            menuitem = menuitem,
            quantity = quantity,
            unit_price = unit_price,
            price = price,
            )
        serializer = OrderItemSerializer(order_items, data=order_items)
        if serializer.is_valid():
            serializer.save(order_items)
        order = Order.objects.create(
            user = user,
            total = price,
            date = date.today(),
        )
        serializer = OrderSerializer(order, data=order)
        if serializer.is_valid():
            serializer.save(order)
        return Response({"message": "Successfully created order!"}, 201)

@api_view(['GET','PUT','PATCH'])
@permission_classes([IsAuthenticated])
def single_item_view(request, pk):
    if request.method == 'GET':
        item = MenuItem.objects.get(pk=pk)
        serializer = MenuItemSerializer(item)
        return JsonResponse(serializer.data, safe=False)
    if request.user.groups.filter(name='Manager').exists():
        item = MenuItem.objects.get(pk=pk)
        serializer = MenuItemSerializer(item, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
        return Response({"message": "Successfully updated item of the day!"}, 201)
    else:
        return Response({"message": "You are not authorized"}, 403)

@api_view(['GET','POST'])
@permission_classes([IsAuthenticated])
def delivery_crew(request):
    if request.method == 'GET':
        crew = User.objects.filter(groups=2)
        serializer = UserSerializer(crew, many=True)
        return JsonResponse(serializer.data, safe=False)
    elif request.method=='POST':
        if request.user.groups.filter(name='Manager').exists():
            username = request.data['username']
            if username:
                delivery_crew = Group.objects.get(name="Delivery Crew")
                user = get_object_or_404(User, username=username)
                delivery_crew.user_set.add(user)
                return Response({"message": "User assigned to delivery crew"}, 201)
        else:
            return Response({"message": "You are not authorized"}, 403)

@api_view(['GET','POST'])
@permission_classes([LittleLemonPermission])
def managers(request):
    if request.method == 'GET':
        managers = User.objects.filter(groups=1)
        serializer = UserSerializer(managers, many=True)
        return JsonResponse(serializer.data, safe=False)
    elif(request.method=='POST'):
        username = request.data['username']
        if username:
            managers = Group.objects.get(name="Manager")
            user = get_object_or_404(User, username=username)
            managers.user_set.add(user)
        return Response({"message": "User assigned to manager group"}, 201)

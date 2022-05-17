from decimal import Decimal
from django.db import transaction
from django.db.models import Sum
from rest_framework import serializers
from store.models import Product, Collection, Review, Cart, CartItem, Customer, Order, OrderItem, ProductImage, Promotions
from store.signals import order_created


class CollectionSerializer(serializers.ModelSerializer):
    products_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Collection
        fields = ['id', 'title', 'products_count']


class ProductImageSerializer(serializers.ModelSerializer):

    def create(self, validated_data):
        return ProductImage.objects.create(product_id=self.context['product_id'], image=validated_data['image'])

    class Meta:
        model = ProductImage
        fields = ['id', 'image']


class ProductSerializer(serializers.ModelSerializer):
    price_with_tax = serializers.SerializerMethodField()
    images = ProductImageSerializer(many=True, read_only=True)
    price_after_discounts = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = ['id', 'title', 'description', 'slug', 'inventory', 'unit_price', 'price_with_tax',
                  'price_after_discounts', 'collection', 'images']

    @staticmethod
    def get_price_with_tax(product):
        return product.unit_price * Decimal(1.1)

    @staticmethod
    def get_price_after_discounts(product):
        discount_sum = product.promotions.aggregate(discount_sum=Sum('discount'))['discount_sum']
        price = float(get_price_with_tax(product))
        discount = float((discount_sum * price)/100)
        return price - discount


class ReviewSerializer(serializers.ModelSerializer):

    class Meta:
        model = Review
        fields = ['id', 'date', 'name', 'description']

    def create(self, validated_data):
        validated_data['product_id'] = self.context['product_pk']
        return super().create(validated_data)


class CartItemProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 'title', 'unit_price']


class CartItemSerializer(serializers.ModelSerializer):
    product = CartItemProductSerializer()
    total_price = serializers.SerializerMethodField()

    def get_total_price(self, cart_item):
        return cart_item.quantity * cart_item.product.unit_price

    class Meta:
        model = CartItem
        fields = ['id', 'product', 'quantity', 'total_price']


class CartSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(read_only=True)
    items = CartItemSerializer(many=True, read_only=True)
    total_price = serializers.SerializerMethodField()

    def get_total_price(self, cart):
        return sum([item.quantity * item.product.unit_price for item in cart.items.all()])

    class Meta:
        model = Cart
        fields = ['id', 'items', 'total_price']


class AddCartItemSerializer(serializers.ModelSerializer):
    product_id = serializers.IntegerField()

    def validate_product_id(self, value):
        if not Product.objects.filter(id=value).exists():
            raise serializers.ValidationError('Product does not exist')
        return value

    def save(self, **kwargs):
        cart_id = self.context['cart_id']
        product_id = self.validated_data['product_id']
        quantity = self.validated_data['quantity']
        try:
            cart_item = CartItem.objects.get(cart_id=cart_id, product_id=product_id)
            cart_item.quantity += quantity
            cart_item.save()
            self.instance = cart_item
        except CartItem.DoesNotExist:
            self.instance = CartItem.objects.create(cart_id=cart_id, product_id=product_id, quantity=quantity)
        return self.instance

    class Meta:
        model = CartItem
        fields = ['id', 'product_id', 'quantity']


class UpdateCartItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = CartItem
        fields = ['quantity']


class CustomerSerializer(serializers.ModelSerializer):
    user_id = serializers.IntegerField(read_only=True)

    class Meta:
        model = Customer
        fields = ['id', 'user_id', 'phone', 'birth_date', 'membership']


class OrderItemSerializer(serializers.ModelSerializer):
    product = CartItemProductSerializer()

    class Meta:
        model = OrderItem
        fields = ['id', 'product', 'unit_price', 'quantity']


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True)

    class Meta:
        model = Order
        fields = ['id', 'customer', 'placed_at', 'payment_status', 'items']


class UpdateOrderSerializer(serializers.ModelSerializer):

    class Meta:
        model = Order
        fields = ['payment_status']


class CreateOrderSerializer(serializers.Serializer):
    cart_id = serializers.UUIDField()

    def validate_cart_id(self, value):
        if not Cart.objects.filter(pk=value).exists():
            raise serializers.ValidationError('No cart with the given id was found')
        if CartItem.objects.filter(cart_id=value).count() == 0:
            raise serializers.ValidationError('The cart is empty')
        return value

    def save(self, **kwargs):
        with transaction.atomic():
            cart_id = self.validated_data['cart_id']
            user_id = self.context['user_id']
            customer = Customer.objects.get(user_id=user_id)
            order = Order.objects.create(customer=customer)
            cart_items = CartItem.objects.select_related('product').filter(cart_id=cart_id)
            OrderItem.objects.bulk_create([OrderItem(order=order, product=item.product, quantity=item.quantity,
                                                     unit_price=item.product.unit_price) for item in cart_items])
            Cart.objects.filter(pk=cart_id).delete()
            order_created.send_robust(sender=self.__class__, order=order)
        return order

from rest_framework_nested.routers import DefaultRouter, NestedDefaultRouter
from store.views import ProductViewSet, CollectionViewSet, ReviewViewSet, CartViewSet, CartItemViewSet, \
    CustomerViewSet, OrderViewSet, ProductImageViewSet

router = DefaultRouter()
router.register('collections', CollectionViewSet)
router.register('products', ProductViewSet, basename='products')
router.register('carts', CartViewSet, basename='carts')
router.register('customers', CustomerViewSet, basename='customers')
router.register('orders', OrderViewSet, basename='orders')

products_router = NestedDefaultRouter(router, 'products', lookup='product')
products_router.register('reviews', ReviewViewSet, basename='product-reviews')
products_router.register('images', ProductImageViewSet, basename='product-images')

carts_router = NestedDefaultRouter(router, 'carts', lookup='cart')
carts_router.register('items', CartItemViewSet, basename='cart-items')

urlpatterns = router.urls + products_router.urls + carts_router.urls

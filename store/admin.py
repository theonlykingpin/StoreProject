from django.contrib import admin, messages
from django.db.models import Count
from django.utils.html import format_html, urlencode
from django.urls import reverse
from store import models


class InventoryFilter(admin.SimpleListFilter):
    title = 'inventory'
    parameter_name = 'inventory'

    def lookups(self, request, model_admin):
        return [
            ('<10', 'Low')
        ]

    def queryset(self, request, queryset):
        if self.value() == '<10':
            return queryset.filter(inventory__lt=10)


@admin.register(models.Promotions)
class PromotionsAdmin(admin.ModelAdmin):
    pass


@admin.register(models.Collection)
class CollectionAdmin(admin.ModelAdmin):
    list_display = ['id', 'title', 'product_count']
    search_fields = ['title']

    @admin.display(ordering='orders_count')
    def product_count(self, collection):
        url = reverse('admin:store_product_changelist') + '?' + urlencode({'collection__id': str(collection.id)})
        return format_html('<a href="{}" >{}</a>', url, collection.products_count)

    def get_queryset(self, request):
        return super().get_queryset(request).annotate(products_count=Count('products'))


class ProductImageInline(admin.TabularInline):
    model = models.ProductImage
    readonly_fields = ['thumbnail']

    def thumbnail(self, obj):
        if obj.image:
            return format_html('<img src="{}" class="thumbnail" />', obj.image.url)
        return ''


@admin.register(models.Product)
class ProductAdmin(admin.ModelAdmin):
    autocomplete_fields = ['collection']
    actions = ['clear_inventory']
    inlines = [ProductImageInline]
    list_display = ['title', 'unit_price', 'inventory_status', 'collection_title']
    list_editable = ['unit_price']
    list_filter = ['collection', 'last_update', InventoryFilter]
    list_per_page = 10
    list_select_related = ['collection']
    prepopulated_fields = {'slug': ('title',)}
    search_fields = ['title', 'description']

    def collection_title(self, product):
        return product.collection.title

    @admin.display(ordering='inventory')
    def inventory_status(self, product):
        if product.inventory < 10:
            return 'Low'
        return 'OK'

    @admin.action(description='Clear inventory')
    def clear_inventory(self, request, queryset):
        updated_count = queryset.update(inventory=0)
        self.message_user(request, '{} products were successfully updated'.format(updated_count), messages.ERROR)

    class Media:
        css = {
            'all': ['store/styles.css']
        }


@admin.register(models.Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_select_related = ['user']
    list_display = ['first_name', 'last_name', 'membership', 'orders']
    list_editable = ['membership']
    list_per_page = 10
    ordering = ['user__first_name', 'user__last_name']
    search_fields = ['first_name__istartswith', 'last_name__istartswith']

    @admin.display(ordering='orders_count')
    def orders(self, customer):
        url = reverse('admin:store_order_changelist') + '?' + urlencode({'customer__id': str(customer.id)})
        return format_html('<a href="{}" >{} Order(s)</a>', url, customer.order_set.count())


class OrderItemInline(admin.TabularInline):
    autocomplete_fields = ['product']
    model = models.OrderItem
    extra = 0
    min_num = 1
    max_num = 10


@admin.register(models.Order)
class OrderAdmin(admin.ModelAdmin):
    autocomplete_fields = ['customer']
    inlines = [OrderItemInline]
    list_display = ['id', 'placed_at', 'customer']


@admin.register(models.OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    pass


@admin.register(models.Address)
class AddressAdmin(admin.ModelAdmin):
    pass


@admin.register(models.Cart)
class CartAdmin(admin.ModelAdmin):
    pass


@admin.register(models.CartItem)
class CartItemAdmin(admin.ModelAdmin):
    pass

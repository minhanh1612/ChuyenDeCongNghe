from django.contrib import admin
from django.utils.html import format_html
from .models import Category, Product, ProductImage, Review, Tag, Order, OrderItem


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'is_active', 'product_count', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'description']
    list_editable = ['is_active']
    readonly_fields = ['created_at', 'updated_at']
    
    def product_count(self, obj):
        return obj.get_product_count()
    product_count.short_description = 'Số sản phẩm'


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = [
        'name', 'category', 'price', 'discount_price', 'final_price',
        'stock_quantity', 'rating', 'status', 'is_featured', 'created_at'
    ]
    list_filter = [
        'category', 'status', 'is_featured', 'created_at', 'rating'
    ]
    search_fields = ['name', 'description', 'slug']
    list_editable = ['status', 'is_featured', 'stock_quantity']
    readonly_fields = ['rating', 'created_at', 'updated_at']
    prepopulated_fields = {'slug': ('name',)}
    
    fieldsets = (
        ('Thông tin cơ bản', {
            'fields': ('name', 'slug', 'category', 'description')
        }),
        ('Giá cả', {
            'fields': ('price', 'discount_price')
        }),
        ('Trạng thái', {
            'fields': ('status', 'is_featured', 'stock_quantity')
        }),
        ('Thông tin khác', {
            'fields': ('rating', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def final_price(self, obj):
        return obj.get_final_price()
    final_price.short_description = 'Giá cuối'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('category')


@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    list_display = ['product', 'image_preview', 'is_primary', 'order', 'created_at']
    list_filter = ['is_primary', 'created_at']
    list_editable = ['is_primary', 'order']
    search_fields = ['product__name', 'alt_text']
    
    def image_preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="max-height: 50px; max-width: 50px;" />',
                obj.image.url
            )
        return "Không có hình"
    image_preview.short_description = 'Hình ảnh'


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = [
        'product', 'user', 'rating', 'title', 'is_verified_purchase', 'created_at'
    ]
    list_filter = ['rating', 'is_verified_purchase', 'created_at']
    search_fields = ['product__name', 'user__username', 'title', 'comment']
    list_editable = ['is_verified_purchase']
    readonly_fields = ['created_at', 'updated_at']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('product', 'user')


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'color_preview', 'product_count', 'created_at']
    list_filter = ['created_at']
    search_fields = ['name', 'slug']
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ['created_at']
    
    def color_preview(self, obj):
        return format_html(
            '<div style="background-color: {}; width: 20px; height: 20px; border: 1px solid #ccc;"></div>',
            obj.color
        )
    color_preview.short_description = 'Màu sắc'
    
    def product_count(self, obj):
        return obj.get_product_count()
    product_count.short_description = 'Số sản phẩm'


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 1
    readonly_fields = ['total_price']


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = [
        'order_number', 'user', 'status', 'total_amount', 'items_count', 'created_at'
    ]
    list_filter = ['status', 'created_at']
    search_fields = ['order_number', 'user__username', 'shipping_address']
    list_editable = ['status']
    readonly_fields = ['order_number', 'total_amount', 'created_at', 'updated_at']
    inlines = [OrderItemInline]
    
    fieldsets = (
        ('Thông tin đơn hàng', {
            'fields': ('order_number', 'user', 'status')
        }),
        ('Thông tin giao hàng', {
            'fields': ('shipping_address', 'notes')
        }),
        ('Thông tin khác', {
            'fields': ('total_amount', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def items_count(self, obj):
        return obj.get_items_count()
    items_count.short_description = 'Số sản phẩm'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user')


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ['order', 'product', 'quantity', 'unit_price', 'total_price']
    list_filter = ['order__status']
    search_fields = ['order__order_number', 'product__name']
    readonly_fields = ['total_price']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('order', 'product')

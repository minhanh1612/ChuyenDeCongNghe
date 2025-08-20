from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.contrib.auth.models import User


class Category(models.Model):
    name = models.CharField(
        max_length=100,
        unique=True,
        help_text="Tên danh mục sản phẩm"
    )
    description = models.TextField(
        blank=True,
        null=True,
        help_text="Mô tả chi tiết về danh mục"
    )
    is_active = models.BooleanField(
        default=True,
        help_text="Trạng thái hoạt động của danh mục"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="Thời gian tạo danh mục"
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="Thời gian cập nhật cuối cùng"
    )
    
    class Meta:
        verbose_name = "Danh mục"
        verbose_name_plural = "Danh mục"
        ordering = ['name']
        db_table = 'demo_categories'
        indexes = [
            models.Index(fields=['name']),
            models.Index(fields=['is_active', 'created_at']),
        ]
    
    def __str__(self):
        return self.name
    
    def get_product_count(self):
        """Instance method để đếm số sản phẩm trong danh mục"""
        return self.products.count()


class Product(models.Model):
    """
    Model minh họa các loại field nâng cao, relationships và custom methods
    """
    PRODUCT_STATUS_CHOICES = [
        ('draft', 'Bản nháp'),
        ('published', 'Đã xuất bản'),
        ('archived', 'Đã lưu trữ'),
    ]
    
    name = models.CharField(
        max_length=200,
        help_text="Tên sản phẩm"
    )
    slug = models.SlugField(
        max_length=200,
        unique=True,
        help_text="URL-friendly version của tên sản phẩm"
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name='products',
        help_text="Danh mục sản phẩm"
    )
    description = models.TextField(
        help_text="Mô tả chi tiết sản phẩm"
    )
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        help_text="Giá sản phẩm"
    )
    discount_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        blank=True,
        null=True,
        validators=[MinValueValidator(0)],
        help_text="Giá khuyến mãi (nếu có)"
    )
    stock_quantity = models.PositiveIntegerField(
        default=0,
        help_text="Số lượng tồn kho"
    )
    rating = models.FloatField(
        default=0.0,
        validators=[MinValueValidator(0.0), MaxValueValidator(5.0)],
        help_text="Đánh giá trung bình (0-5)"
    )
    status = models.CharField(
        max_length=20,
        choices=PRODUCT_STATUS_CHOICES,
        default='draft',
        help_text="Trạng thái sản phẩm"
    )
    is_featured = models.BooleanField(
        default=False,
        help_text="Sản phẩm nổi bật"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Sản phẩm"
        verbose_name_plural = "Sản phẩm"
        ordering = ['-created_at']
        db_table = 'demo_products'
        indexes = [
            models.Index(fields=['category', 'status']),
            models.Index(fields=['price']),
            models.Index(fields=['rating']),
            models.Index(fields=['is_featured', 'status']),
        ]
        constraints = [
            models.CheckConstraint(
                check=models.Q(price__gte=0),
                name='price_positive'
            ),
            models.CheckConstraint(
                check=models.Q(rating__gte=0, rating__lte=5),
                name='rating_range'
            ),
        ]
    
    def __str__(self):
        return self.name
    
    def get_final_price(self):
        return self.discount_price if self.discount_price else self.price
    
    def is_in_stock(self):
        return self.stock_quantity > 0
    
    def get_discount_percentage(self):
        if self.discount_price and self.price > 0:
            return round(((self.price - self.discount_price) / self.price) * 100, 2)
        return 0
    
    @property
    def is_on_sale(self):
        return bool(self.discount_price and self.discount_price < self.price)


class ProductImage(models.Model):
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='images'
    )
    image = models.ImageField(
        upload_to='products/%Y/%m/%d/',
        help_text="Hình ảnh sản phẩm"
    )
    alt_text = models.CharField(
        max_length=200,
        blank=True,
        help_text="Mô tả hình ảnh cho SEO"
    )
    is_primary = models.BooleanField(
        default=False,
        help_text="Hình ảnh chính của sản phẩm"
    )
    order = models.PositiveSmallIntegerField(
        default=0,
        help_text="Thứ tự hiển thị hình ảnh"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Hình ảnh sản phẩm"
        verbose_name_plural = "Hình ảnh sản phẩm"
        ordering = ['order', 'created_at']
        db_table = 'demo_product_images'
        indexes = [
            models.Index(fields=['product', 'is_primary']),
            models.Index(fields=['order']),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=['product', 'is_primary'],
                condition=models.Q(is_primary=True),
                name='unique_primary_image_per_product'
            ),
        ]
    
    def __str__(self):
        return f"Hình ảnh của {self.product.name}"
    
    def save(self, *args, **kwargs):
        if self.is_primary:
            # Đặt tất cả hình ảnh khác của sản phẩm này thành không phải chính
            ProductImage.objects.filter(
                product=self.product,
                is_primary=True
            ).exclude(pk=self.pk).update(is_primary=False)
        super().save(*args, **kwargs)


class Review(models.Model):
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='reviews'
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='product_reviews'
    )
    rating = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text="Đánh giá từ 1-5 sao"
    )
    title = models.CharField(
        max_length=200,
        help_text="Tiêu đề đánh giá"
    )
    comment = models.TextField(
        help_text="Nội dung đánh giá chi tiết"
    )
    is_verified_purchase = models.BooleanField(
        default=False,
        help_text="Xác nhận mua hàng"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Đánh giá sản phẩm"
        verbose_name_plural = "Đánh giá sản phẩm"
        ordering = ['-created_at']
        db_table = 'demo_reviews'
        indexes = [
            models.Index(fields=['product', 'rating']),
            models.Index(fields=['user', 'created_at']),
            models.Index(fields=['is_verified_purchase', 'rating']),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=['product', 'user'],
                name='unique_review_per_user_per_product'
            ),
        ]
    
    def __str__(self):
        return f"Đánh giá của {self.user.username} cho {self.product.name}"
    
    def save(self, *args, **kwargs):
        """Override save method để cập nhật rating trung bình của sản phẩm"""
        super().save(*args, **kwargs)
        self.update_product_rating()
    
    def update_product_rating(self):
        """Method để cập nhật rating trung bình của sản phẩm"""
        avg_rating = self.product.reviews.aggregate(
            avg=models.Avg('rating')
        )['avg'] or 0.0
        self.product.rating = round(avg_rating, 2)
        self.product.save(update_fields=['rating'])


class Tag(models.Model):

    name = models.CharField(
        max_length=50,
        unique=True,
        help_text="Tên tag"
    )
    slug = models.SlugField(
        max_length=50,
        unique=True,
        help_text="URL-friendly version của tag"
    )
    color = models.CharField(
        max_length=7,
        default='#007bff',
        help_text="Màu sắc của tag (hex code)"
    )
    products = models.ManyToManyField(
        Product,
        related_name='tags',
        blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Tag"
        verbose_name_plural = "Tags"
        ordering = ['name']
        db_table = 'demo_tags'
        indexes = [
            models.Index(fields=['name']),
            models.Index(fields=['slug']),
        ]
    
    def __str__(self):
        return self.name
    
    def get_product_count(self):
        """Instance method để đếm số sản phẩm có tag này"""
        return self.products.count()


class Order(models.Model):

    ORDER_STATUS_CHOICES = [
        ('pending', 'Chờ xử lý'),
        ('processing', 'Đang xử lý'),
        ('shipped', 'Đã gửi hàng'),
        ('delivered', 'Đã giao hàng'),
        ('cancelled', 'Đã hủy'),
    ]
    
    order_number = models.CharField(
        max_length=20,
        unique=True,
        help_text="Mã đơn hàng"
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='orders'
    )
    status = models.CharField(
        max_length=20,
        choices=ORDER_STATUS_CHOICES,
        default='pending'
    )
    total_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="Tổng tiền đơn hàng"
    )
    shipping_address = models.TextField(
        help_text="Địa chỉ giao hàng"
    )
    notes = models.TextField(
        blank=True,
        help_text="Ghi chú đơn hàng"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Đơn hàng"
        verbose_name_plural = "Đơn hàng"
        ordering = ['-created_at']
        db_table = 'demo_orders'
        indexes = [
            models.Index(fields=['user', 'status']),
            models.Index(fields=['status', 'created_at']),
            models.Index(fields=['order_number']),
        ]
    
    def __str__(self):
        return f"Đơn hàng {self.order_number}"
    
    def get_status_display_name(self):
        """Instance method để lấy tên hiển thị của trạng thái"""
        return dict(self.ORDER_STATUS_CHOICES)[self.status]
    
    def can_cancel(self):
        """Instance method để kiểm tra có thể hủy đơn hàng không"""
        return self.status in ['pending', 'processing']
    
    def get_items_count(self):
        """Instance method để đếm số sản phẩm trong đơn hàng"""
        return self.items.count()


class OrderItem(models.Model):
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name='items'
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='order_items'
    )
    quantity = models.PositiveIntegerField(
        default=1,
        help_text="Số lượng sản phẩm"
    )
    unit_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="Đơn giá tại thời điểm đặt hàng"
    )
    total_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="Tổng tiền cho sản phẩm này"
    )
    
    class Meta:
        verbose_name = "Chi tiết đơn hàng"
        verbose_name_plural = "Chi tiết đơn hàng"
        db_table = 'demo_order_items'
        indexes = [
            models.Index(fields=['order', 'product']),
        ]
    
    def __str__(self):
        return f"{self.quantity}x {self.product.name} trong đơn hàng {self.order.order_number}"
    
    def save(self, *args, **kwargs):
        """Override save method để tự động tính total_price"""
        self.total_price = self.quantity * self.unit_price
        super().save(*args, **kwargs)

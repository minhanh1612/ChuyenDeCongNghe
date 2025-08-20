from django.shortcuts import render, get_object_or_404
from django.db.models import Count, Avg, Q
from .models import Category, Product, Review, Tag, Order


def index(request):
    context = {
        'total_categories': Category.objects.count(),
        'total_products': Product.objects.count(),
        'total_reviews': Review.objects.count(),
        'total_orders': Order.objects.count(),
        'featured_products': Product.objects.filter(is_featured=True, status='published')[:5],
        'recent_products': Product.objects.filter(status='published').order_by('-created_at')[:5],
        'top_rated_products': Product.objects.filter(status='published').order_by('-rating')[:5],
    }
    return render(request, 'models_demo/index.html', context)


def category_list(request):
    categories = Category.objects.annotate(
        product_count=Count('products')
    ).filter(is_active=True)
    
    context = {
        'categories': categories,
    }
    return render(request, 'models_demo/category_list.html', context)


def product_list(request):
    products = Product.objects.select_related('category').filter(status='published')
    
    # Filter theo danh mục
    category_id = request.GET.get('category')
    if category_id:
        products = products.filter(category_id=category_id)
    
    # Filter theo giá
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')
    if min_price:
        products = products.filter(price__gte=min_price)
    if max_price:
        products = products.filter(price__lte=max_price)
    
    # Search theo tên
    search_query = request.GET.get('search')
    if search_query:
        products = products.filter(
            Q(name__icontains=search_query) | 
            Q(description__icontains=search_query)
        )
    
    # Sắp xếp
    sort_by = request.GET.get('sort', '-created_at')
    if sort_by == 'price':
        products = products.order_by('price')
    elif sort_by == '-price':
        products = products.order_by('-price')
    elif sort_by == 'rating':
        products = products.order_by('-rating')
    else:
        products = products.order_by('-created_at')
    
    categories = Category.objects.filter(is_active=True)
    
    context = {
        'products': products,
        'categories': categories,
        'current_category': category_id,
        'current_sort': sort_by,
        'search_query': search_query,
    }
    return render(request, 'models_demo/product_list.html', context)


def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk, status='published')
    reviews = product.reviews.select_related('user').order_by('-created_at')
    related_products = Product.objects.filter(
        category=product.category,
        status='published'
    ).exclude(pk=pk)[:4]
    
    context = {
        'product': product,
        'reviews': reviews,
        'related_products': related_products,
    }
    return render(request, 'models_demo/product_detail.html', context)


def review_list(request):
    reviews = Review.objects.select_related('product', 'user').order_by('-created_at')
    
    # Filter theo rating
    rating = request.GET.get('rating')
    if rating:
        reviews = reviews.filter(rating=rating)
    
    # Filter theo verified purchase
    verified = request.GET.get('verified')
    if verified == 'true':
        reviews = reviews.filter(is_verified_purchase=True)
    
    context = {
        'reviews': reviews,
        'current_rating': rating,
        'current_verified': verified,
    }
    return render(request, 'models_demo/review_list.html', context)


def tag_list(request):
    tags = Tag.objects.annotate(
        product_count=Count('products')
    ).order_by('name')
    
    context = {
        'tags': tags,
    }
    return render(request, 'models_demo/tag_list.html', context)


def order_list(request):
    """Danh sách đơn hàng (chỉ admin có thể xem)"""
    if not request.user.is_staff:
        return render(request, 'models_demo/access_denied.html')
    
    orders = Order.objects.select_related('user').order_by('-created_at')
    
    # Filter theo status
    status = request.GET.get('status')
    if status:
        orders = orders.filter(status=status)
    
    context = {
        'orders': orders,
        'current_status': status,
    }
    return render(request, 'models_demo/order_list.html', context)

from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Q, Avg
from django.core.paginator import Paginator
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import Category, Product, ProductReview
from decimal import Decimal


def home_view(request):
    featured_categories = Category.objects.filter(is_featured=True)[:8]
    if not featured_categories.exists():
        featured_categories = Category.objects.all()[:8]

    # Best deals (products with greatest discount)
    deal_products = Product.objects.filter(is_available=True, discount_price__isnull=False).order_by('-discount_price')[:8]

    # Best sellers / featured
    featured_products = Product.objects.filter(is_available=True, is_featured=True)[:8]
    if not featured_products.exists():
        featured_products = Product.objects.filter(is_available=True).order_by('-rating')[:8]

    # New arrivals
    new_arrivals = Product.objects.filter(is_available=True).order_by('-created_at')[:8]

    context = {
        'featured_categories': featured_categories,
        'deal_products': deal_products,
        'featured_products': featured_products,
        'new_arrivals': new_arrivals,
    }
    return render(request, 'products/home.html', context)


def product_list_view(request, category_slug=None):
    category = None
    categories = Category.objects.all()
    products = Product.objects.filter(is_available=True)

    # Filter by category if slug is provided
    if category_slug:
        category = get_object_or_404(Category, slug=category_slug)
        products = products.filter(category=category)

    # Search query
    query = request.GET.get('q', '').strip()
    selected_category_id = request.GET.get('cat', '').strip()

    if selected_category_id and selected_category_id.isdigit():
        products = products.filter(category_id=int(selected_category_id))
        category = Category.objects.filter(id=int(selected_category_id)).first()

    if query:
        products = products.filter(
            Q(name__icontains=query) |
            Q(brand__icontains=query) |
            Q(description__icontains=query) |
            Q(category__name__icontains=query)
        ).distinct()

    # Filter by price range
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')
    if min_price and min_price.isdigit():
        products = products.filter(price__gte=Decimal(min_price))
    if max_price and max_price.isdigit():
        products = products.filter(price__lte=Decimal(max_price))

    # In stock filter
    in_stock_only = request.GET.get('in_stock')
    if in_stock_only == '1':
        products = products.filter(stock__gt=0)

    # Sorting
    sort_by = request.GET.get('sort', 'newest')
    if sort_by == 'price_asc':
        products = products.order_by('price')
    elif sort_by == 'price_desc':
        products = products.order_by('-price')
    elif sort_by == 'rating':
        products = products.order_by('-rating', '-num_reviews')
    elif sort_by == 'popularity':
        products = products.order_by('-num_reviews', '-rating')
    else:  # newest
        products = products.order_by('-created_at')

    # Pagination: 12 products per page
    paginator = Paginator(products, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Clean GET parameters for pagination links
    query_params = request.GET.copy()
    if 'page' in query_params:
        del query_params['page']
    pagination_params = query_params.urlencode()

    context = {
        'category': category,
        'categories': categories,
        'products': page_obj,
        'total_count': products.count(),
        'query': query,
        'sort_by': sort_by,
        'min_price': min_price or '',
        'max_price': max_price or '',
        'in_stock_only': in_stock_only == '1',
        'pagination_params': pagination_params,
    }
    return render(request, 'products/product_list.html', context)


def product_detail_view(request, slug):
    product = get_object_or_404(Product, slug=slug)
    related_products = Product.objects.filter(
        category=product.category, 
        is_available=True
    ).exclude(id=product.id)[:4]
    
    reviews = product.reviews.select_related('user').all()
    user_has_reviewed = False
    if request.user.is_authenticated:
        user_has_reviewed = reviews.filter(user=request.user).exists()

    context = {
        'product': product,
        'related_products': related_products,
        'reviews': reviews,
        'user_has_reviewed': user_has_reviewed,
    }
    return render(request, 'products/product_detail.html', context)


@login_required
def add_review_view(request, slug):
    product = get_object_or_404(Product, slug=slug)
    if request.method == 'POST':
        rating = request.POST.get('rating', '5')
        comment = request.POST.get('comment', '').strip()

        if not comment:
            messages.error(request, "Review comment cannot be empty.")
            return redirect('products:product_detail', slug=product.slug)

        try:
            rating_int = int(rating)
            if rating_int < 1 or rating_int > 5:
                rating_int = 5
        except ValueError:
            rating_int = 5

        # Check existing review or create new
        review, created = ProductReview.objects.update_or_create(
            product=product,
            user=request.user,
            defaults={'rating': rating_int, 'comment': comment}
        )

        # Recalculate average rating
        avg_rating = product.reviews.aggregate(Avg('rating'))['rating__avg'] or 5.0
        product.rating = round(Decimal(str(avg_rating)), 2)
        product.num_reviews = product.reviews.count()
        product.save()

        messages.success(request, "Thank you! Your review has been submitted successfully.")

    return redirect('products:product_detail', slug=product.slug)

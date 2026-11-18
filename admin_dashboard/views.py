from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import user_passes_test
from django.contrib import messages
from django.db.models import Sum, Count, Q
from django.contrib.auth.models import User
from django.core.paginator import Paginator

from products.models import Product, Category
from orders.models import Order, OrderItem
from .forms import AdminProductForm, AdminCategoryForm, AdminOrderStatusForm


def staff_required(view_func):
    return user_passes_test(lambda u: u.is_authenticated and (u.is_staff or u.is_superuser), login_url='accounts:login')(view_func)


@staff_required
def dashboard_home(request):
    total_revenue = Order.objects.exclude(status='Cancelled').aggregate(Sum('grand_total'))['grand_total__sum'] or 0
    total_orders = Order.objects.count()
    pending_orders = Order.objects.filter(status='Pending').count()
    processing_orders = Order.objects.filter(status='Processing').count()
    delivered_orders = Order.objects.filter(status='Delivered').count()
    
    total_products = Product.objects.count()
    low_stock_products = Product.objects.filter(stock__lte=5).order_by('stock')
    out_of_stock_count = Product.objects.filter(stock=0).count()
    total_customers = User.objects.filter(is_staff=False).count()

    recent_orders = Order.objects.select_related('user').order_by('-created_at')[:8]

    context = {
        'total_revenue': total_revenue,
        'total_orders': total_orders,
        'pending_orders': pending_orders,
        'processing_orders': processing_orders,
        'delivered_orders': delivered_orders,
        'total_products': total_products,
        'low_stock_products': low_stock_products,
        'out_of_stock_count': out_of_stock_count,
        'total_customers': total_customers,
        'recent_orders': recent_orders,
    }
    return render(request, 'admin_dashboard/index.html', context)


@staff_required
def product_list(request):
    query = request.GET.get('q', '').strip()
    category_id = request.GET.get('cat', '')
    stock_status = request.GET.get('stock', '')

    products = Product.objects.select_related('category').order_by('-created_at')

    if query:
        products = products.filter(
            Q(name__icontains=query) |
            Q(brand__icontains=query) |
            Q(category__name__icontains=query)
        )

    if category_id and category_id.isdigit():
        products = products.filter(category_id=int(category_id))

    if stock_status == 'low':
        products = products.filter(stock__lte=5, stock__gt=0)
    elif stock_status == 'out':
        products = products.filter(stock=0)

    paginator = Paginator(products, 15)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    categories = Category.objects.all()

    context = {
        'products': page_obj,
        'categories': categories,
        'query': query,
        'selected_cat': category_id,
        'stock_status': stock_status,
    }
    return render(request, 'admin_dashboard/product_list.html', context)


@staff_required
def product_add(request):
    if request.method == 'POST':
        form = AdminProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save()
            messages.success(request, f'Product "{product.name}" was added successfully!')
            return redirect('admin_dashboard:product_list')
        else:
            messages.error(request, "Please correct the form errors.")
    else:
        form = AdminProductForm()

    return render(request, 'admin_dashboard/product_form.html', {
        'form': form,
        'title': 'Add New Product',
        'is_edit': False,
    })


@staff_required
def product_edit(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        form = AdminProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            messages.success(request, f'Product "{product.name}" was updated successfully!')
            return redirect('admin_dashboard:product_list')
        else:
            messages.error(request, "Please correct the form errors.")
    else:
        form = AdminProductForm(instance=product)

    return render(request, 'admin_dashboard/product_form.html', {
        'form': form,
        'title': f'Edit Product: {product.name}',
        'is_edit': True,
        'product': product,
    })


@staff_required
def product_delete(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        product_name = product.name
        product.delete()
        messages.success(request, f'Product "{product_name}" has been deleted.')
        return redirect('admin_dashboard:product_list')

    return render(request, 'admin_dashboard/product_confirm_delete.html', {'product': product})


@staff_required
def category_list(request):
    categories = Category.objects.annotate(product_count=Count('products')).order_by('name')
    return render(request, 'admin_dashboard/category_list.html', {'categories': categories})


@staff_required
def category_add(request):
    if request.method == 'POST':
        form = AdminCategoryForm(request.POST, request.FILES)
        if form.is_valid():
            cat = form.save()
            messages.success(request, f'Category "{cat.name}" added successfully!')
            return redirect('admin_dashboard:category_list')
    else:
        form = AdminCategoryForm()

    return render(request, 'admin_dashboard/category_form.html', {'form': form, 'title': 'Add Category'})


@staff_required
def category_edit(request, pk):
    category = get_object_or_404(Category, pk=pk)
    if request.method == 'POST':
        form = AdminCategoryForm(request.POST, request.FILES, instance=category)
        if form.is_valid():
            form.save()
            messages.success(request, f'Category "{category.name}" updated successfully!')
            return redirect('admin_dashboard:category_list')
    else:
        form = AdminCategoryForm(instance=category)

    return render(request, 'admin_dashboard/category_form.html', {'form': form, 'title': f'Edit Category: {category.name}'})


@staff_required
def category_delete(request, pk):
    category = get_object_or_404(Category, pk=pk)
    if request.method == 'POST':
        name = category.name
        category.delete()
        messages.success(request, f'Category "{name}" removed.')
        return redirect('admin_dashboard:category_list')
    return render(request, 'admin_dashboard/category_confirm_delete.html', {'category': category})


@staff_required
def order_list(request):
    status_filter = request.GET.get('status', 'all')
    search_q = request.GET.get('q', '').strip()

    orders = Order.objects.select_related('user').order_by('-created_at')

    if status_filter != 'all':
        orders = orders.filter(status=status_filter)

    if search_q:
        orders = orders.filter(
            Q(order_number__icontains=search_q) |
            Q(full_name__icontains=search_q) |
            Q(user__username__icontains=search_q) |
            Q(phone__icontains=search_q)
        )

    paginator = Paginator(orders, 15)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'orders': page_obj,
        'status_filter': status_filter,
        'search_q': search_q,
    }
    return render(request, 'admin_dashboard/order_list.html', context)


@staff_required
def order_detail_manage(request, order_number):
    order = get_object_or_404(Order, order_number=order_number)

    if request.method == 'POST':
        form = AdminOrderStatusForm(request.POST, instance=order)
        if form.is_valid():
            form.save()
            messages.success(request, f"Order #{order.order_number} status updated to {order.status}!")
            return redirect('admin_dashboard:order_detail', order_number=order.order_number)
    else:
        form = AdminOrderStatusForm(instance=order)

    return render(request, 'admin_dashboard/order_detail.html', {
        'order': order,
        'form': form,
    })


@staff_required
def customer_list(request):
    customers = User.objects.filter(is_staff=False).annotate(
        total_orders=Count('orders'),
        total_spent=Sum('orders__grand_total')
    ).order_by('-date_joined')

    paginator = Paginator(customers, 15)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'admin_dashboard/customer_list.html', {'customers': page_obj})


@staff_required
def stock_manage(request):
    if request.method == 'POST':
        # Batch stock update
        for key, value in request.POST.items():
            if key.startswith('stock_'):
                product_id = key.split('_')[1]
                try:
                    new_stock = int(value)
                    if new_stock >= 0:
                        Product.objects.filter(id=product_id).update(
                            stock=new_stock,
                            is_available=(new_stock > 0)
                        )
                except ValueError:
                    pass
        messages.success(request, "Product inventory stocks updated successfully!")
        return redirect('admin_dashboard:stock_manage')

    products = Product.objects.select_related('category').order_by('stock')
    return render(request, 'admin_dashboard/stock_manage.html', {'products': products})

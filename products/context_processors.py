from .models import Category


def categories_context(request):
    try:
        categories = Category.objects.all().order_by('name')
    except Exception:
        categories = []
    return {
        'all_categories': categories
    }

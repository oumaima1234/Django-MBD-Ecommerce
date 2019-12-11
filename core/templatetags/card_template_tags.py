from django import template
from core.models import Order

register = template.Library()

@register.filter # decorator : to use function name as a filter
def card_item_count(user):
    if user.is_authenticated:
        qs = Order.objects.filter(user=user, ordered=False)
        if qs.exists():
            return qs[0].items.count()
    return 0
from django import template

register = template.Library()


@register.filter
def get_service_price(pricelist, service):
    try:
        return pricelist.get(service=service).price
    except pricelist.model.DoesNotExist:
        return None

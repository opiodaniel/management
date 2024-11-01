from django import template

register = template.Library()


@register.filter(name='add_commas')
def add_commas(value):
    """
    Add commas to a number string.
    """
    try:
        value = int(value)
        return "{:,}".format(value)
    except (TypeError, ValueError):
        return value


@register.filter(name='to_11')
def to_range(value):
    return range(value)


@register.filter(name='has_group')
def has_group(user, group_name):
    return user.groups.filter(name=group_name).exists()
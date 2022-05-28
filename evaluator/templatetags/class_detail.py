from django import template

register = template.Library()


@register.filter(name='get_my_submission')
def get_my_submission(value, arg):
    try:
        return value.get_my_submission(user=arg).pk
    except AttributeError:
        return None

from django import template

register = template.Library()

EN_TO_FA = str.maketrans("0123456789", "۰۱۲۳۴۵۶۷۸۹")


@register.filter
def persian_digits(value):
    if value is None:
        return ""

    return str(value).translate(EN_TO_FA)


@register.filter
def toman(value):
    if value is None or value == "":
        return ""

    try:
        value = int(value)
    except (TypeError, ValueError):
        return str(value).translate(EN_TO_FA)

    formatted = f"{value:,}".replace(",", "٬")
    return formatted.translate(EN_TO_FA)
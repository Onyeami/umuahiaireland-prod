from django import template
from django.utils.safestring import mark_safe

register = template.Library()


@register.simple_tag(takes_context=True)
def page_title_with_context(context, custom_title=None):
    """
    Generate a complete page title with context
    Usage: {% page_title_with_context "Custom Title" %}
    """
    request = context.get("request")
    page_title = context.get("page_title", "")
    page_type = context.get("page_type", "")

    if custom_title:
        title = custom_title
    elif page_title and page_title != "Page":
        title = page_title
    else:
        title = "Umuahia Community Ireland"

    # Build the full title
    parts = []
    if title and title != "Umuahia Community Ireland":
        parts.append(title)

    if page_type:
        parts.append(page_type)

    parts.append("Umuahia Community Ireland")

    return " | ".join(parts)


@register.inclusion_tag("_includes/breadcrumb.html", takes_context=True)
def show_breadcrumb(context):
    """
    Display breadcrumb navigation
    Usage: {% show_breadcrumb %}
    """
    return context


@register.simple_tag(takes_context=True)
def page_heading(context, custom_heading=None):
    """
    Generate page heading based on context
    Usage: {% page_heading %} or {% page_heading "Custom Heading" %}
    """
    if custom_heading:
        return custom_heading

    page_title = context.get("page_title", "Page")
    return page_title if page_title != "Page" else "Umuahia Community Ireland"


@register.filter
def page_icon(page_title):
    """
    Get FontAwesome icon for page based on title
    Usage: {{ page_title|page_icon }}
    """
    icon_mapping = {
        # Admin icons
        "Dashboard": "fas fa-tachometer-alt",
        "Manage Members": "fas fa-users",
        "Manage Minutes": "fas fa-file-alt",
        "Financial Checkbooks": "fas fa-book",
        "Settings": "fas fa-cog",
        "Blog Management": "fas fa-blog",
        "Manage Blog Posts": "fas fa-newspaper",
        "Create Blog Post": "fas fa-plus",
        "Edit Blog Post": "fas fa-edit",
        "Manage Comments": "fas fa-comments",
        "Manage Categories": "fas fa-tags",
        "Create User": "fas fa-user-plus",
        "Edit User": "fas fa-user-edit",
        # User icons
        "My Profile": "fas fa-user",
        "Meeting Minutes": "fas fa-file-alt",
        # Blog icons
        "Blog Posts": "fas fa-newspaper",
        "Blog Post": "fas fa-newspaper",
        "Search Results": "fas fa-search",
        # Public icons
        "Home": "fas fa-home",
        "Contact Us": "fas fa-envelope",
        "Privacy Statement": "fas fa-shield-alt",
        # Auth icons
        "Login": "fas fa-sign-in-alt",
        "Register": "fas fa-user-plus",
        "Password Reset": "fas fa-key",
    }

    return icon_mapping.get(page_title, "fas fa-file")

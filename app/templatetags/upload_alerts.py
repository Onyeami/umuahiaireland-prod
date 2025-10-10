from django import template
from django.utils.safestring import mark_safe
import json

register = template.Library()

@register.inclusion_tag('_includes/upload_alerts_scripts.html')
def upload_alerts_scripts():
    """Include upload alert JavaScript and CSS"""
    return {}

@register.simple_tag
def upload_results_data(form):
    """Get upload results as JSON data attribute for JavaScript"""
    if hasattr(form, 'get_upload_results_json'):
        return mark_safe(f'data-upload-results=\'{form.get_upload_results_json()}\'')
    return ''

@register.filter
def add_upload_class(field, css_class="file-upload-form"):
    """Add upload-related CSS class to form fields"""
    if hasattr(field, 'as_widget'):
        return field.as_widget(attrs={'class': css_class})
    return field

@register.inclusion_tag('_includes/file_upload_preview.html')
def file_upload_preview(field):
    """Render file upload preview component"""
    return {
        'field': field,
        'field_id': field.auto_id if hasattr(field, 'auto_id') else 'file-input',
        'field_name': field.name if hasattr(field, 'name') else 'file'
    }

@register.simple_tag
def alert_enabled_form_attrs(form):
    """Add data attributes for alert-enabled forms"""
    attrs = [
        'data-upload-alerts="true"',
        'data-form-type="file-upload"'
    ]
    
    if hasattr(form, 'get_upload_results_json'):
        upload_data = form.get_upload_results_json()
        if upload_data and upload_data != '{}':
            attrs.append(f'data-upload-results=\'{upload_data}\'')
    
    return mark_safe(' '.join(attrs))
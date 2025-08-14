from django.conf import settings

def paypal_settings(request):
    """
    Make PayPal settings available in all templates.
    """
    return {
        'paypal_client_id': getattr(settings, 'PAYPAL_CLIENT_ID', ''),
        'paypal_secret': getattr(settings, 'PAYPAL_SECRET', ''),
    }

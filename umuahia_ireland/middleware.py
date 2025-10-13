"""
Debug middleware to help identify CSRF issues
"""
import logging

logger = logging.getLogger(__name__)

class CSRFDebugMiddleware:
    """Middleware to debug CSRF token issues"""
    
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Log CSRF token information for POST requests
        if request.method == 'POST':
            csrf_token = request.META.get('CSRF_COOKIE')
            post_token = request.POST.get('csrfmiddlewaretoken')
            
            logger.info(f"POST request to {request.path}")
            logger.info(f"CSRF Cookie: {csrf_token}")
            logger.info(f"POST CSRF Token: {post_token}")
            logger.info(f"User Agent: {request.META.get('HTTP_USER_AGENT')}")
            logger.info(f"Referer: {request.META.get('HTTP_REFERER')}")
            
            # Print to console for immediate debugging
            print(f"🔍 CSRF Debug - POST to {request.path}")
            print(f"   CSRF Cookie: {csrf_token}")
            print(f"   POST Token: {post_token}")
            print(f"   Match: {csrf_token == post_token if csrf_token and post_token else 'No'}")

        response = self.get_response(request)
        return response
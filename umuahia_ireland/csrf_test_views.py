from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.middleware.csrf import get_token

def csrf_test(request):
    """Simple CSRF test view"""
    if request.method == 'POST':
        return JsonResponse({
            'success': True,
            'message': 'CSRF test successful!',
            'csrf_token': get_token(request)
        })
    
    # GET request - show test form
    context = {
        'csrf_token': get_token(request)
    }
    return render(request, 'csrf_test.html', context)
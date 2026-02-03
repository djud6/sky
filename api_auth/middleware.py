from django.http import JsonResponse
from django.utils.deprecation import MiddlewareMixin
from django.core.cache import cache
import time

class LoginRateLimitMiddleware(MiddlewareMixin):
    """Rate limiting for login attempts"""
    
    def process_request(self, request):
        if request.path == '/api-auth/v1/Login' and request.method == 'POST':
            ip = self.get_client_ip(request)
            cache_key = f"login_attempts_{ip}"
            
            # Get current attempts
            attempts = cache.get(cache_key, 0)
            
            if attempts >= 5:  # Max 5 attempts per 15 minutes
                return JsonResponse({
                    'success': False,
                    'message': 'Too many login attempts. Please try again later.'
                }, status=429)
    
    def process_response(self, request, response):
        if (request.path == '/api-auth/v1/Login' and 
            request.method == 'POST' and 
            response.status_code == 400):
            
            ip = self.get_client_ip(request)
            cache_key = f"login_attempts_{ip}"
            
            # Increment failed attempts
            attempts = cache.get(cache_key, 0) + 1
            cache.set(cache_key, attempts, 900)  # 15 minutes
        
        return response
    
    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            return x_forwarded_for.split(',')[0]
        return request.META.get('REMOTE_ADDR')
    


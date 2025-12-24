from django.utils.deprecation import MiddlewareMixin
from django.core.cache import cache
from django.http import JsonResponse
from accounts.models import AuditLog
from accounts.utils import get_client_ip, get_user_agent
import logging

logger = logging.getLogger('security')


class AuditMiddleware(MiddlewareMixin):
    """
    Middleware pour enregistrer toutes les requêtes importantes
    """
    
    AUDITED_PATHS = [
        '/api/auth/login',
        '/api/auth/register',
        '/api/transactions/',
        '/api/profile/',
        '/api/beneficiaries/',
    ]
    
    def process_request(self, request):
        """Enregistrer les informations de la requête"""
        # Vérifier si le chemin doit être audité
        if any(request.path.startswith(path) for path in self.AUDITED_PATHS):
            request.audit_info = {
                'ip_address': get_client_ip(request),
                'user_agent': get_user_agent(request),
                'path': request.path,
                'method': request.method,
            }
        return None
    
    def process_response(self, request, response):
        """Enregistrer la réponse si nécessaire"""
        if hasattr(request, 'audit_info') and hasattr(request, 'user') and request.user.is_authenticated:
            # Enregistrer dans les logs si la réponse est un échec
            if response.status_code >= 400:
                logger.warning(
                    f"Failed request: {request.method} {request.path} - "
                    f"Status: {response.status_code} - "
                    f"User: {request.user.email} - "
                    f"IP: {request.audit_info['ip_address']}"
                )
        
        return response


class RateLimitMiddleware(MiddlewareMixin):
    """
    Middleware pour limiter le nombre de requêtes par IP
    """
    
    # Limites par endpoint (requêtes par minute)
    RATE_LIMITS = {
        '/api/auth/login': (5, 60),  # 5 requêtes par minute
        '/api/auth/register': (3, 60),  # 3 requêtes par minute
        '/api/transactions/initiate': (10, 60),  # 10 requêtes par minute
        '/api/transactions/verify-and-execute': (10, 60),
        '/api/otp/send': (5, 60),
    }
    
    def process_request(self, request):
        """Vérifier les limites de taux"""
        # Ignorer les requêtes GET
        if request.method == 'GET':
            return None
        
        # Vérifier si le chemin a une limite
        rate_limit = None
        for path, limit in self.RATE_LIMITS.items():
            if request.path.startswith(path):
                rate_limit = limit
                break
        
        if not rate_limit:
            return None
        
        max_requests, time_window = rate_limit
        
        # Créer une clé de cache basée sur l'IP et le chemin
        ip_address = get_client_ip(request)
        cache_key = f'rate_limit:{ip_address}:{request.path}'
        
        # Récupérer le compteur actuel
        request_count = cache.get(cache_key, 0)
        
        if request_count >= max_requests:
            logger.warning(
                f"Rate limit exceeded for IP {ip_address} on {request.path}"
            )
            
            # Enregistrer dans les logs de sécurité
            if hasattr(request, 'user') and request.user.is_authenticated:
                try:
                    AuditLog.objects.create(
                        user=request.user,
                        action='rate_limit_exceeded',
                        status='failed',
                        ip_address=ip_address,
                        user_agent=get_user_agent(request),
                        description=f"Rate limit exceeded on {request.path}"
                    )
                except Exception as e:
                    logger.error(f"Failed to create audit log: {str(e)}")
            
            return JsonResponse({
                'success': False,
                'error': 'Too many requests. Please try again later.',
                'retry_after': time_window
            }, status=429)
        
        # Incrémenter le compteur
        cache.set(cache_key, request_count + 1, timeout=time_window)
        
        return None


class SecurityHeadersMiddleware(MiddlewareMixin):
    """
    Middleware pour ajouter des en-têtes de sécurité
    """
    
    def process_response(self, request, response):
        """Ajouter les en-têtes de sécurité"""
        # Content Security Policy
        response['Content-Security-Policy'] = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' 'unsafe-eval'; "
            "style-src 'self' 'unsafe-inline'; "
            "img-src 'self' data: https:; "
            "font-src 'self' data:; "
            "connect-src 'self'; "
            "frame-ancestors 'none';"
        )
        
        # X-Content-Type-Options
        response['X-Content-Type-Options'] = 'nosniff'
        
        # X-Frame-Options
        response['X-Frame-Options'] = 'DENY'
        
        # X-XSS-Protection
        response['X-XSS-Protection'] = '1; mode=block'
        
        # Referrer-Policy
        response['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        
        # Permissions-Policy
        response['Permissions-Policy'] = (
            'geolocation=(), microphone=(), camera=(), '
            'payment=(), usb=(), magnetometer=(), gyroscope=()'
        )
        
        return response


class IPWhitelistMiddleware(MiddlewareMixin):
    """
    Middleware optionnel pour restreindre l'accès par IP
    (à activer uniquement si nécessaire)
    """
    
    # Liste des IPs autorisées (vide = toutes les IPs)
    WHITELIST = []
    
    def process_request(self, request):
        """Vérifier si l'IP est dans la whitelist"""
        if not self.WHITELIST:
            return None
        
        ip_address = get_client_ip(request)
        
        if ip_address not in self.WHITELIST:
            logger.warning(f"Access denied for IP {ip_address}")
            
            return JsonResponse({
                'success': False,
                'error': 'Access denied'
            }, status=403)
        
        return None


class SuspiciousActivityMiddleware(MiddlewareMixin):
    """
    Middleware pour détecter les activités suspectes
    """
    
    def process_request(self, request):
        """Détecter les patterns suspects"""
        ip_address = get_client_ip(request)
        user_agent = get_user_agent(request)
        
        # Vérifier les user agents suspects
        suspicious_agents = ['bot', 'crawler', 'spider', 'scraper']
        if any(agent in user_agent.lower() for agent in suspicious_agents):
            logger.warning(f"Suspicious user agent detected: {user_agent} from IP {ip_address}")
        
        # Vérifier les tentatives d'injection SQL
        suspicious_patterns = ["'", '"', '--', '/*', '*/', 'DROP', 'DELETE', 'INSERT', 'UPDATE']
        
        for key, value in request.GET.items():
            if any(pattern in str(value).upper() for pattern in suspicious_patterns):
                logger.warning(
                    f"Potential SQL injection attempt detected in GET params: "
                    f"{key}={value} from IP {ip_address}"
                )
                
                if hasattr(request, 'user') and request.user.is_authenticated:
                    try:
                        AuditLog.objects.create(
                            user=request.user,
                            action='suspicious_activity',
                            status='failed',
                            ip_address=ip_address,
                            user_agent=user_agent,
                            description=f"Potential SQL injection in GET: {key}={value}"
                        )
                    except:
                        pass
        
        return None
import json
from time import time
from django.utils.deprecation import MiddlewareMixin
from .models import Bitacora, DetalleBitacora

def _get_client_ip(request):
    xff = request.META.get('HTTP_X_FORWARDED_FOR')
    if xff:
        return xff.split(',')[0].strip()
    return request.META.get('REMOTE_ADDR')

class AuditMiddleware(MiddlewareMixin):
    def process_request(self, request):
        request._audit_started_at = time()
        return None

    def process_response(self, request, response):
        try:
            session_key = getattr(request.session, 'session_key', None)
            user = getattr(request, 'user', None)
            if not session_key and user and user.is_authenticated:
                request.session.save()
                session_key = request.session.session_key

            bitacora = None
            if session_key:
                bitacora = Bitacora.objects.filter(session_key=session_key).order_by('-login_at').first()
                if not bitacora and user and user.is_authenticated:
                    bitacora = Bitacora.objects.create(
                        user=user, session_key=session_key, ip=_get_client_ip(request),
                        user_agent=request.META.get('HTTP_USER_AGENT','')
                    )

            if bitacora:
                payload = None
                if request.method in ('POST','PUT','PATCH','DELETE'):
                    try:
                        body = request.body.decode('utf-8')[:4000]
                        payload = json.loads(body) if body else None
                    except Exception:
                        payload = None

                DetalleBitacora.objects.create(
                    bitacora=bitacora,
                    accion='request',
                    method=request.method,
                    path=request.path[:512],
                    status_code=getattr(response, 'status_code', None),
                    detalle=f"Duración {round((time()-getattr(request,'_audit_started_at',time()))*1000)} ms",
                    payload=payload
                )
        except Exception:
            pass
        return response

from django.contrib.auth.signals import user_logged_in, user_logged_out, user_login_failed
from django.dispatch import receiver
from django.utils import timezone
from .models import Bitacora, DetalleBitacora

def _get_client_ip(request):
    xff = request.META.get('HTTP_X_FORWARDED_FOR')
    if xff:
        return xff.split(',')[0].strip()
    return request.META.get('REMOTE_ADDR')

def _device_from_ua(ua: str) -> str:
    if not ua: return ''
    low = ua.lower()
    if 'mobile' in low: return 'mobile'
    if 'tablet' in low or 'ipad' in low: return 'tablet'
    return 'desktop'

@receiver(user_logged_in)
def on_login(sender, request, user, **kwargs):
    if not request.session.session_key:
        request.session.save()
    session_key = request.session.session_key or ''
    ip = _get_client_ip(request)
    ua = request.META.get('HTTP_USER_AGENT', '')
    device = _device_from_ua(ua)
    Bitacora.objects.create(
        user=user, session_key=session_key, ip=ip,
        user_agent=ua, dispositivo=device, login_at=timezone.now()
    )

@receiver(user_logged_out)
def on_logout(sender, request, user, **kwargs):
    sk = getattr(request.session, 'session_key', '')
    if not sk:
        return
    Bitacora.objects.filter(session_key=sk, logout_at__isnull=True).update(logout_at=timezone.now())

@receiver(user_login_failed)
def on_login_failed(sender, credentials, request, **kwargs):
    ip = _get_client_ip(request) if request else None
    ua = request.META.get('HTTP_USER_AGENT', '') if request else ''
    b = Bitacora.objects.create(
        user=None, session_key='-login-failed-', ip=ip, user_agent=ua,
        dispositivo=_device_from_ua(ua)
    )
    DetalleBitacora.objects.create(
        bitacora=b,
        accion='login_failed',
        detalle=f"Intento fallido username/email={credentials.get('username')}"
    )

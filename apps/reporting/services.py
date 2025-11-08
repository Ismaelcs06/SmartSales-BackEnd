import csv, json
from pathlib import Path
from django.conf import settings
from django.utils import timezone
from datetime import datetime
from apps.sales.models import Venta

def ventas_por_dia_queryset(date_from=None, date_to=None):
    qs = Venta.objects.all()
    if date_from:
        qs = qs.filter(fecha_venta__date__gte=date_from)
    if date_to:
        qs = qs.filter(fecha_venta__date__lte=date_to)
    # agregamos en Python por simplicidad (podrías usar annotate/TruncDate)
    data = {}
    for v in qs.only('fecha_venta','total'):
        d = v.fecha_venta.date().isoformat()
        data[d] = data.get(d, 0) + float(v.total)
    rows = [{'fecha': k, 'total': round(v, 2)} for k, v in sorted(data.items())]
    return rows

def ensure_reports_dir():
    reports_dir = Path(settings.MEDIA_ROOT) / 'reports'
    reports_dir.mkdir(parents=True, exist_ok=True)
    return reports_dir

def export_rows(rows, formato='CSV', base_filename='reporte'):
    reports_dir = ensure_reports_dir()
    timestamp = timezone.now().strftime('%Y%m%d_%H%M%S')
    if formato == 'CSV':
        fname = f"{base_filename}_{timestamp}.csv"
        fpath = reports_dir / fname
        with open(fpath, 'w', newline='', encoding='utf-8') as f:
            if rows:
                writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
                writer.writeheader()
                writer.writerows(rows)
            else:
                f.write("")  # vacío con headers omitidos
        return f"reports/{fname}"
    elif formato == 'JSON':
        fname = f"{base_filename}_{timestamp}.json"
        fpath = reports_dir / fname
        with open(fpath, 'w', encoding='utf-8') as f:
            json.dump(rows, f, ensure_ascii=False, indent=2)
        return f"reports/{fname}"
    else:
        raise ValueError("Formato no soportado")

def generar_reporte(tipo, formato='CSV', params=None):
    params = params or {}
    date_from = params.get('date_from')  # 'YYYY-MM-DD' (opcional)
    date_to   = params.get('date_to')
    if date_from and isinstance(date_from, str):
        date_from = datetime.fromisoformat(date_from).date()
    if date_to and isinstance(date_to, str):
        date_to = datetime.fromisoformat(date_to).date()

    if tipo == 'ventas':
        rows = ventas_por_dia_queryset(date_from, date_to)
        ruta_rel = export_rows(rows, formato=formato, base_filename='ventas_por_dia')
        descripcion = f"Ventas por día {date_from or ''} - {date_to or ''}".strip()
        return ruta_rel, descripcion

    # Future: otros tipos (clientes, productos, IA, etc.)
    raise ValueError("Tipo de reporte no soportado")

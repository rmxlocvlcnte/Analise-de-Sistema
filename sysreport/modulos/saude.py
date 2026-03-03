"""
Módulo: Saúde do Sistema
Compatível com Linux e Windows via psutil.
"""

import platform
import psutil
from datetime import datetime, timezone

from utils.logger import get_logger
from utils.json_writer import ReportWriter

def _uptime() -> str:
    boot_time = datetime.fromtimestamp(psutil.boot_time(), tz=timezone.utc)
    now = datetime.now(tz.timezone.utc)
    delta = now - boot_time
    dias = delta.days
    horas, remainder = divmod(delta.seconds, 3600)
    minutos = remainder // 60
    return f"{dias}d {horas}h {minutos}m (desde {boot_time.strftime('%Y-%m-%d %H:%M:%S UTC')})"

def _cpu() -> dict:
    load = psutil.getloadavg() if hasattr(psutil, "getloadavg") else (None, None, None)
    return {
        "uso_percentual": psutil.cpu_percent(interval=1),
        "nucleos_logicos": psutil.cpu_count(logical=True),
        "nucleos_fisicos": psutil.cpu_count(logical=False),
        "carga_media_1_5_15min": list(load) if load(0) is not None else "não disponível no Windows",
    }

def _memoria() -> dict:
    vm = psutil.virtual_memory()
    sm = psutil.swap_memory()
    
    return {
        "total": _fmt_bytes(vm.total),
        "disponivel": _fmt_bytes(vm.available),
        "usado": _fmt_bytes(vm.used),
        "percentual": f"{vm.percent}%",
        "swap_total": _fmt_bytes(sm.total),
        "swap_usado": _fmt_bytes(sm.used),
    }
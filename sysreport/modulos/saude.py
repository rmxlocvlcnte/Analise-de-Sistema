"""
Módulo: Saúde do Sistema
"""

import platform
import psutil
from datetime import datetime, timezone

from utils.logger import get_logger
from utils.writerjson import ReportWriter

def _uptime() -> str:
    boot_time = datetime.fromtimestamp(psutil.boot_time(), tz=timezone.utc)
    now = datetime.now(tz=timezone.utc)
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
        "carga_media_1_5_15min": list(load) if load[0] is not None else "não disponível no Windows",
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

def _armazenamento() -> list[dict]:
    partitions = []
    for part in psutil.disk_partitions(all=False):
        try:
            uso = psutil.disk_usage(part.mountpoint)
            partitions.append({
                "dispositivo": part.device,
                "ponto_montagem": part.mountpoint,
                "sistema_arquivos": part.fstype,
                "total": _fmt_bytes(uso.total),
                "usado": _fmt_bytes(uso.used),
                "livre": _fmt_bytes(uso.free),
                "percentual": f"{uso.percent}%"
            })
        except PermissionError:
            continue
    return partitions

def _processos_top(n: int = 5) -> list[dict]:
    procs = []
    for proc in psutil.process_iter(["pid", "name", "username", "cpu_percent", "memory_percent"]):
        try:
            info = proc.info
            info["memory_percent"] = round(info["memory_percent"] or 0, 2)
            info["cpu_percent"] = round(info["cpu_percent"] or 0, 2)
            procs.append(info)
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    return sorted(procs, key=lambda p: p["memory_percent"], reverse=True)[:n]

def _fmt_bytes(b: int) -> str:
    for unit in ("B", "KB", "MB", "GB", "TB"):
        if b < 1024:
            return f"{b:.1f} {unit}"
        b /= 1024
    return f"{b:.1f} PB"

def analise(writer: ReportWriter) -> None:
    log = get_logger()
    log.info("saude_sis - iniciando")

    writer.add("plataforma", {
        "sistema": platform.system(),
        "versao": platform.version(),
        "arquitetura": platform.machine(),
        "python": platform.python_version(),
    })
    writer.add("tempo_online", _uptime())
    writer.add("cpu", _cpu())
    writer.add("memoria", _memoria())
    writer.add("armazenamento", _armazenamento())
    writer.add("processos_top5_mem", _processos_top(5))

    log.info("saude_sis - concluído")
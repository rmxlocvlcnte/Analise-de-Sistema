"""
Módulo: Logs de Autenticação
Linux -> journalctl + /var/log/auth.log
Windows -> Event Log via pywin32
"""

import platform
import subprocess
import re
from collections import Counter
from pathlib import Path

from utils.logger import get_logger
from utils.writerjson import ReportWriter

LINHAS_MAX = 3000
SISTEMA = platform.system()

# Análise para Linux

def _journalctl_erros() -> list[str]:
    """Erros ou Alertas nas útilmas 24 horas"""
    try:
        result=subprocess.run(
            ["journalctl", "-p", "err..alert", "--since", "24 hours ago", "--no-pager"],
            capture_output=True, text=True, timeout=30,
        )
        linhas = [
            l for l in result.stdout.splitlines()
            if re.search(r"failed|denied|unauthorized", l, re.IGNORECASE) 
        ]
        return linhas[:LINHAS_MAX]
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return ["journalctl não disponível"]

def _auth_log_brute_force() -> list[dict]:
    """IPs com tentativas de senha falha em /var/log/auth.log."""
    auth = Path("/var/log/auth.log")
    if not auth.exists():
        return []
    
    ips: list[str] = []
    pattern = re.compile(r"Failed password.*from\s+(\d+\.\d+\.\d+\.\d+)", re.IGNORECASE)
    try:
        with auth.open(encoding="utf-8", errors="replace") as f:
            for line in f:
                m = pattern.search(line)
                if m:
                    ips.append(m.group(1))
    except PermissionError:
        return [{"erro": "permissão negada para /var/log/auth.log"}]

    return [
        {"ip": ip, "tentativas": count}
        for ip, count in Counter(ips).most_common(20)
    ]

def _analise_linux(writer: ReportWriter) -> None:
    writer.add("erros_24h", _journalctl_erros())
    writer.add("brute_force_ssh", _auth_log_brute_force())

# Análise do Windows

def _analise_windows(writer: ReportWriter) -> None:
    """
    Lê o Event Log de Segurança do Windows.
    Requer permissões de Administrador.
    Importante: Instale o pywin32 para melhor funcionalidade: `pip install pywin32`
    """

    try:
        import win32evtlog
        import win32con

        hand = win32evtlog.OpenEventLog(None, "Security")
        flags = win32evtlog.EVENTLOG_BACKWARDS_READ | win32evtlog.EVENTLOG_SEQUENTIAL_READ

        falhas: list[dict] = []
        eventos = win32evtlog.ReadEventLog(hand, flags, 0)

        while eventos and len(falhas) < LINHAS_MAX:
            for ev in eventos:
                #ID de Evento 4625 = Falha de LogOn
                if ev.EventID & 0xFFFF == 4625:
                    falhas.append({
                        "horario": str(ev.TimeGenerated),
                        "mensagem": str(ev.StringInserts),
                    })
            eventos = win32evtlog.ReadEventLog(hand, flags, 0)

        win32evtlog.CloseEventLog(hand)
        writer.add("falhas_logon_windows", falhas)
    
    except ImportError:
        writer.add(
            "falhas_logon_windows",
            "pywin32 não instalado - instale com pip install pywin32",
        )

    except Exception as e:
        writer.add("falhas_logon_windows", f"erro ao ler Event Log: {e}")

# Ponto de Entrada

def analise(writer: ReportWriter) -> None:
    log = get_logger()
    log.info("analise_logs - iniciando")

    if SISTEMA == "Linux":
        _analise_linux(writer)
    elif SISTEMA == "Windows":
        _analise_windows(writer)
    else:
        writer.add("logs", f"{SISTEMA} não é suportado")

    log.info("analise_logs - concluída")
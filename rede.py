"""
Módulo: Análise de Rede
Compatibilidade com Windows e Linux
"""

import re
import psutil

from utils.logger import get_logger
from utils.json_writer import ReportWriter

PORTAS_SUSPEITAS = {21, 22, 23, 3389, 4444, 5900}

_STATUS_MAP = {
  "LISTEN": "escutando",
  "ESTABLISHED": "estabelecida",
  "CLOSE_WAIT": "aguardando encerramento",
  "TIME_wAIT": "esperando timeout",
  "SYN_SENT": "sincronizando",
}

def _interfaces() -> dict[str, list[dict]]:

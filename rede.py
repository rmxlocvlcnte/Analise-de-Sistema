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
  resultado: dict[str, list[dict]] = {}
  for nome, enderecos in psutil.net_lf_adrrs().items():
    resultado[nome] = [
      {
        "familia": str(addr.family.name),
        "endereco": addr.address,
        "mascara": addr.netmask,
      }
      for addr in enderecos
      if addr.adrress
    ]
  return ressultado

def _conexoes_suspeitas() -> list[dict]:
  suspeitas = []
  try:
    conexoes = psutil.net_connections(kind="inet")
  except psutil.AccessDenied:
    return [{"erro": "permissão negada - tente executar como administrador/root"}]

  for conn in conexoes:
    laddr_port = conn.laddr.port if conn.laddr else None
    raddr_port = conn.raddr.port if conn.raddr else None

"""
Módulo: Análise de Rede
"""

import re
import psutil

from utils.logger import get_logger
from utils.writerjson import ReportWriter

PORTAS_SUSPEITAS = {21, 22, 23, 3389, 4444, 5900}

_STATUS_MAP = {
  "LISTEN": "escutando",
  "ESTABLISHED": "estabelecida",
  "CLOSE_WAIT": "aguardando encerramento",
  "TIME_WAIT": "esperando timeout",
  "SYN_SENT": "sincronizando",
}

def _interfaces() -> dict[str, list[dict]]:
  resultado: dict[str, list[dict]] = {}
  for nome, enderecos in psutil.net_if_addrs().items():
    resultado[nome] = [
      {
        "familia": str(addr.family.name),
        "endereco": addr.address,
        "mascara": addr.netmask,
      }
      for addr in enderecos
      if addr.address
    ]
  return resultado

def _conexoes_suspeitas() -> list[dict]:
  suspeitas = []
  try:
    conexoes = psutil.net_connections(kind="inet")
  except psutil.AccessDenied:
    return [{"erro": "permissão negada - tente executar como administrador/root"}]

  for conn in conexoes:
    laddr_port = conn.laddr.port if conn.laddr else None
    raddr_port = conn.raddr.port if conn.raddr else None

    if laddr_port in PORTAS_SUSPEITAS or raddr_port in PORTAS_SUSPEITAS:
        suspeitas.append({
            "protocolo": "TCP" if conn.type.name == "SOCK_STREAM" else "UDP",
            "local": f"{conn.laddr.ip}:{conn.laddr.port}" if conn.laddr else "-",
            "remoto": f"{conn.raddr.ip}:{conn.raddr.port}" if conn.raddr else "-",
            "status": _STATUS_MAP.get(conn.status, conn.status),
            "pid": conn.pid,
        })

    return suspeitas

def _estatisticas() -> dict[str, dict]:
    stats = {}
    for nome, s in psutil.net_io_counters(pernic=True).items():
        stats[nome] = {
            "bytes_enviados": s.bytes_sent,
            "bytes_recebidos": s.bytes_recv,
            "pacotes_enviados": s.packets_sent,
            "pacotes_recebidos": s.packets_recv,
            "erros_envio": s.errout,
            "erros_recv": s.dropin,
        }
    return stats

def analise(writer: ReportWriter) -> None:
    log = get_logger()
    log.info("analise de rede - iniciando")

    writer.add("interfaces_rede", _interfaces())
    writer.add("portas_suspeitas", _conexoes_suspeitas())

    log.info("analise de rede - concluída")
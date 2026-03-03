#!usr/bin/bash/env python3

"""
sysreport - Relatório de segurança e saúde do sistema
Compatível com sistemas Linux e Windows.

Uso:
    python main.py
    python main.py --dir "/caminho/personalizado/"
"""

import argparse
import platform
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from pathlib import Path

from utils.logger import logger_setup
from utils.writerjson import ReportWriter
from modulos import saude, rede, logs

sys.path.insert(0, str(Path(__file__).parent.parent))

# Definindo diretório/pasta padrão

def dir_padrao() -> Path:
    if platform.system() == "Windows":
	    return Path.home() / "AppData" / "Local" / "sysreport" / "relatorios"
    return Path.home() / "sysreport" / "relatorios"

# CLI

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
    description="Gera um relatório sobre a segurança e saúde do Sistema",
    formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--dir",
        type=Path,
        default=dir_padrao(),
        help="Diretório de saída dos relatórios (Padrão: %(default)s)",
    )
    return parser.parse_args()

# Código Principal

def main() -> None:
    args = parse_args()

    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    report_dir: Path = args.dir

    log = logger_setup(report_dir, timestamp)
    writer = ReportWriter(hostname=platform.node(), timestamp=timestamp)

    log.info("sysreport Iniciado — %s %s", platform.system(), platform.version())
    log.info("Relatórios em: %s", report_dir)

    # Módulos paralelos
    erros: list[str] = []

    with ThreadPoolExecutor(max_workers=2, thread_name_prefix="sysreport") as pool:
        futures = {
            pool.submit(rede.analise, writer): "rede",
            pool.submit(logs.analise, writer): "logs",
        }

        # Teste de saúde rodando em paralelo
        try:
            saude.analise(writer)
        except Exception as e:
            log.error("Saúde — Erro: %s", e)
            erros.append(f"Saúde: {e}")

        for future in as_completed(futures):
            modulo = futures[future]
            try:
                future.result()
            except Exception as e:
                log.error("%s — Erro: %s", modulo, e)
                erros.append(f"{modulo}: {e}")
    if erros:
        writer.add("erros_execucao", erros)

    # Salvando JSON
    report_path = report_dir / f"report_{timestamp}.json"
    try:
        writer.save(report_path)
        log.info("Relatório Salvo: %s", report_path)
    except Exception as e:
        log.critical("Falha ao salvar relatório: %s", e)
        sys.exit(1)

    log.info("sysreport concluído.")

if __name__ == "__main__":
    main()
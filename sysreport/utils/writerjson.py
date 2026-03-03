import json
import threading
from pathlib import Path
from typing import Any

class ReportWriter:
    """
    Acumula dados do relatório em memória com thread-safety e serializa para JSON ao final
    """

    def __init__(self, hostname: str, timestamp: str) -> None:
        self._lock = threading.Lock()
        self._report: dict[str, Any] = {
            "horario": timestamp,
            "hostname": hostname,
            "data": {},
        }
    
    def add(self, key: str, value: Any) -> None:
        """Adiciona ou atualiza uma chave em data"""
        with self._lock:
            self._report["data"][key] = value

    def save(self, path: Path) -> None:
        """Salva o relatório em disco"""
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(self._report, f, ensure_ascii=False, indent=2)

    @property
    def data(self) -> dict[str, Any]:
        with self._lock:
            return dict[self._report]
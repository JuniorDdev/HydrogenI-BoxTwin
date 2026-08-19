import json
from datetime import datetime, timezone
from pathlib import Path


class OfflineNotificationQueue:
    """
    Fila persistente para notificações que falharam.
    Tenta reenviar até um número máximo de tentativas.
    """

    def __init__(self, storage_path, config, database, notification_service):
        self.storage_path = Path(storage_path)
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)
        self.config = config
        self.database = database
        self.notification_service = notification_service
        self.max_attempts = config.get("OFFLINE_MAX_ATTEMPTS", 5)
        self._load_queue()

    def _load_queue(self):
        if self.storage_path.exists():
            with open(self.storage_path, "r", encoding="utf-8") as f:
                self.queue = json.load(f)
        else:
            self.queue = []

    def _save_queue(self):
        with open(self.storage_path, "w", encoding="utf-8") as f:
            json.dump(self.queue, f, indent=2, default=str)

    def enqueue(self, anomaly, target, attempt=0):
        """
        Adiciona uma notificação à fila para tentativas futuras.
        """
        entry = {
            "anomaly": anomaly,
            "target": target,
            "attempt": attempt,
            "last_try": datetime.now(timezone.utc).isoformat(),
            "created_at": datetime.now(timezone.utc).isoformat(),
        }
        self.queue.append(entry)
        self._save_queue()

    def process_queue(self):
        """
        Tenta reenviar todas as notificações pendentes.
        Remove da fila em caso de sucesso ou após exceder tentativas.
        """
        remaining = []
        for entry in self.queue:
            anomaly = entry["anomaly"]
            target = entry["target"]

            try:
                result = self.notification_service._send(anomaly, target)
                if result:
                    # Sucesso: registra no log e não mantém na fila
                    self.database.log_notification(
                        anomaly["id"],
                        target["channel"],
                        "sent",
                        f"Reenviado após {entry['attempt'] + 1} tentativa(s)",
                        recipient_id=target.get("recipient_id"),
                    )
                    continue  # não reinsere
            except Exception as exc:
                # Falha: incrementa tentativa
                entry["attempt"] += 1
                entry["last_try"] = datetime.now(timezone.utc).isoformat()

                if entry["attempt"] < self.max_attempts:
                    remaining.append(entry)
                else:
                    # Excedeu tentativas: descarta e loga como falha permanente
                    self.database.log_notification(
                        anomaly["id"],
                        target["channel"],
                        "failed_permanent",
                        f"Falha após {self.max_attempts} tentativas: {str(exc)[:200]}",
                        recipient_id=target.get("recipient_id"),
                    )
                    # Não reinsere

        self.queue = remaining
        self._save_queue()
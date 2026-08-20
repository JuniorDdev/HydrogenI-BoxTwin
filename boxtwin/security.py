import os
import subprocess
from pathlib import Path


class SSLManager:
    """Gerencia certificados SSL para o BoxTwin."""

    def __init__(self, cert_path=None, key_path=None, auto_generate=False):
        self.cert_path = Path(cert_path) if cert_path else None
        self.key_path = Path(key_path) if key_path else None
        if auto_generate and not (self.cert_path and self.cert_path.exists()):
            self.generate_self_signed()

    def generate_self_signed(self, common_name="boxtwin.local", days=365):
        """Gera um certificado autoassinado usando openssl."""
        if not self.cert_path or not self.key_path:
            raise ValueError("Caminhos do certificado e chave devem ser definidos.")
        self.cert_path.parent.mkdir(parents=True, exist_ok=True)
        self.key_path.parent.mkdir(parents=True, exist_ok=True)
        cmd = [
            "openssl", "req", "-x509", "-newkey", "rsa:4096",
            "-nodes", "-out", str(self.cert_path), "-keyout", str(self.key_path),
            "-days", str(days), "-subj", f"/CN={common_name}"
        ]
        subprocess.run(cmd, check=True)
        return {"cert": str(self.cert_path), "key": str(self.key_path)}

    @property
    def has_certificates(self):
        return self.cert_path and self.cert_path.exists() and self.key_path and self.key_path.exists()

    def get_gunicorn_ssl_args(self):
        """Retorna argumentos para o Gunicorn (--certfile e --keyfile)."""
        if self.has_certificates:
            return ["--certfile", str(self.cert_path), "--keyfile", str(self.key_path)]
        return []
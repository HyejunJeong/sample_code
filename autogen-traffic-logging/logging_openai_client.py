import datetime
import socket
from autogen_ext.models.openai import OpenAIChatCompletionClient
from .isp_logger import isp_logger


class LoggingOpenAIClient(OpenAIChatCompletionClient):
    """
    OpenAI client wrapper that logs API request metadata
    (domain, IP, payload size) for evaluation and auditing.
    """

    async def acompletion(self, *args, **kwargs):
        messages = kwargs.get("messages") or (args[0] if args else [])
        timestamp = datetime.datetime.utcnow().isoformat()

        domain = "api.openai.com"
        try:
            ip = socket.gethostbyname(domain)
        except Exception:
            ip = "unknown"

        try:
            payload_size = len(str(messages).encode())
        except Exception:
            payload_size = "unknown"

        isp_logger.info(
            f"[API] {timestamp} | Domain: {domain} | IP: {ip} | Size: {payload_size}"
        )

        return await super().acompletion(*args, **kwargs)

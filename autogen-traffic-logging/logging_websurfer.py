import asyncio
import datetime
import socket
from urllib.parse import urlparse

from autogen_ext.agents.web_surfer import MultimodalWebSurfer
from .isp_logger import isp_logger


class LoggingWebSurfer(MultimodalWebSurfer):
    """
    Web-browsing agent instrumented to log network-level behavior
    including requests, responses, and navigation events.

    Instrumentation is applied by patching Playwright hooks during
    lazy initialization to ensure all pages and tabs are covered.
    """

    async def _lazy_init(self):
        await super()._lazy_init()

        original_visit_page = self._playwright_controller.visit_page
        original_on_new_page = self._playwright_controller.on_new_page

        async def attach_logging(page):
            async def log_request(route, request):
                url = request.url
                domain = urlparse(url).netloc or "unknown"
                timestamp = datetime.datetime.utcnow().isoformat()

                try:
                    ip = socket.gethostbyname(domain)
                except Exception:
                    ip = "unknown"

                size = request.headers.get("content-length", "unknown")
                method = request.method

                isp_logger.info(
                    f"[REQ] {timestamp} | Domain: {domain} | IP: {ip} | "
                    f"Method: {method} | Size: {size} | URL: {url}"
                )

                await route.continue_()

            def log_response(response):
                async def handle():
                    timestamp = datetime.datetime.utcnow().isoformat()
                    url = response.url
                    domain = urlparse(url).netloc or "unknown"

                    try:
                        ip = socket.gethostbyname(domain)
                    except Exception:
                        ip = "unknown"

                    try:
                        body = await response.body()
                        size = len(body)
                    except Exception:
                        size = "unknown"

                    isp_logger.info(
                        f"[RESP] {timestamp} | Domain: {domain} | IP: {ip} | "
                        f"Status: {response.status} | Size: {size} | URL: {url}"
                    )

                asyncio.create_task(handle())

            await page.route("**/*", log_request)
            page.on("response", log_response)

            page.on(
                "framenavigated",
                lambda frame: isp_logger.info(
                    f"[NAV] {datetime.datetime.utcnow().isoformat()} | "
                    f"Domain: {urlparse(frame.url).netloc} | URL: {frame.url}"
                ),
            )

        async def logging_visit_page(page, url, *args, **kwargs):
            await attach_logging(page)
            page.context.on(
                "page", lambda p: asyncio.create_task(attach_logging(p))
            )
            return await original_visit_page(page, url, *args, **kwargs)

        async def logging_on_new_page(page):
            await original_on_new_page(page)
            await attach_logging(page)

        self._playwright_controller.visit_page = logging_visit_page
        self._playwright_controller.on_new_page = logging_on_new_page

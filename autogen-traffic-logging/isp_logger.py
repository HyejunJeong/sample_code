import logging

# Global logger for network-level agent behavior
isp_logger = logging.getLogger("isp_logger")
isp_logger.setLevel(logging.INFO)
isp_logger.propagate = False


def set_isp_logfile(filepath: str):
    """
    Configure the ISP-style logger to write structured logs to a file.
    Existing handlers are removed to avoid duplicate logs.
    """
    for h in isp_logger.handlers:
        isp_logger.removeHandler(h)

    handler = logging.FileHandler(filepath, mode="w")
    handler.setFormatter(logging.Formatter("%(levelname)s | %(message)s"))
    isp_logger.addHandler(handler)

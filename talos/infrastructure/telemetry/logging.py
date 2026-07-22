"""Minimal logging setup — one place to configure, so services never call
``logging.basicConfig`` themselves."""

from __future__ import annotations

import logging


def get_logger(name: str = "talos", level: int = logging.INFO) -> logging.Logger:
    logger = logging.getLogger(name)
    if not logger.handlers:
        handler = logging.StreamHandler()
        handler.setFormatter(
            logging.Formatter("%(asctime)s %(levelname)-7s %(name)s: %(message)s")
        )
        logger.addHandler(handler)
        logger.setLevel(level)
    return logger

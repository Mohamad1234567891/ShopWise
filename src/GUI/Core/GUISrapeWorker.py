"""
This file is part of ShopWise, an open-source multi-region, multi-store
price-comparison and product-search engine.

Copyright (c) 2026 Muhammed Bekiroğlu and the ShopWise contributors.

Original ShopWise repository: https://github.com/Mohamad1234567891/ShopWise

Muhammed Bekiroğlu (ShopWise team leader and top contributor) YouTube channel:
    https://www.youtube.com/@ALShajaraComputerScienceInstit

Licensed under the Mozilla Public License 2.0 with Additional Attribution
Terms — see the LICENSE file.
"""

import asyncio
from PySide6.QtCore import QThread, Signal   # PyQt: use pyqtSignal instead of Signal
from src.Core.DataAcquisition.Scraping import Scraper

from src.Core.DataAnalysis import StatisticalAnalysis as SA


class ScrapeWorker(QThread):
    """Background QThread that runs the scraping pipeline and emits finished_ok(products, stats) on success or failed(message) on error, keeping the GUI responsive."""
    finished_ok = Signal(list, dict)   # products, stats
    failed = Signal(str)

    def __init__(self, query, parent=None):
        super().__init__(parent)
        self.query = query

    def run(self):
        try:
            products, stats = asyncio.run(Scraper.StartScraping(self.query))
            products = SA.AnalyzeResults(products)   # same as the CLI path
            self.finished_ok.emit(products, stats)
        except Exception as exc:
            self.failed.emit(repr(exc))
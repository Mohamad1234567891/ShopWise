import asyncio
from PySide6.QtCore import QThread, Signal   # PyQt: use pyqtSignal instead of Signal
from src.Core.DataAcquisition.Scraping import Scraper

from src.Core.DataAnalysis import StatisticalAnalysis as SA


class ScrapeWorker(QThread):
    finished_ok = Signal(list, dict)   # products, stats
    failed = Signal(str)

    def __init__(self, query, parent=None):
        super().__init__(parent)
        self.query = query

    def run(self):
        try:
            products, stats = asyncio.run(Scraper.StartScraping(self.query))
            products = SA.SortAndColorStores(SA.AssignPoints(products))   # same as the CLI path
            self.finished_ok.emit(products, stats)
        except Exception as exc:
            self.failed.emit(repr(exc))
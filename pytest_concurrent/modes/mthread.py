import concurrent.futures

from .base import BaseMode


class MultiThreadMode(BaseMode):
    NAME = 'mthread'

    def run_items(self, items, session, workers=None):
        with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as executor:
            for index, item in enumerate(items):
                executor.submit(self._run_next_item, session, item, index)

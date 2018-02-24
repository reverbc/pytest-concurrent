from .base import BaseMode


class AsyncNetMode(BaseMode):
    NAME = 'asyncnet'

    def run_items(self, items, session, workers=None):
        import gevent
        import gevent.monkey
        import gevent.pool
        gevent.monkey.patch_all()
        pool = gevent.pool.Pool(size=workers)
        for index, item in enumerate(items):
            pool.spawn(self._run_next_item, session, item, index)
        pool.join()

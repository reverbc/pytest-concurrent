class BaseMode(object):
    NAME = 'base'

    def run_items(self, items, session, workers=None):
        raise NotImplementedError

    def _run_next_item(self, session, item, i):
        nextitem = session.items[i + 1] if i + 1 < len(session.items) else None
        item.config.hook.pytest_runtest_protocol(item=item, nextitem=nextitem)
        if session.shouldstop:
            raise session.Interrupted(session.shouldstop)

    def set_reporter(self, config):
        pass

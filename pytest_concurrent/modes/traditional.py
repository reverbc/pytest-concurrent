from .base import BaseMode


class TraditionalMode(BaseMode):
    NAME = ''

    def run_items(self, items, session, workers=None):
        for i, item in enumerate(items):
            nextitem = items[i + 1] if i + 1 < len(items) else None
            item.config.hook.pytest_runtest_protocol(item=item, nextitem=nextitem)
            if session.shouldstop:
                raise session.Interrupted(session.shouldstop)

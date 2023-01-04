import time
from collections import defaultdict
from typing import Iterator, Tuple, Any, Union

from health_api import logger


class NotSet:
    pass

DEFAULT_TTL = 10

class _KnowledgeBase(dict):

    def __init__(self):
        super().__init__()
        # everything will be cached for 10 seconds by default
        self._ttl = defaultdict(lambda: DEFAULT_TTL)
        self._update_time = {}

    def get(self, key: str = None, default: Any = NotSet) -> Union[Iterator[Tuple[str, Any]], Any]:
        if not self.has(key):
            if default != NotSet:
                return default
            else:
                raise KeyError(key)
        return self[key]

    def set(self, key: str, value: Any, ttl: int = DEFAULT_TTL):
        self[key] = value
        self._update_time[key] = time.time()
        self._ttl[key] = ttl

    def has(self, key: str) -> bool:
        return key in self and not self._expired(key)

    def remove(self, key: str):
        if key in self:
            del self[key]
        del self._update_time[key]
        del self._ttl[key]

    def _expired(self, key):
        # if we don't have enough data to tell, we assume it is expired
        if key not in self._ttl or key not in self._update_time:
            return True
        # check the time elapsed
        ttl = self._ttl[key]
        elapsed = int(time.time() - self._update_time[key])
        # disabled, too noisy
        # logger.debug("Resource '{}':{}Found in cache {} secs old. TTL is {}".format(
        #     key, ' ' * (12 - len(key)), elapsed, ttl
        # ))
        return 0 <= ttl < elapsed


KnowledgeBase = _KnowledgeBase()

__all__ = [
    'KnowledgeBase'
]

import time
from collections import defaultdict, deque


class RateLimiter:
    """Не больше max_requests запросов в 60 секунд на один client_id."""

    def __init__(self, max_requests: int):
        self.max_requests = max_requests
        self.requests = defaultdict(deque)  # client_id -> времена запросов

    def allow(self, client_id: str) -> bool:
        now = time.time()
        history = self.requests[client_id]

        # выбрасываем запросы старше 1 минуты
        while history and now - history[0] > 60:
            history.popleft()

        if len(history) >= self.max_requests:
            return False  # лимит исчерпан

        history.append(now)
        return True
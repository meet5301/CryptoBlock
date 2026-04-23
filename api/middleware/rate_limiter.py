from collections import defaultdict
from functools import wraps
from time import time
from flask import jsonify, request

_requests = defaultdict(list)
RATE_LIMIT = 30
WINDOW = 60


def rate_limit(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        ip = request.remote_addr
        now = time()
        _requests[ip] = [t for t in _requests[ip] if now - t < WINDOW]
        if len(_requests[ip]) >= RATE_LIMIT:
            return jsonify({"error": "Rate limit exceeded"}), 429
        _requests[ip].append(now)
        return f(*args, **kwargs)
    return decorated

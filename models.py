# Data models for logs (placeholder for future use)
class Log:
    def __init__(self, ip, timestamp, method, endpoint, status, size):
        self.ip = ip
        self.timestamp = timestamp
        self.method = method
        self.endpoint = endpoint
        self.status = status
        self.size = size

import os

bind = f"0.0.0.0:{os.getenv('PORT', '8000')}"
workers = 5
worker_class = "uvicorn.workers.UvicornWorker"
preload_app = True
timeout = 120
keepalive = 5
accesslog = "-"
errorlog = "-"
loglevel = "info"
max_requests = 1000
max_requests_jitter = 100
worker_connections = 1000
limit_request_line = 4096
limit_request_fields = 20
limit_request_field_size = 4096

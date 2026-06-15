import os


bind = f"0.0.0.0:{os.environ.get('NINA_PORT', '5000')}"
workers = int(os.environ.get("NINA_WEB_CONCURRENCY", "1"))
threads = int(os.environ.get("NINA_GUNICORN_THREADS", "4"))
timeout = int(os.environ.get("NINA_GUNICORN_TIMEOUT", "120"))
graceful_timeout = 30
keepalive = 5
accesslog = "-"
errorlog = "-"
capture_output = True


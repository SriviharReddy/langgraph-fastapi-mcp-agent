from fastapi.middleware.gzip import GZipMiddleware

def setup_gzip(app):
    # Compress all responses larger than 1000 bytes (1KB)
    app.add_middleware(GZipMiddleware, minimum_size=1000)

from fastapi.middleware.cors import CORSMiddleware

def setup_cors(app):
    # Completely open for local development
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )


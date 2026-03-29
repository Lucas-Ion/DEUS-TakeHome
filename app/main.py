"""
main.py is the entry point for local development.

When deployed, uvicorn is invoked directly via the Dockerfile.
"""

import uvicorn

if __name__ == "__main__":
    uvicorn.run(
        "app.app:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
    )

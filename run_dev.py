"""
Local development server script
"""
import os
import sys

# Set the database path to local data directory
os.environ['DB_PATH'] = os.path.join(os.path.dirname(__file__), 'data', 'news.db')

# Run uvicorn
if __name__ == '__main__':
    import uvicorn
    uvicorn.run(
        "backend.app:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )

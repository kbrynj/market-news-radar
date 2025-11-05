"""
FastAPI Application for Market News Radar
- REST API endpoints for feeds, tickers, keywords, settings, articles
- WebSocket support for live updates
- Background scraper task
- Static file serving for frontend
"""
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException, Query, Header, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, field_validator
from typing import List, Optional, Set
import asyncio
import os
from datetime import datetime, timedelta
import json

from . import db
from . import scraper


# Get admin token from environment (optional)
ADMIN_TOKEN = os.environ.get("ADMIN_TOKEN", None)


# Pydantic models for API requests/responses
class FeedCreate(BaseModel):
    url: str = Field(..., min_length=1)
    name: str = Field(..., min_length=1)


class TickerCreate(BaseModel):
    symbol: str = Field(..., min_length=1, max_length=10)
    company_names: str = Field(default="", max_length=500)


class KeywordCreate(BaseModel):
    word: str = Field(..., min_length=1, max_length=50)


class SettingsUpdate(BaseModel):
    refresh_interval: Optional[int] = Field(None, ge=10)
    min_score: Optional[int] = Field(None, ge=0)
    strong_words: Optional[str] = None
    
    @field_validator('strong_words')
    def validate_strong_words(cls, v):
        if v is not None and len(v) > 500:
            raise ValueError('strong_words too long')
        return v


# Admin token dependency
async def verify_admin_token(x_admin_token: Optional[str] = Header(None)):
    """
    Verify admin token if ADMIN_TOKEN is set.
    If no token is configured, allow all requests (open mode).
    """
    if ADMIN_TOKEN is None:
        # No token configured - allow request
        return True
    
    if x_admin_token is None:
        raise HTTPException(
            status_code=401,
            detail="Admin authentication required. Set x-admin-token header."
        )
    
    if x_admin_token != ADMIN_TOKEN:
        raise HTTPException(
            status_code=403,
            detail="Invalid admin token"
        )
    
    return True


# WebSocket connection manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: Set[WebSocket] = set()
    
    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.add(websocket)
        print(f"WebSocket connected. Total connections: {len(self.active_connections)}")
    
    def disconnect(self, websocket: WebSocket):
        self.active_connections.discard(websocket)
        print(f"WebSocket disconnected. Total connections: {len(self.active_connections)}")
    
    async def broadcast(self, message: dict):
        """Broadcast message to all connected clients."""
        if not self.active_connections:
            return
        
        message_text = json.dumps(message)
        disconnected = set()
        
        for connection in self.active_connections:
            try:
                await connection.send_text(message_text)
            except Exception as e:
                print(f"Error sending to WebSocket: {e}")
                disconnected.add(connection)
        
        # Remove disconnected clients
        for conn in disconnected:
            self.active_connections.discard(conn)


# Initialize FastAPI app
app = FastAPI(title="Market News Radar API", version="1.0.0")

# CORS middleware - allow all origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# WebSocket manager
manager = ConnectionManager()

# Background task reference
background_task = None


# Startup event
@app.on_event("startup")
async def startup_event():
    """Initialize database and start background scraper."""
    print("Starting Market News Radar...")
    
    # Initialize database
    await db.init_db()
    print("Database initialized")
    
    # Start background scraper loop
    global background_task
    background_task = asyncio.create_task(background_scraper_loop())
    print("Background scraper started")


# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    """Clean up on shutdown."""
    global background_task
    if background_task:
        background_task.cancel()
        try:
            await background_task
        except asyncio.CancelledError:
            pass
    
    await db.close_db()
    print("Application shutdown complete")


async def background_scraper_loop():
    """Background task that runs scraper at configured intervals."""
    # Wait a bit for app to fully start
    await asyncio.sleep(5)
    
    while True:
        try:
            # Get current settings
            settings = await db.get_settings()
            interval = max(settings.get('refresh_interval', 300), 10)  # Minimum 10 seconds
            
            print(f"Running background scrape cycle...")
            inserted = await scraper.run_cycle()
            
            # Broadcast to WebSocket clients if new articles inserted
            if inserted > 0:
                await manager.broadcast({
                    "type": "refresh",
                    "inserted": inserted,
                    "timestamp": datetime.now().isoformat()
                })
            
            print(f"Next scrape in {interval} seconds")
            await asyncio.sleep(interval)
            
        except Exception as e:
            print(f"Error in background scraper: {e}")
            await asyncio.sleep(60)  # Wait before retry on error


# WebSocket endpoint
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for live updates."""
    await manager.connect(websocket)
    try:
        while True:
            # Keep connection alive, wait for messages (though we only broadcast)
            data = await websocket.receive_text()
            # Echo back or ignore
            await websocket.send_json({"type": "pong"})
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        print(f"WebSocket error: {e}")
        manager.disconnect(websocket)


# ============ Feed Endpoints ============

@app.get("/api/feeds")
async def get_feeds():
    """Get all RSS feeds."""
    feeds = await db.get_all_feeds()
    return {"feeds": feeds}


@app.post("/api/feeds")
async def create_feed(feed: FeedCreate, _admin: bool = Depends(verify_admin_token)):
    """Add a new RSS feed."""
    try:
        feed_id = await db.add_feed(feed.url, feed.name)
        return {"id": feed_id, "message": "Feed added successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to add feed: {str(e)}")


@app.delete("/api/feeds/{feed_id}")
async def delete_feed(feed_id: int, _admin: bool = Depends(verify_admin_token)):
    """Delete an RSS feed."""
    try:
        await db.delete_feed(feed_id)
        return {"message": "Feed deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to delete feed: {str(e)}")


@app.put("/api/feeds/{feed_id}/toggle")
async def toggle_feed(feed_id: int, active: bool = Query(...), _admin: bool = Depends(verify_admin_token)):
    """Toggle feed active status."""
    try:
        await db.toggle_feed(feed_id, active)
        return {"message": f"Feed {'activated' if active else 'deactivated'}"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to toggle feed: {str(e)}")


# ============ Ticker Endpoints ============

@app.get("/api/tickers")
async def get_tickers():
    """Get all tickers."""
    tickers = await db.get_all_tickers()
    return {"tickers": tickers}


@app.post("/api/tickers")
async def create_ticker(ticker: TickerCreate, _admin: bool = Depends(verify_admin_token)):
    """Add a new ticker with optional company name aliases."""
    try:
        ticker_id = await db.add_ticker(ticker.symbol, ticker.company_names)
        return {"id": ticker_id, "message": "Ticker added successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to add ticker: {str(e)}")


@app.delete("/api/tickers/{ticker_id}")
async def delete_ticker(ticker_id: int, _admin: bool = Depends(verify_admin_token)):
    """Delete a ticker."""
    try:
        await db.delete_ticker(ticker_id)
        return {"message": "Ticker deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to delete ticker: {str(e)}")


@app.put("/api/tickers/{ticker_id}")
async def update_ticker(ticker_id: int, company_names: str = Query(..., max_length=500), _admin: bool = Depends(verify_admin_token)):
    """Update company name aliases for a ticker."""
    try:
        await db.update_ticker_company_names(ticker_id, company_names)
        return {"message": "Company names updated successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to update ticker: {str(e)}")


# ============ Keyword Endpoints ============

@app.get("/api/keywords")
async def get_keywords():
    """Get all keywords."""
    keywords = await db.get_all_keywords()
    return {"keywords": keywords}


@app.post("/api/keywords")
async def create_keyword(keyword: KeywordCreate, _admin: bool = Depends(verify_admin_token)):
    """Add a new keyword."""
    try:
        keyword_id = await db.add_keyword(keyword.word)
        return {"id": keyword_id, "message": "Keyword added successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to add keyword: {str(e)}")


@app.delete("/api/keywords/{keyword_id}")
async def delete_keyword(keyword_id: int, _admin: bool = Depends(verify_admin_token)):
    """Delete a keyword."""
    try:
        await db.delete_keyword(keyword_id)
        return {"message": "Keyword deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to delete keyword: {str(e)}")


# ============ Settings Endpoints ============

@app.get("/api/settings")
async def get_settings():
    """Get current settings."""
    settings = await db.get_settings()
    return settings


@app.put("/api/settings")
async def update_settings(settings: SettingsUpdate, _admin: bool = Depends(verify_admin_token)):
    """Update settings."""
    try:
        await db.update_settings(
            refresh_interval=settings.refresh_interval,
            min_score=settings.min_score,
            strong_words=settings.strong_words
        )
        return {"message": "Settings updated successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to update settings: {str(e)}")


# ============ Article Endpoints ============

@app.get("/api/articles")
async def get_articles(
    q: Optional[str] = Query(None, description="Search query"),
    min_score: Optional[int] = Query(None, ge=0, description="Minimum score filter"),
    limit: int = Query(50, ge=1, le=200, description="Number of articles to return"),
    offset: int = Query(0, ge=0, description="Offset for pagination")
):
    """Get articles with optional filtering and pagination."""
    try:
        articles = await db.get_articles(
            limit=limit,
            offset=offset,
            min_score=min_score,
            search=q
        )
        
        total = await db.get_articles_count(
            min_score=min_score,
            search=q
        )
        
        return {
            "articles": articles,
            "total": total,
            "limit": limit,
            "offset": offset
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch articles: {str(e)}")


@app.post("/api/refresh")
async def manual_refresh(_admin: bool = Depends(verify_admin_token)):
    """Manually trigger a scrape cycle."""
    try:
        print("Manual refresh triggered")
        inserted = await scraper.run_cycle()
        
        # Broadcast to WebSocket clients
        if inserted > 0:
            await manager.broadcast({
                "type": "refresh",
                "inserted": inserted,
                "timestamp": datetime.now().isoformat()
            })
        
        return {
            "message": "Refresh completed",
            "inserted": inserted
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Refresh failed: {str(e)}")


@app.delete("/api/articles")
async def prune_articles(days: int = Query(7, ge=1, description="Delete articles older than X days"), _admin: bool = Depends(verify_admin_token)):
    """Delete articles older than specified days."""
    try:
        cutoff_timestamp = int((datetime.now() - timedelta(days=days)).timestamp())
        
        connection = await db.get_db()
        cursor = await connection.execute(
            "DELETE FROM articles WHERE published_ts < ?",
            (cutoff_timestamp,)
        )
        await connection.commit()
        
        deleted_count = cursor.rowcount
        return {
            "message": f"Deleted {deleted_count} articles older than {days} days",
            "deleted": deleted_count
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to prune articles: {str(e)}")


# Ticker search endpoint (for autocomplete)
@app.get("/api/search/tickers")
async def search_tickers(q: str = Query(..., min_length=1, max_length=50)):
    """
    Search tickers by symbol or name.
    Returns matching tickers from local dataset (backend/tickers.json).
    """
    try:
        import json
        from pathlib import Path
        
        # Load tickers dataset
        tickers_file = Path(__file__).parent / "tickers.json"
        if not tickers_file.exists():
            raise HTTPException(status_code=500, detail="Tickers dataset not found")
        
        with open(tickers_file, 'r', encoding='utf-8') as f:
            all_tickers = json.load(f)
        
        # Normalize query
        query = q.upper().strip()
        
        # Search: symbol starts with query OR name contains query
        matches = []
        for ticker in all_tickers:
            symbol_match = ticker['symbol'].upper().startswith(query)
            name_match = query in ticker['name'].upper()
            
            if symbol_match or name_match:
                matches.append(ticker)
                
                # Limit results to 20 for performance
                if len(matches) >= 20:
                    break
        
        return {"results": matches}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to search tickers: {str(e)}")


# Health check endpoint
@app.get("/api/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat()
    }


# Mount static files (frontend) - must be last
frontend_path = os.path.join(os.path.dirname(__file__), "..", "frontend")
if os.path.exists(frontend_path):
    app.mount("/", StaticFiles(directory=frontend_path, html=True), name="static")
    print(f"Mounted frontend from {frontend_path}")

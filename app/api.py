from fastapi import FastAPI, Depends, HTTPException, Response, Request
from sqlalchemy.orm import Session
from sqlalchemy import func, text
from datetime import datetime, timedelta
import random
import time
from typing import List

from app.database import get_db, engine
from app import models, schemas
from app.models import Base
from app.metrics import (
    http_requests_total, http_request_duration_seconds, http_requests_in_progress,
    active_players_count, matches_total, revenue_total_usd, init_metrics
)
from prometheus_client import CONTENT_TYPE_LATEST, generate_latest

# Create tables and initialize metrics
try:
    Base.metadata.create_all(bind=engine)
    print("Database tables created successfully")
    init_metrics()
    print("Metrics initialized successfully")
except Exception as e:
    print(f"Error creating tables: {e}")

app = FastAPI(
    title="BattleArena API",
    version="1.0.0",
    description="Multiplayer gaming platform API"
)


# ========================================
# MIDDLEWARE FOR AUTOMATIC METRICS TRACKING
# ========================================

@app.middleware("http")
async def track_requests_middleware(request: Request, call_next):
    """Middleware to automatically track all HTTP requests"""
    method = request.method
    endpoint = request.url.path
    
    # Skip metrics endpoint to avoid recursion
    if endpoint == "/metrics":
        return await call_next(request)
    
    # Increment in-progress counter
    http_requests_in_progress.labels(method=method, endpoint=endpoint).inc()
    
    # Start timing
    start_time = time.time()
    
    try:
        # Process request
        response = await call_next(request)
        
        # Record metrics
        duration = time.time() - start_time
        status = str(response.status_code)
        
        http_requests_total.labels(
            method=method,
            endpoint=endpoint,
            status=status
        ).inc()
        
        http_request_duration_seconds.labels(
            method=method,
            endpoint=endpoint
        ).observe(duration)
        
        return response
        
    except Exception as e:
        # Record failed request
        duration = time.time() - start_time
        status = "500"
        
        http_requests_total.labels(
            method=method,
            endpoint=endpoint,
            status=status
        ).inc()
        
        http_request_duration_seconds.labels(
            method=method,
            endpoint=endpoint
        ).observe(duration)
        
        raise
        
    finally:
        # Always decrement in-progress counter
        http_requests_in_progress.labels(method=method, endpoint=endpoint).dec()

# ========================================
# READ ENDPOINTS (Statistics & Queries)
# ========================================

@app.get("/")
def root():
    """Root endpoint"""
    return {
        "message": "Welcome to BattleArena API",
        "version": "1.0.0",
        "docs": "/docs"
    }

@app.get("/metrics")
def metrics():
    """Prometheus metrics endpoint"""
    return Response(
        content=generate_latest(),
        media_type=CONTENT_TYPE_LATEST
    )

@app.get("/health")
def health_check(db: Session = Depends(get_db)):
    """Health check with DB connectivity"""
    try:
        # Test DB connection
        db.execute(text("SELECT 1"))
        return {
            "status": "healthy",
            "database": "connected",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "database": "disconnected",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

@app.get("/api/stats/players")
def get_player_stats(db: Session = Depends(get_db)):
    """Get player statistics"""
    total_players = db.query(func.count(models.Player.id)).scalar()
    
    active_today = db.query(func.count(models.Player.id)).filter(
        models.Player.last_login >= datetime.now() - timedelta(days=1)
    ).scalar()
    
    active_now = db.query(func.count(models.Player.id)).filter(
        models.Player.last_login >= datetime.now() - timedelta(minutes=5)
    ).scalar()
    
    new_today = db.query(func.count(models.Player.id)).filter(
        func.date(models.Player.created_at) == datetime.now().date()
    ).scalar()
    
    return {
        "total_players": total_players or 0,
        "active_today": active_today or 0,
        "active_now": active_now or 0,
        "new_today": new_today or 0,
        "timestamp": datetime.now().isoformat()
    }

@app.get("/api/stats/matches")
def get_match_stats(db: Session = Depends(get_db)):
    """Get match statistics"""
    total_matches = db.query(func.count(models.Match.id)).scalar()
    
    in_progress = db.query(func.count(models.Match.id)).filter(
        models.Match.status == 'in_progress'
    ).scalar()
    
    completed_today = db.query(func.count(models.Match.id)).filter(
        models.Match.status == 'completed',
        func.date(models.Match.start_time) == datetime.now().date()
    ).scalar()
    
    crashed_today = db.query(func.count(models.Match.id)).filter(
        models.Match.status == 'crashed',
        func.date(models.Match.start_time) == datetime.now().date()
    ).scalar()
    
    crash_rate = (crashed_today / completed_today * 100) if completed_today and completed_today > 0 else 0
    
    avg_duration = db.query(func.avg(models.Match.duration_seconds)).filter(
        models.Match.status == 'completed',
        models.Match.duration_seconds.isnot(None)
    ).scalar()
    
    return {
        "total_matches": total_matches or 0,
        "in_progress": in_progress or 0,
        "completed_today": completed_today or 0,
        "crashed_today": crashed_today or 0,
        "crash_rate_percent": round(crash_rate, 2),
        "avg_duration_seconds": int(avg_duration) if avg_duration else 0,
        "timestamp": datetime.now().isoformat()
    }

@app.get("/api/stats/revenue")
def get_revenue_stats(db: Session = Depends(get_db)):
    """Get revenue statistics"""
    total_today = db.query(func.sum(models.Transaction.amount)).filter(
        models.Transaction.status == 'completed',
        func.date(models.Transaction.created_at) == datetime.now().date()
    ).scalar() or 0.0
    
    total_month = db.query(func.sum(models.Transaction.amount)).filter(
        models.Transaction.status == 'completed',
        func.extract('month', models.Transaction.created_at) == datetime.now().month,
        func.extract('year', models.Transaction.created_at) == datetime.now().year
    ).scalar() or 0.0
    
    transactions_today = db.query(func.count(models.Transaction.id)).filter(
        func.date(models.Transaction.created_at) == datetime.now().date()
    ).scalar()
    
    failed_today = db.query(func.count(models.Transaction.id)).filter(
        models.Transaction.status == 'failed',
        func.date(models.Transaction.created_at) == datetime.now().date()
    ).scalar()
    
    return {
        "revenue_today": round(total_today, 2),
        "revenue_month": round(total_month, 2),
        "transactions_today": transactions_today or 0,
        "failed_today": failed_today or 0,
        "timestamp": datetime.now().isoformat()
    }

@app.get("/api/leaderboard")
def get_leaderboard(limit: int = 10, db: Session = Depends(get_db)):
    """Get top players by points"""
    top_players = db.query(
        models.Player.id,
        models.Player.username,
        models.Player.level,
        models.Player.total_points
    ).filter(
        models.Player.is_active == True
    ).order_by(
        models.Player.total_points.desc()
    ).limit(limit).all()
    
    return {
        "leaderboard": [
            {
                "rank": idx + 1,
                "player_id": p.id,
                "username": p.username,
                "level": p.level,
                "points": p.total_points
            }
            for idx, p in enumerate(top_players)
        ]
    }

# ========================================
# WRITE ENDPOINTS (Simulator calls these)
# ========================================

@app.post("/api/players/register")
def register_player(player: schemas.PlayerCreate, db: Session = Depends(get_db)):
    """Register a new player"""
    # Check if username exists
    existing = db.query(models.Player).filter(
        models.Player.username == player.username
    ).first()
    
    if existing:
        raise HTTPException(status_code=400, detail="Username already exists")
    
    new_player = models.Player(
        username=player.username,
        email=player.email,
        level=player.level,
        created_at=datetime.now(),
        last_login=datetime.now()
    )
    
    db.add(new_player)
    db.commit()
    db.refresh(new_player)
    
    return {
        "player_id": new_player.id,
        "username": new_player.username,
        "message": "Player registered successfully"
    }

@app.post("/api/players/login")
def player_login(login: schemas.PlayerLogin, db: Session = Depends(get_db)):
    """Record player login"""
    player = db.query(models.Player).filter(
        models.Player.id == login.player_id
    ).first()

    if not player:
        raise HTTPException(status_code=404, detail="Player not found")

    # Update last login
    player.last_login = datetime.now()

    # Log event
    event = models.SystemEvent(
        event_type='login',
        severity='info',
        message=f'Player {player.id} ({player.username}) logged in',
        timestamp=datetime.now()
    )
    db.add(event)

    db.commit()

    # Update metrics
    active_players_count.inc()

    return {
        "player_id": player.id,
        "username": player.username,
        "level": player.level,
        "last_login": player.last_login.isoformat()
    }

@app.post("/api/matches/start")
def start_match(match: schemas.MatchCreate, db: Session = Depends(get_db)):
    """Start a new match"""
    try:
        # Validate players exist
        players = db.query(models.Player).filter(
            models.Player.id.in_(match.player_ids)
        ).all()

        if len(players) != len(match.player_ids):
            raise HTTPException(status_code=400, detail=f"Some players not found. Expected {len(match.player_ids)} players, found {len(players)}")

        # Validate match type
        if match.match_type not in ['solo', 'team', 'tournament']:
            raise HTTPException(status_code=400, detail=f"Invalid match type: {match.match_type}. Must be 'solo', 'team', or 'tournament'")

        # Validate player_ids is not empty
        if not match.player_ids:
            raise HTTPException(status_code=400, detail="player_ids cannot be empty")

        # Create match
        new_match = models.Match(
            match_type=match.match_type,
            status='in_progress',
            start_time=datetime.now(),
            server_region=match.server_region
        )
        db.add(new_match)
        db.flush()  # Get match ID

        # Add participants
        for player_id in match.player_ids:
            participant = models.MatchParticipant(
                match_id=new_match.id,
                player_id=player_id,
                joined_at=datetime.now()
            )
            db.add(participant)

        db.commit()
        db.refresh(new_match)

        # Update metrics
        matches_total.labels(match_type=match.match_type, status='started').inc()

        return {
            "match_id": new_match.id,
            "match_type": new_match.match_type,
            "status": new_match.status,
            "player_count": len(match.player_ids),
            "server_region": match.server_region
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error starting match: {str(e)}")

@app.post("/api/matches/complete")
def complete_match(result: schemas.MatchComplete, db: Session = Depends(get_db)):
    """Complete a match with results"""
    match = db.query(models.Match).filter(
        models.Match.id == result.match_id
    ).first()
    
    if not match:
        raise HTTPException(status_code=404, detail="Match not found")
    
    if match.status != 'in_progress':
        raise HTTPException(status_code=400, detail="Match is not in progress")
    
    # Update match
    match.status = 'completed'
    match.end_time = datetime.now()
    match.duration_seconds = result.duration_seconds
    match.winner_id = result.winner_id
    
    # Update participant stats
    for stat in result.participant_stats:
        participant = db.query(models.MatchParticipant).filter(
            models.MatchParticipant.match_id == result.match_id,
            models.MatchParticipant.player_id == stat.player_id
        ).first()
        
        if participant:
            participant.score = stat.score
            participant.kills = stat.kills
            participant.deaths = stat.deaths
            participant.left_at = datetime.now()
            
            # Update player total points
            player = db.query(models.Player).filter(
                models.Player.id == stat.player_id
            ).first()
            if player:
                player.total_points += stat.score
    
    db.commit()
    
    return {
        "match_id": match.id,
        "status": "completed",
        "winner_id": result.winner_id,
        "duration_seconds": result.duration_seconds,
        "message": "Match completed successfully"
    }

@app.post("/api/matches/crash")
def crash_match(crash: schemas.MatchCrash, db: Session = Depends(get_db)):
    """Mark a match as crashed"""
    match = db.query(models.Match).filter(
        models.Match.id == crash.match_id
    ).first()
    
    if not match:
        raise HTTPException(status_code=404, detail="Match not found")
    
    # Update match
    match.status = 'crashed'
    match.end_time = datetime.now()
    
    # Log system event
    event = models.SystemEvent(
        event_type='server_crash',
        severity='critical',
        message=f'Match {match.id} crashed: {crash.error_message}',
        timestamp=datetime.now()
    )
    db.add(event)
    
    db.commit()
    
    return {
        "match_id": match.id,
        "status": "crashed",
        "message": "Match marked as crashed"
    }

@app.post("/api/transactions/create")
def create_transaction(transaction: schemas.TransactionCreate, db: Session = Depends(get_db)):
    """Create a new transaction (purchase)"""
    try:
        player = db.query(models.Player).filter(
            models.Player.id == transaction.player_id
        ).first()

        if not player:
            raise HTTPException(status_code=404, detail=f"Player not found with ID: {transaction.player_id}")

        # 1% chance of payment failure (simulation)
        status = 'failed' if random.random() < 0.01 else 'completed'

        # Create transaction
        new_transaction = models.Transaction(
            player_id=transaction.player_id,
            item_type=transaction.item_type,
            item_name=transaction.item_name,
            amount=transaction.amount,
            status=status,
            created_at=datetime.now()
        )
        db.add(new_transaction)

        # If successful, update player balance
        if status == 'completed':
            player.account_balance += transaction.amount
            # Update revenue metrics
            revenue_total_usd.labels(item_type=transaction.item_type).inc(transaction.amount)

        db.commit()
        db.refresh(new_transaction)

        return {
            "transaction_id": new_transaction.id,
            "player_id": player.id,
            "item": transaction.item_name,
            "amount": transaction.amount,
            "status": status
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error creating transaction: {str(e)}")

@app.post("/api/system/event")
def log_system_event(event: schemas.SystemEventCreate, db: Session = Depends(get_db)):
    """Log a system event"""
    new_event = models.SystemEvent(
        event_type=event.event_type,
        severity=event.severity,
        message=event.message,
        metadata=str(event.metadata) if event.metadata else None,
        timestamp=datetime.now()
    )
    
    db.add(new_event)
    db.commit()
    db.refresh(new_event)
    
    return {
        "event_id": new_event.id,
        "event_type": event.event_type,
        "severity": event.severity,
        "message": "Event logged successfully"
    }

# ========================================
# UTILITY ENDPOINTS
# ========================================

@app.get("/api/players/{player_id}")
def get_player(player_id: int, db: Session = Depends(get_db)):
    """Get player details"""
    player = db.query(models.Player).filter(
        models.Player.id == player_id
    ).first()
    
    if not player:
        raise HTTPException(status_code=404, detail="Player not found")
    
    return {
        "player_id": player.id,
        "username": player.username,
        "email": player.email,
        "level": player.level,
        "total_points": player.total_points,
        "account_balance": player.account_balance,
        "created_at": player.created_at.isoformat(),
        "last_login": player.last_login.isoformat() if player.last_login else None,
        "is_active": player.is_active
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

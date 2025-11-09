from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime

# Player schemas
class PlayerCreate(BaseModel):
    username: str
    email: EmailStr
    level: int = 1

class PlayerLogin(BaseModel):
    player_id: int

class PlayerResponse(BaseModel):
    id: int
    username: str
    level: int
    total_points: int
    last_login: Optional[datetime]
    
    class Config:
        from_attributes = True

# Match schemas
class MatchCreate(BaseModel):
    match_type: str  # 'solo', 'team', 'tournament'
    player_ids: List[int]
    server_region: str = 'us-east'

class ParticipantStat(BaseModel):
    player_id: int
    score: int
    kills: int
    deaths: int

class MatchComplete(BaseModel):
    match_id: int
    winner_id: int
    duration_seconds: int
    participant_stats: List[ParticipantStat]

class MatchCrash(BaseModel):
    match_id: int
    error_message: str

# Transaction schemas
class TransactionCreate(BaseModel):
    player_id: int
    item_type: str
    item_name: str
    amount: float

# System event schemas
class SystemEventCreate(BaseModel):
    event_type: str
    severity: str
    message: str
    metadata: Optional[dict] = None

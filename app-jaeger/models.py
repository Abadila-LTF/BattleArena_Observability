from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

Base = declarative_base()

class Player(Base):
    """Player accounts"""
    __tablename__ = 'players'
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(100), nullable=False, unique=True, index=True)
    email = Column(String(255))
    level = Column(Integer, default=1)
    total_points = Column(Integer, default=0)
    account_balance = Column(Float, default=0.0)
    created_at = Column(DateTime, server_default=func.now())
    last_login = Column(DateTime)
    is_active = Column(Boolean, default=True)
    
    # Relationships
    transactions = relationship("Transaction", back_populates="player")
    match_participations = relationship("MatchParticipant", back_populates="player")

class Match(Base):
    """Game matches"""
    __tablename__ = 'matches'
    
    id = Column(Integer, primary_key=True, index=True)
    match_type = Column(String(50), index=True)  # 'solo', 'team', 'tournament'
    status = Column(String(20), index=True)      # 'waiting', 'in_progress', 'completed', 'crashed'
    start_time = Column(DateTime, index=True)
    end_time = Column(DateTime)
    winner_id = Column(Integer, ForeignKey('players.id'))
    duration_seconds = Column(Integer)
    server_region = Column(String(20), index=True)  # 'us-east', 'eu-west', 'asia'
    
    # Relationships
    participants = relationship("MatchParticipant", back_populates="match")

class MatchParticipant(Base):
    """Players in each match"""
    __tablename__ = 'match_participants'
    
    id = Column(Integer, primary_key=True)
    match_id = Column(Integer, ForeignKey('matches.id'), index=True)
    player_id = Column(Integer, ForeignKey('players.id'), index=True)
    score = Column(Integer, default=0)
    kills = Column(Integer, default=0)
    deaths = Column(Integer, default=0)
    joined_at = Column(DateTime)
    left_at = Column(DateTime)
    
    # Relationships
    match = relationship("Match", back_populates="participants")
    player = relationship("Player", back_populates="match_participations")

class Transaction(Base):
    """In-game purchases"""
    __tablename__ = 'transactions'
    
    id = Column(Integer, primary_key=True)
    player_id = Column(Integer, ForeignKey('players.id'), index=True)
    item_type = Column(String(50), index=True)   # 'skin', 'weapon', 'currency'
    item_name = Column(String(100))
    amount = Column(Float)
    currency = Column(String(10), default='USD')
    status = Column(String(20), index=True)      # 'completed', 'failed', 'refunded'
    created_at = Column(DateTime, server_default=func.now(), index=True)
    
    # Relationships
    player = relationship("Player", back_populates="transactions")

class SystemEvent(Base):
    """System logs and events"""
    __tablename__ = 'system_events'
    
    id = Column(Integer, primary_key=True)
    event_type = Column(String(50), index=True)  # 'login', 'logout', 'error', 'server_crash'
    severity = Column(String(20), index=True)    # 'info', 'warning', 'error', 'critical'
    message = Column(Text)
    event_metadata = Column(Text)                # JSON string
    timestamp = Column(DateTime, server_default=func.now(), index=True)

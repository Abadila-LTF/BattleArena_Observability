"""
Prometheus metrics for BattleArena API
"""

from prometheus_client import Counter, Histogram, Gauge, Info, Summary
import time

# ========================================
# HTTP METRICS
# ========================================

http_requests_total = Counter(
    'http_requests_total',
    'Total HTTP requests',
    ['method', 'endpoint', 'status']
)

http_request_duration_seconds = Histogram(
    'http_request_duration_seconds',
    'HTTP request duration in seconds',
    ['method', 'endpoint'],
    buckets=[0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0]
)

http_requests_in_progress = Gauge(
    'http_requests_in_progress',
    'Number of HTTP requests currently being processed',
    ['method', 'endpoint']
)

# ========================================
# BUSINESS METRICS
# ========================================

active_players_count = Gauge(
    'active_players_count',
    'Number of active players'
)

matches_total = Counter(
    'matches_total',
    'Total matches created',
    ['match_type', 'status']
)

revenue_total_usd = Counter(
    'revenue_total_usd',
    'Total revenue in USD',
    ['item_type']
)

# ========================================
# SYSTEM METRICS
# ========================================

api_info = Info(
    'api_info',
    'BattleArena API information'
)

# ========================================
# METRIC UPDATERS
# ========================================

def update_player_metrics(active_count: int):
    """Update active players metric"""
    active_players_count.set(active_count)

def increment_matches(match_type: str, status: str = 'started'):
    """Increment match counter"""
    matches_total.labels(match_type=match_type, status=status).inc()

def add_revenue(amount: float, item_type: str):
    """Add to revenue counter"""
    revenue_total_usd.labels(item_type=item_type).inc(amount)

# ========================================
# INITIALIZATION
# ========================================

def init_metrics():
    """Initialize metrics with API info"""
    api_info.info({
        'version': '1.0.0',
        'service': 'BattleArena API'
    })

# Call init on import
init_metrics()

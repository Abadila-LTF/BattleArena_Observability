"""
BattleArena Simulator with Jaeger Tracing - Generates realistic HTTP traffic
"""

import requests
import random
import time
from datetime import datetime
import os
import sys
import logging
from contextlib import nullcontext

# Jaeger imports
from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.instrumentation.requests import RequestsInstrumentor
from opentelemetry.sdk.resources import Resource

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ========================================
# JAEGER TRACING SETUP
# ========================================

def setup_jaeger_tracing():
    """Initialize Jaeger tracing for simulator"""
    try:
        # Create resource
        resource = Resource.create({
            "service.name": os.getenv("JAEGER_SERVICE_NAME", "battlearena-simulator"),
            "service.version": "1.0.0",
        })
        
        # Set up tracer provider
        trace.set_tracer_provider(TracerProvider(resource=resource))
        tracer = trace.get_tracer(__name__)
        
        # Create OTLP exporter
        otlp_exporter = OTLPSpanExporter(
            endpoint=f"http://{os.getenv('JAEGER_AGENT_HOST', 'localhost')}:4317",
            insecure=True,
        )
        
        # Create span processor
        span_processor = BatchSpanProcessor(otlp_exporter)
        trace.get_tracer_provider().add_span_processor(span_processor)
        
        # Instrument requests library
        RequestsInstrumentor().instrument()
        
        logger.info("Jaeger tracing initialized successfully for simulator")
        return tracer
        
    except Exception as e:
        logger.error(f"Failed to initialize Jaeger tracing: {e}")
        return None

# Initialize Jaeger
tracer = setup_jaeger_tracing()

class BattleArenaSimulator:
    def get_existing_players(self):
        """Get list of existing player IDs from the database"""
        with tracer.start_as_current_span("get_existing_players") if tracer else nullcontext():
            try:
                response = requests.get(f"{self.api_url}/api/stats/players", timeout=5)
                if response.status_code == 200:
                    data = response.json()
                    total_players = data.get('total_players', 0)
                    if total_players > 0:
                        # Generate player IDs from 1 to total_players
                        player_ids = list(range(1, total_players + 1))
                        if tracer:
                            span = trace.get_current_span()
                            span.set_attribute("players.count", total_players)
                        return player_ids
                    else:
                        print("⚠️  No players found in database")
                        return []
                else:
                    print(f"⚠️  Failed to fetch player stats: {response.status_code}")
                    return []
            except requests.exceptions.RequestException as e:
                print(f"⚠️  Failed to connect to API: {e}")
                if tracer:
                    span = trace.get_current_span()
                    span.record_exception(e)
                return []

    def __init__(self, api_url="http://localhost:8000"):
        self.api_url = api_url
        self.mode = os.getenv('SIMULATION_MODE', 'normal')
        self.active_matches = []  # Track in-progress matches
        self.player_pool = self.get_existing_players()  # Get actual players from database
        
        print(f"🎮 BattleArena Simulator with Jaeger Tracing")
        print(f"API URL: {self.api_url}")
        print(f"Mode: {self.mode}")
        print(f"Tracing: {'Enabled' if tracer else 'Disabled'}")
        print("-" * 50)

    def seed_initial_data(self, target_players=1000):
        """Seed the database with initial players if needed"""
        with tracer.start_as_current_span("seed_initial_data") if tracer else nullcontext():
            current_players = len(self.player_pool)

            if current_players >= target_players:
                print(f"✅ Already have {current_players} players (target: {target_players})")
                if tracer:
                    span = trace.get_current_span()
                    span.set_attribute("seeding.skipped", True)
                    span.set_attribute("seeding.current_players", current_players)
                return

            print(f"🌱 Seeding initial data: {current_players} → {target_players} players")

            from faker import Faker
            fake = Faker()

            players_to_create = target_players - current_players
            print(f"📝 Creating {players_to_create} players...")

            created = 0
            for i in range(current_players + 1, target_players + 1):
                with tracer.start_as_current_span("create_player") if tracer else nullcontext():
                    try:
                        response = requests.post(
                            f"{self.api_url}/api/players/register",
                            json={
                                "username": f"{fake.user_name()}_{i}",
                                "email": fake.email(),
                                "level": fake.random_int(min=1, max=50)
                            },
                            timeout=5
                        )

                        if response.status_code == 200:
                            created += 1
                            if created % 100 == 0:
                                print(f"   ✅ Created {created}/{players_to_create} players...")
                        else:
                            print(f"   ❌ Failed to create player {i}: {response.status_code}")

                    except requests.exceptions.RequestException as e:
                        print(f"   ❌ Failed to create player {i}: {e}")
                        if tracer:
                            span = trace.get_current_span()
                            span.record_exception(e)

            # Refresh player pool after seeding
            self.player_pool = self.get_existing_players()
            print(f"✅ Seeding complete! Now have {len(self.player_pool)} players")
            
            if tracer:
                span = trace.get_current_span()
                span.set_attribute("seeding.completed", True)
                span.set_attribute("seeding.players_created", created)
                span.set_attribute("seeding.final_count", len(self.player_pool))

    def get_traffic_multiplier(self):
        """Realistic traffic patterns based on time of day"""
        hour = datetime.now().hour
        
        if 18 <= hour <= 23:  # Evening peak (6 PM - 11 PM)
            return 2.0
        elif 0 <= hour <= 6:  # Night low (midnight - 6 AM)
            return 0.3
        elif 12 <= hour <= 14:  # Lunch peak
            return 1.5
        else:  # Daytime (morning/afternoon)
            return 1.0
    
    def get_mode_multiplier(self):
        """Get multiplier based on simulation mode"""
        if self.mode == 'stress':
            return 3.0
        elif self.mode == 'quiet':
            return 0.3
        else:  # normal
            return 1.0

    def simulate_player_login(self):
        """Simulate player login"""
        with tracer.start_as_current_span("simulate_player_login") if tracer else nullcontext():
            if not self.player_pool:
                return

            player_id = random.choice(self.player_pool)
            
            try:
                response = requests.post(
                    f"{self.api_url}/api/players/login",
                    json={"player_id": player_id},
                    timeout=5
                )
                
                if tracer:
                    span = trace.get_current_span()
                    span.set_attribute("login.player_id", player_id)
                    span.set_attribute("login.status_code", response.status_code)
                    span.set_attribute("login.success", response.status_code == 200)
                
                if response.status_code == 200:
                    print(f"🔐 Player {player_id} logged in")
                else:
                    print(f"❌ Login failed for player {player_id}: {response.status_code}")
                    
            except requests.exceptions.RequestException as e:
                print(f"❌ Login request failed for player {player_id}: {e}")
                if tracer:
                    span = trace.get_current_span()
                    span.record_exception(e)

    def simulate_match_start(self):
        """Simulate starting a new match"""
        with tracer.start_as_current_span("simulate_match_start") if tracer else nullcontext():
            if len(self.player_pool) < 2:
                return

            # Choose match type and players
            match_type = random.choice(['solo', 'team', 'tournament'])
            server_region = random.choice(['us-east', 'us-west', 'eu-west', 'asia-pacific'])
            
            if match_type == 'solo':
                player_count = 1
            elif match_type == 'team':
                player_count = random.randint(2, 4)
            else:  # tournament
                player_count = random.randint(4, 8)
            
            # Select random players
            selected_players = random.sample(self.player_pool, min(player_count, len(self.player_pool)))
            
            try:
                response = requests.post(
                    f"{self.api_url}/api/matches/start",
                    json={
                        "match_type": match_type,
                        "player_ids": selected_players,
                        "server_region": server_region
                    },
                    timeout=5
                )
                
                if tracer:
                    span = trace.get_current_span()
                    span.set_attribute("match.type", match_type)
                    span.set_attribute("match.player_count", len(selected_players))
                    span.set_attribute("match.server_region", server_region)
                    span.set_attribute("match.status_code", response.status_code)
                    span.set_attribute("match.success", response.status_code == 200)
                
                if response.status_code == 200:
                    data = response.json()
                    match_id = data['match_id']
                    self.active_matches.append({
                        'match_id': match_id,
                        'start_time': time.time(),
                        'match_type': match_type,
                        'players': selected_players
                    })
                    print(f"🎮 Started {match_type} match {match_id} with {len(selected_players)} players")
                else:
                    print(f"❌ Failed to start match: {response.status_code}")
                    
            except requests.exceptions.RequestException as e:
                print(f"❌ Match start request failed: {e}")
                if tracer:
                    span = trace.get_current_span()
                    span.record_exception(e)

    def simulate_match_completion(self):
        """Simulate completing an active match"""
        with tracer.start_as_current_span("simulate_match_completion") if tracer else nullcontext():
            if not self.active_matches:
                return

            # Pick a random active match
            match = random.choice(self.active_matches)
            match_id = match['match_id']
            players = match['players']
            
            # Calculate duration (1-10 minutes)
            duration = random.randint(60, 600)
            
            # Pick a winner
            winner_id = random.choice(players)
            
            # Generate participant stats
            participant_stats = []
            for player_id in players:
                participant_stats.append({
                    "player_id": player_id,
                    "score": random.randint(0, 1000),
                    "kills": random.randint(0, 20),
                    "deaths": random.randint(0, 15)
                })
            
            try:
                response = requests.post(
                    f"{self.api_url}/api/matches/complete",
                    json={
                        "match_id": match_id,
                        "winner_id": winner_id,
                        "duration_seconds": duration,
                        "participant_stats": participant_stats
                    },
                    timeout=5
                )
                
                if tracer:
                    span = trace.get_current_span()
                    span.set_attribute("match.id", match_id)
                    span.set_attribute("match.duration", duration)
                    span.set_attribute("match.winner_id", winner_id)
                    span.set_attribute("match.participants", len(players))
                    span.set_attribute("match.status_code", response.status_code)
                    span.set_attribute("match.success", response.status_code == 200)
                
                if response.status_code == 200:
                    # Remove from active matches
                    self.active_matches.remove(match)
                    print(f"🏆 Match {match_id} completed - Winner: Player {winner_id}")
                else:
                    print(f"❌ Failed to complete match {match_id}: {response.status_code}")
                    
            except requests.exceptions.RequestException as e:
                print(f"❌ Match completion request failed: {e}")
                if tracer:
                    span = trace.get_current_span()
                    span.record_exception(e)

    def simulate_transaction(self):
        """Simulate a player making a purchase"""
        with tracer.start_as_current_span("simulate_transaction") if tracer else nullcontext():
            if not self.player_pool:
                return

            player_id = random.choice(self.player_pool)
            
            # Random item purchase
            items = [
                {"type": "weapon", "name": "Legendary Sword", "amount": 9.99},
                {"type": "armor", "name": "Dragon Armor", "amount": 14.99},
                {"type": "consumable", "name": "Health Potion Pack", "amount": 4.99},
                {"type": "cosmetic", "name": "Golden Skin", "amount": 2.99},
                {"type": "currency", "name": "Gold Coins", "amount": 19.99}
            ]
            
            item = random.choice(items)
            
            try:
                response = requests.post(
                    f"{self.api_url}/api/transactions/create",
                    json={
                        "player_id": player_id,
                        "item_type": item["type"],
                        "item_name": item["name"],
                        "amount": item["amount"]
                    },
                    timeout=5
                )
                
                if tracer:
                    span = trace.get_current_span()
                    span.set_attribute("transaction.player_id", player_id)
                    span.set_attribute("transaction.item_type", item["type"])
                    span.set_attribute("transaction.item_name", item["name"])
                    span.set_attribute("transaction.amount", item["amount"])
                    span.set_attribute("transaction.status_code", response.status_code)
                    span.set_attribute("transaction.success", response.status_code == 200)
                
                if response.status_code == 200:
                    data = response.json()
                    status = data.get('status', 'unknown')
                    if status == 'completed':
                        print(f"💰 Player {player_id} purchased {item['name']} for ${item['amount']}")
                    else:
                        print(f"❌ Transaction failed for player {player_id}: {status}")
                else:
                    print(f"❌ Transaction request failed for player {player_id}: {response.status_code}")
                    
            except requests.exceptions.RequestException as e:
                print(f"❌ Transaction request failed: {e}")
                if tracer:
                    span = trace.get_current_span()
                    span.record_exception(e)

    def simulate_system_event(self):
        """Simulate system events"""
        with tracer.start_as_current_span("simulate_system_event") if tracer else nullcontext():
            events = [
                {"type": "server_restart", "severity": "info", "message": "Server restarted successfully"},
                {"type": "maintenance", "severity": "warning", "message": "Scheduled maintenance in 1 hour"},
                {"type": "performance", "severity": "warning", "message": "High CPU usage detected"},
                {"type": "security", "severity": "info", "message": "Security scan completed"},
                {"type": "backup", "severity": "info", "message": "Daily backup completed successfully"}
            ]
            
            event = random.choice(events)
            
            try:
                response = requests.post(
                    f"{self.api_url}/api/system/event",
                    json={
                        "event_type": event["type"],
                        "severity": event["severity"],
                        "message": event["message"],
                        "metadata": {"source": "simulator", "timestamp": datetime.now().isoformat()}
                    },
                    timeout=5
                )
                
                if tracer:
                    span = trace.get_current_span()
                    span.set_attribute("event.type", event["type"])
                    span.set_attribute("event.severity", event["severity"])
                    span.set_attribute("event.status_code", response.status_code)
                    span.set_attribute("event.success", response.status_code == 200)
                
                if response.status_code == 200:
                    print(f"📋 System event: {event['type']} - {event['message']}")
                else:
                    print(f"❌ Failed to log system event: {response.status_code}")
                    
            except requests.exceptions.RequestException as e:
                print(f"❌ System event request failed: {e}")
                if tracer:
                    span = trace.get_current_span()
                    span.record_exception(e)

    def run_simulation_cycle(self):
        """Run one cycle of simulation"""
        with tracer.start_as_current_span("simulation_cycle") if tracer else nullcontext():
            # Get traffic multiplier based on time and mode
            traffic_multiplier = self.get_traffic_multiplier() * self.get_mode_multiplier()
            
            if tracer:
                span = trace.get_current_span()
                span.set_attribute("simulation.traffic_multiplier", traffic_multiplier)
                span.set_attribute("simulation.mode", self.mode)
                span.set_attribute("simulation.active_matches", len(self.active_matches))
                span.set_attribute("simulation.player_pool_size", len(self.player_pool))
            
            # Simulate different activities based on probability
            activities = [
                (0.4, self.simulate_player_login),      # 40% chance
                (0.3, self.simulate_match_start),       # 30% chance
                (0.2, self.simulate_match_completion),  # 20% chance
                (0.08, self.simulate_transaction),      # 8% chance
                (0.02, self.simulate_system_event)      # 2% chance
            ]
            
            # Run activities based on traffic multiplier
            for probability, activity_func in activities:
                if random.random() < (probability * traffic_multiplier):
                    activity_func()
            
            # Clean up old matches (prevent memory leak)
            current_time = time.time()
            self.active_matches = [
                match for match in self.active_matches 
                if current_time - match['start_time'] < 1800  # 30 minutes max
            ]

    def run(self):
        """Main simulation loop"""
        print("🚀 Starting simulation...")
        
        # Seed initial data
        self.seed_initial_data()
        
        cycle_interval = int(os.getenv('CYCLE_INTERVAL', 60))
        print(f"⏰ Running simulation cycles every {cycle_interval} seconds")
        print("Press Ctrl+C to stop")
        print("-" * 50)
        
        try:
            while True:
                cycle_start = time.time()
                
                with tracer.start_as_current_span("simulation_loop") if tracer else nullcontext():
                    self.run_simulation_cycle()
                
                # Wait for next cycle
                elapsed = time.time() - cycle_start
                sleep_time = max(0, cycle_interval - elapsed)
                
                if sleep_time > 0:
                    time.sleep(sleep_time)
                    
        except KeyboardInterrupt:
            print("\n🛑 Simulation stopped by user")
        except Exception as e:
            print(f"\n❌ Simulation error: {e}")
            if tracer:
                with tracer.start_as_current_span("simulation_error") as span:
                    span.record_exception(e)

if __name__ == "__main__":
    api_url = os.getenv('API_URL', 'http://localhost:8000')
    simulator = BattleArenaSimulator(api_url)
    simulator.run()
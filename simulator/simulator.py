"""
BattleArena Simulator - Generates realistic HTTP traffic
"""

import requests
import random
import time
from datetime import datetime
import os
import sys

class BattleArenaSimulator:
    def get_existing_players(self):
        """Get list of existing player IDs from the database"""
        try:
            response = requests.get(f"{self.api_url}/api/stats/players", timeout=5)
            if response.status_code == 200:
                data = response.json()
                total_players = data.get('total_players', 0)
                if total_players > 0:
                    # Generate player IDs from 1 to total_players
                    return list(range(1, total_players + 1))
                else:
                    print("⚠️  No players found in database")
                    return []
            else:
                print(f"⚠️  Failed to fetch player stats: {response.status_code}")
                return []
        except requests.exceptions.RequestException as e:
            print(f"⚠️  Failed to connect to API: {e}")
            return []

    def __init__(self, api_url="http://localhost:8000"):
        self.api_url = api_url
        self.mode = os.getenv('SIMULATION_MODE', 'normal')
        self.active_matches = []  # Track in-progress matches
        self.player_pool = self.get_existing_players()  # Get actual players from database
        
        print(f"🎮 BattleArena Simulator")
        print(f"API URL: {self.api_url}")
        print(f"Mode: {self.mode}")
        print("-" * 50)

    def seed_initial_data(self, target_players=1000):
        """Seed the database with initial players if needed"""
        current_players = len(self.player_pool)

        if current_players >= target_players:
            print(f"✅ Already have {current_players} players (target: {target_players})")
            return

        print(f"🌱 Seeding initial data: {current_players} → {target_players} players")

        from faker import Faker
        fake = Faker()

        players_to_create = target_players - current_players
        print(f"📝 Creating {players_to_create} players...")

        created = 0
        for i in range(current_players + 1, target_players + 1):
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

        # Refresh player pool after seeding
        self.player_pool = self.get_existing_players()
        print(f"✅ Seeding complete! Now have {len(self.player_pool)} players")

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
        """Adjust traffic based on simulation mode"""
        multipliers = {
            'slow': 0.5,
            'normal': 1.0,
            'stress': 5.0,
            'tournament': 10.0
        }
        return multipliers.get(self.mode, 1.0)
    
    def simulate_logins(self, base_count=100):
        """Simulate player logins via API"""
        time_mult = self.get_traffic_multiplier()
        mode_mult = self.get_mode_multiplier()
        num_logins = int(base_count * time_mult * mode_mult)
        
        player_ids = random.sample(self.player_pool, min(num_logins, len(self.player_pool)))
        
        success = 0
        failures = 0
        
        for player_id in player_ids:
            try:
                response = requests.post(
                    f"{self.api_url}/api/players/login",
                    json={"player_id": player_id},
                    timeout=2
                )
                
                if response.status_code == 200:
                    success += 1
                else:
                    failures += 1
                    
            except requests.exceptions.RequestException:
                failures += 1
        
        total = success + failures
        success_rate = (success / total * 100) if total > 0 else 0
        print(f"  🔐 Logins: {success}/{total} ({success_rate:.1f}% success)")
        return success
    
    def simulate_matches(self, base_count=20):
        """Simulate match lifecycle via API"""
        time_mult = self.get_traffic_multiplier()
        mode_mult = self.get_mode_multiplier()
        num_new_matches = int(base_count * time_mult * mode_mult)
        
        started = 0
        completed = 0
        crashed = 0
        
        # Start new matches
        for _ in range(num_new_matches):
            try:
                match_type = random.choice(['solo', 'team', 'team', 'tournament'])  # Weighted
                num_players = 2 if match_type == 'solo' else random.randint(4, 10)
                
                player_ids = random.sample(self.player_pool, num_players)
                
                response = requests.post(
                    f"{self.api_url}/api/matches/start",
                    json={
                        "match_type": match_type,
                        "player_ids": player_ids,
                        "server_region": random.choice(['us-east', 'eu-west', 'asia'])
                    },
                    timeout=2
                )
                
                if response.status_code == 200:
                    match_data = response.json()
                    self.active_matches.append({
                        'match_id': match_data['match_id'],
                        'match_type': match_type,
                        'player_ids': player_ids,
                        'start_time': time.time()
                    })
                    started += 1
                    
            except requests.exceptions.RequestException:
                pass
        
        # Complete matches that are ready
        matches_to_complete = []
        current_time = time.time()
        
        for match in self.active_matches[:]:
            duration = current_time - match['start_time']
            
            # Match should last 5-30 seconds (accelerated for demo)
            if duration >= random.randint(5, 30):
                matches_to_complete.append(match)
                self.active_matches.remove(match)
        
        # Process completions
        for match in matches_to_complete:
            try:
                # 2% chance of crash
                if random.random() < 0.02:
                    response = requests.post(
                        f"{self.api_url}/api/matches/crash",
                        json={
                            "match_id": match['match_id'],
                            "error_message": random.choice([
                                "Server timeout",
                                "Memory overflow",
                                "Network disconnection",
                                "Unexpected exception",
                                "Database deadlock"
                            ])
                        },
                        timeout=2
                    )
                    if response.status_code == 200:
                        crashed += 1
                else:
                    # Normal completion
                    winner_id = random.choice(match['player_ids'])
                    duration_seconds = int(current_time - match['start_time'])
                    
                    participant_stats = [
                        {
                            'player_id': pid,
                            'score': random.randint(100, 5000),
                            'kills': random.randint(0, 20),
                            'deaths': random.randint(0, 15)
                        }
                        for pid in match['player_ids']
                    ]
                    
                    response = requests.post(
                        f"{self.api_url}/api/matches/complete",
                        json={
                            "match_id": match['match_id'],
                            "winner_id": winner_id,
                            "duration_seconds": duration_seconds,
                            "participant_stats": participant_stats
                        },
                        timeout=2
                    )
                    
                    if response.status_code == 200:
                        completed += 1
                        
            except requests.exceptions.RequestException:
                pass
        
        print(f"  🎯 Matches: {started} started, {completed} completed, {crashed} crashed")
        print(f"     Active matches: {len(self.active_matches)}")
        return started + completed
    
    def simulate_transactions(self, base_count=10):
        """Simulate purchases via API"""
        time_mult = self.get_traffic_multiplier()
        mode_mult = self.get_mode_multiplier()
        num_transactions = int(base_count * time_mult * mode_mult)
        
        player_ids = random.sample(self.player_pool, min(num_transactions, len(self.player_pool)))
        
        items = [
            ('skin', 'Dragon Armor', 9.99),
            ('weapon', 'Legendary Sword', 14.99),
            ('currency', '1000 Gold', 4.99),
            ('skin', 'Galaxy Wings', 19.99),
            ('weapon', 'Fire Staff', 12.99),
            ('currency', '500 Gold', 2.99),
            ('skin', 'Ice Crown', 24.99),
            ('weapon', 'Shadow Blade', 16.99),
        ]
        
        success = 0
        total_revenue = 0.0
        
        for player_id in player_ids:
            try:
                item_type, item_name, amount = random.choice(items)
                
                response = requests.post(
                    f"{self.api_url}/api/transactions/create",
                    json={
                        "player_id": player_id,
                        "item_type": item_type,
                        "item_name": item_name,
                        "amount": amount
                    },
                    timeout=2
                )
                
                if response.status_code == 200:
                    result = response.json()
                    if result['status'] == 'completed':
                        success += 1
                        total_revenue += amount
                    
            except requests.exceptions.RequestException:
                pass
        
        print(f"  💰 Transactions: {success} successful, ${total_revenue:.2f} revenue")
        return success
    
    def inject_chaos(self):
        """Inject random system failures via API"""
        if random.random() < 0.05:  # 5% chance per cycle
            chaos_events = [
                ('database_slow', 'error', 'Database query exceeded 5s'),
                ('api_timeout', 'error', 'API endpoint timed out'),
                ('memory_leak', 'warning', 'Memory usage at 85%'),
                ('network_partition', 'critical', 'Network connection lost'),
                ('disk_full', 'critical', 'Disk usage at 95%'),
                ('high_cpu', 'warning', 'CPU usage at 90%'),
            ]
            
            event_type, severity, message = random.choice(chaos_events)
            
            try:
                response = requests.post(
                    f"{self.api_url}/api/system/event",
                    json={
                        "event_type": event_type,
                        "severity": severity,
                        "message": message,
                        "metadata": {
                            "timestamp": datetime.now().isoformat(),
                            "source": "simulator"
                        }
                    },
                    timeout=2
                )
                
                if response.status_code == 200:
                    print(f"  💥 CHAOS: {message}")
                    
            except requests.exceptions.RequestException:
                pass
    
    def check_api_health(self):
        """Check if API is responding"""
        try:
            response = requests.get(f"{self.api_url}/health", timeout=5)
            data = response.json()
            return data.get('status') == 'healthy'
        except:
            return False
    
    def get_current_stats(self):
        """Fetch and display current system stats"""
        try:
            stats_response = requests.get(f"{self.api_url}/api/stats/players", timeout=3)
            matches_response = requests.get(f"{self.api_url}/api/stats/matches", timeout=3)
            revenue_response = requests.get(f"{self.api_url}/api/stats/revenue", timeout=3)
            
            if all(r.status_code == 200 for r in [stats_response, matches_response, revenue_response]):
                stats = stats_response.json()
                matches = matches_response.json()
                revenue = revenue_response.json()
                
                print(f"\n📊 System Stats:")
                print(f"   Players: {stats['total_players']} total, {stats['active_now']} active now")
                print(f"   Matches: {matches['in_progress']} in progress, {matches['completed_today']} completed today")
                print(f"   Revenue: ${revenue['revenue_today']:.2f} today")
                print()
        except:
            pass
    
    def run_cycle(self):
        """Run one simulation cycle"""
        timestamp = datetime.now().strftime('%H:%M:%S')
        print(f"\n{'='*60}")
        print(f"🎮 CYCLE START [{timestamp}] - Mode: {self.mode}")
        print(f"{'='*60}")
        
        # Check API health first
        if not self.check_api_health():
            print("❌ API is not responding, skipping cycle")
            print("   Please check if the API is running")
            return
        
        # Run simulations
        total_requests = 0
        total_requests += self.simulate_logins()
        total_requests += self.simulate_matches()
        total_requests += self.simulate_transactions()
        self.inject_chaos()
        
        # Show current stats
        self.get_current_stats()
        
        print(f"✅ Cycle complete - {total_requests} total API requests")
    
    def run(self, interval_seconds=60):
        """Run simulator continuously"""
        print("\n🚀 BattleArena Simulator Started")
        print(f"Cycle interval: {interval_seconds}s")
        print(f"Press Ctrl+C to stop")
        print("="*60)
        
        # Wait for API to be ready
        print("⏳ Waiting for API to be ready...")
        retries = 0
        while not self.check_api_health():
            time.sleep(2)
            retries += 1
            if retries > 30:
                print("❌ API did not become ready. Exiting.")
                sys.exit(1)
        
        print("✅ API is ready!\n")

        # Seed initial data if needed
        self.seed_initial_data()

        try:
            while True:
                self.run_cycle()
                time.sleep(interval_seconds)
        except KeyboardInterrupt:
            print("\n\n🛑 Simulator stopped by user")
            print(f"Final active matches: {len(self.active_matches)}")

if __name__ == '__main__':
    # Configuration from environment
    api_url = os.getenv('API_URL', 'http://localhost:8000')
    mode = os.getenv('SIMULATION_MODE', 'normal')
    interval = int(os.getenv('CYCLE_INTERVAL', '60'))
    
    # Create and run simulator
    simulator = BattleArenaSimulator(api_url=api_url)
    simulator.mode = mode
    simulator.run(interval_seconds=interval)

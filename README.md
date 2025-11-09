# 📊 BattleArena Observability - Production Monitoring Stack

A complete, production-ready observability solution for the BattleArena gaming platform featuring Prometheus metrics collection, Grafana dashboards, infrastructure monitoring, and distributed tracing with Jaeger.

---

## 🎓 Getting Started - Step by Step

Follow these steps to learn observability from basic monitoring to advanced distributed tracing!

### **Step 1: Prometheus & Grafana (Basic Monitoring)**

Start with the fundamentals - application metrics collection and visualization!

#### **What You'll Learn:**
- How Prometheus collects metrics from your application
- How to visualize metrics with Grafana dashboards
- How to query metrics using PromQL
- Application-level monitoring (HTTP requests, business metrics, etc.)

#### **Setup:**

1. **Start the basic monitoring stack:**
   ```bash
   docker-compose up -d
   ```

2. **Wait for services to be ready (about 30 seconds):**
   ```bash
   # Check status
   docker-compose ps
   
   # View logs
   docker-compose logs -f
   ```

3. **Access the monitoring tools:**
   ```bash
   # Grafana Dashboards (Username: admin, Password: admin123)
   open http://localhost:3000
   
   # Prometheus Query Interface
   open http://localhost:9090
   
   # API Metrics Endpoint
   curl http://localhost:8000/metrics
   ```

4. **Explore Grafana:**
   - Navigate to **Dashboards** → **System Overview**
   - See real-time metrics: active players, request rates, response times
   - Check the **In-Depth Dashboard** for detailed analytics

5. **Try Prometheus queries:**
   ```promql
   # Request rate
   rate(http_requests_total[5m])
   
   # Active players
   active_players_count
   
   # Response time 95th percentile
   histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m]))
   ```

6. **Test the API to generate metrics:**
   ```bash
   # Generate some traffic
   curl http://localhost:8000/health
   curl http://localhost:8000/api/stats/players
   
   # Watch metrics update in Grafana!
   ```

**✅ Success!** You now have basic application monitoring with Prometheus and Grafana!

**What's Running:**
- ✅ BattleArena API (with Prometheus metrics)
- ✅ PostgreSQL Database
- ✅ Traffic Simulator (generating load)
- ✅ Prometheus (collecting metrics)
- ✅ Grafana (visualizing metrics)

---

### **Step 2: Node Exporter & PostgreSQL Exporter (Infrastructure Monitoring)**

Add infrastructure monitoring to see system-level metrics - CPU, memory, disk, and database performance!

#### **What You'll Learn:**
- How to monitor system resources (CPU, memory, disk, network)
- How to monitor database performance (connections, queries, locks)
- Infrastructure-level observability
- Complete visibility into your system's health

#### **Setup:**

1. **Stop the basic stack (if running):**
   ```bash
   docker-compose down
   ```

2. **Start the extended monitoring stack:**
   ```bash
   docker-compose -f docker-compose-extended.yml up -d
   ```

3. **Wait for services to be ready:**
   ```bash
   # Check all services are running
   docker-compose -f docker-compose-extended.yml ps
   ```

4. **Access the new exporters:**
   ```bash
   # Node Exporter (System metrics)
   curl http://localhost:9100/metrics | head -20
   
   # PostgreSQL Exporter (Database metrics)
   curl http://localhost:9187/metrics | head -20
   ```

5. **Explore new metrics in Prometheus:**
   ```bash
   # Open Prometheus
   open http://localhost:9090
   ```

   **Try these queries:**
   ```promql
   # CPU Usage
   rate(node_cpu_seconds_total[5m])
   
   # Available Memory
   node_memory_MemAvailable_bytes
   
   # Disk Space
   node_filesystem_avail_bytes
   
   # Database Connections
   pg_stat_database_numbackends
   
   # Database Size
   pg_database_size_bytes
   ```

6. **View in Grafana:**
   ```bash
   # Open Grafana
   open http://localhost:3000
   ```
   
   - The dashboards now include infrastructure metrics
   - You can see system resource usage alongside application metrics
   - Database performance metrics are available

**✅ Success!** You now have complete infrastructure monitoring!

**What's New:**
- ✅ **Node Exporter** - System metrics (CPU, memory, disk, network)
- ✅ **PostgreSQL Exporter** - Database metrics (connections, queries, performance)
- ✅ Enhanced Prometheus configuration to scrape exporters
- ✅ Complete visibility into infrastructure health

**Key Metrics Added:**
- System CPU usage and load
- Memory consumption and availability
- Disk I/O and space usage
- Network traffic
- Database connection pools
- Query performance and cache hit ratios
- Database locks and transactions

---

### **Step 3: Jaeger (Distributed Tracing)**

Add distributed tracing to see the complete journey of requests across your system!

#### **What You'll Learn:**
- How distributed tracing works
- How to trace requests across services
- How to identify performance bottlenecks
- How to debug issues with full request context
- End-to-end visibility into request flows

#### **Setup:**

1. **Stop the extended stack (if running):**
   ```bash
   docker-compose -f docker-compose-extended.yml down
   ```

2. **Start the Jaeger tracing stack:**
   ```bash
   docker-compose -f docker-compose-jaeger.yml up -d
   ```

3. **Wait for services to be ready:**
   ```bash
   # Check all services are running
   docker-compose -f docker-compose-jaeger.yml ps
   
   # View logs to see tracing in action
   docker-compose -f docker-compose-jaeger.yml logs -f api
   ```

4. **Access Jaeger UI:**
   ```bash
   # Open Jaeger UI
   open http://localhost:16686
   ```

5. **Generate some traffic to create traces:**
   ```bash
   # The simulator is already running and generating traced requests!
   # Or manually trigger some API calls:
   curl http://localhost:8000/api/stats/players
   curl http://localhost:8000/api/leaderboard
   ```

6. **Explore traces in Jaeger:**
   - Go to **Search** tab in Jaeger UI
   - Select service: `battlearena-api` or `battlearena-simulator`
   - Click **Find Traces**
   - Click on a trace to see the complete request flow!

7. **Understand trace structure:**
   ```
   POST /api/players/login
   ├── player_login (custom span)
   │   ├── SELECT battlearena (find player)
   │   ├── UPDATE battlearena (update last_login)
   │   └── INSERT battlearena (log system event)
   └── HTTP Response
   ```

8. **View trace details:**
   - See timing for each operation
   - Check for errors and exceptions
   - View custom attributes (player ID, username, etc.)
   - Analyze performance bottlenecks

**✅ Success!** You now have distributed tracing with Jaeger!

**What's New:**
- ✅ **Jaeger** - Distributed tracing backend
- ✅ **OTLP Collector** - Modern OpenTelemetry protocol
- ✅ **Instrumented API** - Traces all requests automatically
- ✅ **Instrumented Simulator** - Traces traffic generation
- ✅ **Complete Request Visibility** - See requests from start to finish

**Key Features:**
- **Request Flow Visualization**: See complete request journey across services
- **Performance Analysis**: Identify bottlenecks and slow operations
- **Error Tracking**: Trace errors to their source with full context
- **Service Dependencies**: Understand how services interact
- **Business Context**: Custom attributes for business logic tracing

**Custom Business Attributes:**
- `player.id`: Player identifier
- `player.username`: Player username
- `match.type`: Match type (solo/team/tournament)
- `transaction.amount`: Transaction value
- `login.timestamp`: Login time

---

## 🚀 Quick Start (All-in-One)

If you want to jump straight to the complete stack with everything:

```bash
# Start complete observability stack (Prometheus + Grafana + Exporters + Jaeger)
docker-compose -f docker-compose-jaeger.yml up -d

# Wait 30 seconds, then:
open http://localhost:3000   # Grafana (admin/admin123)
open http://localhost:9090   # Prometheus
open http://localhost:16686  # Jaeger
```

---

## 📚 What You're Learning

This project teaches you:

### **Observability Fundamentals**
- **Prometheus Metrics**: Custom metrics collection and exposition
- **Grafana Dashboards**: Real-time visualization and monitoring
- **Service Discovery**: Automatic target discovery and scraping
- **Metric Design**: Effective metric naming and labeling

### **Production Monitoring**
- **Application Metrics**: Business and technical metrics collection
- **Infrastructure Monitoring**: System performance and resource usage
- **Dashboard Design**: Effective visualization of complex data
- **Performance Analysis**: Using metrics for optimization

### **DevOps Best Practices**
- **Monitoring as Code**: Configuration management for observability
- **Metric Design**: Effective metric naming and labeling
- **Dashboard Design**: User-friendly monitoring interfaces
- **Performance Optimization**: Using metrics to improve system performance

---

## 🏗️ Observability Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    Observability Stack                        │
│                                                                 │
│  ┌─────────────────┐    ┌─────────────────┐    ┌─────────────┐ │
│  │   BattleArena   │    │   Prometheus    │    │   Grafana   │ │
│  │      API        │    │                 │    │             │ │
│  │                 │    │ • Metrics       │    │ • Dashboards│ │
│  │ • Custom        │◄──►│   Collection    │◄──►│ • Queries   │ │
│  │   Metrics       │    │ • Storage       │    │ • Viz       │ │
│  │ • /metrics      │    │ • Querying      │    │ • Analysis  │ │
│  │   Endpoint      │    │ • Time Series   │    │             │ │
│  └─────────────────┘    └─────────────────┘    └─────────────┘ │
│           │                       │                   │        │
│           ▼                       ▼                   ▼        │
│  ┌─────────────────┐    ┌─────────────────┐    ┌─────────────┐ │
│  │   Simulator     │    │   Metrics       │    │   Analysis  │ │
│  │                 │    │   Storage       │    │             │ │
│  │ • Load Testing  │    │ • Historical    │    │ • Trends    │ │
│  │ • Traffic       │    │   Data          │    │ • Patterns  │ │
│  │   Generation    │    │ • Query Engine  │    │ • Insights  │ │
│  │ • Auto-Seeding  │    │ • Data Export   │    │ • Reports   │ │
│  └─────────────────┘    └─────────────────┘    └─────────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

### **Core Components**

1. **BattleArena API** (FastAPI Application)
   - Custom Prometheus metrics (20+ metrics)
   - `/metrics` endpoint for Prometheus scraping
   - Business and technical metrics collection
   - Real-time performance monitoring

2. **Prometheus** (Metrics Collection & Storage)
   - Scrapes metrics from API every 5 seconds
   - Stores time-series data for historical analysis
   - Provides query language (PromQL) for data analysis
   - Exports metrics for external systems

3. **Grafana** (Visualization & Dashboards)
   - Interactive dashboards for system monitoring
   - Real-time visualization of metrics
   - Historical data analysis and trends
   - Custom dashboard for BattleArena metrics

4. **Traffic Simulator** (Load Testing)
   - Generates realistic gaming traffic
   - Automatically seeds database with test players
   - Creates load for monitoring and testing
   - Simulates various user behaviors

---

## 📊 Prometheus Metrics

### **HTTP Metrics**

| Metric | Type | Description | Labels |
|--------|------|-------------|--------|
| `http_requests_total` | Counter | Total HTTP requests | method, endpoint, status |
| `http_request_duration_seconds` | Histogram | Request latency | method, endpoint |
| `http_requests_in_progress` | Gauge | Active requests | method, endpoint |

### **Business Metrics**

| Metric | Type | Description | Labels |
|--------|------|-------------|--------|
| `active_players_count` | Gauge | Current active players | - |
| `matches_total` | Counter | Total matches created | match_type, status |
| `revenue_total_usd` | Counter | Total revenue | item_type |
| `player_registrations_total` | Counter | Total registrations | - |
| `player_logins_total` | Counter | Total logins | - |

### **System Metrics**

| Metric | Type | Description | Labels |
|--------|------|-------------|--------|
| `matches_in_progress` | Gauge | Current active matches | - |
| `matches_crashed_total` | Counter | Total crashed matches | - |
| `transactions_total` | Counter | Total transactions | type, status |
| `transaction_failure_rate` | Gauge | Transaction failure rate | - |

### **Database Metrics**

| Metric | Type | Description | Labels |
|--------|------|-------------|--------|
| `database_connections_active` | Gauge | Active DB connections | - |
| `database_queries_total` | Counter | Total DB queries | query_type |
| `database_query_duration_seconds` | Histogram | DB query latency | query_type |

---

## 📈 Grafana Dashboards

### **System Overview Dashboard**

Access at `http://localhost:3000` (admin/admin123):

**Key Panels:**
- **Active Players**: Real-time player count
- **HTTP Request Rate**: Requests per second
- **Response Time**: API latency percentiles
- **Error Rate**: 4xx/5xx error percentage
- **Revenue**: Total revenue tracking
- **Match Statistics**: Match creation and completion rates

**Dashboard Features:**
- **Real-time Updates**: 30-second refresh interval
- **Interactive Queries**: Click to drill down
- **Threshold Alerts**: Visual indicators for issues
- **Time Range Selection**: Historical analysis
- **Export Capabilities**: PNG, PDF, JSON export

### **In-Depth Dashboard**

Advanced monitoring with detailed metrics:
- **Performance Metrics**: Detailed latency analysis
- **Business Analytics**: Player behavior patterns
- **System Health**: Resource usage and performance
- **Error Analysis**: Detailed error tracking
- **Capacity Planning**: Growth trends and projections

---

## 🛠️ Monitoring Operations

### **Accessing the Stack**

```bash
# Grafana Dashboards
open http://localhost:3000
# Username: admin, Password: admin123

# Prometheus Query Interface
open http://localhost:9090


# API Metrics Endpoint
curl http://localhost:8000/metrics
```

### **Prometheus Queries**

**Basic Queries:**
```promql
# Request rate
rate(http_requests_total[5m])

# Response time 95th percentile
histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m]))

# Active players
active_players_count

# Error rate
rate(http_requests_total{status=~"5.."}[5m])
```

**Advanced Queries:**
```promql
# Revenue per hour
rate(revenue_total_usd[1h])

# Match completion rate
rate(matches_total{status="completed"}[5m]) / rate(matches_total[5m])

# Top endpoints by request count
topk(10, rate(http_requests_total[5m]))
```

### **Dashboard Management**

```bash
# View dashboard configuration
cat monitoring/grafana/dashboards/system-overview.json

# Update dashboard
# Edit JSON file and restart Grafana

# Create new dashboard
# Use Grafana UI or import JSON configuration
```

---

## 🔧 Customization Guide

### **Adding New Metrics**

Edit `app/metrics.py`:
```python
from prometheus_client import Counter, Gauge

# Add new business metric
new_metric = Counter(
    'new_business_metric_total',
    'Description of new metric',
    ['label1', 'label2']
)

# Increment metric in your code
new_metric.labels(label1='value1', label2='value2').inc()
```

### **Creating Custom Dashboards**

1. **Access Grafana**: `http://localhost:3000`
2. **Create Dashboard**: Click "+" → "Dashboard"
3. **Add Panels**: Configure queries and visualizations
4. **Export Configuration**: Save as JSON
5. **Add to Project**: Place in `monitoring/grafana/dashboards/`

### **Adding Custom Metrics**

Edit `app/metrics.py` to add new business metrics:
```python
from prometheus_client import Counter, Gauge

# Add new business metric
custom_metric = Counter(
    'custom_business_metric_total',
    'Description of your custom metric',
    ['label1', 'label2']
)

# Use in your application
custom_metric.labels(label1='value1', label2='value2').inc()
```

---

## 🐛 Troubleshooting

### **Common Issues**

**Prometheus not scraping metrics:**
```bash
# Check Prometheus targets
curl http://localhost:9090/api/v1/targets

# Check API metrics endpoint
curl http://localhost:8000/metrics

# Check Prometheus configuration
docker-compose logs prometheus
```

**Grafana dashboard not loading:**
```bash
# Check Grafana logs
docker-compose logs grafana

# Verify dashboard configuration
cat monitoring/grafana/dashboards/system-overview.json | jq .

# Check data source connection
# Grafana UI → Configuration → Data Sources
```

**Prometheus queries not working:**
```bash
# Check Prometheus targets
curl http://localhost:9090/api/v1/targets

# Test query in Prometheus UI
# Prometheus UI → Graph → Enter expression

# Check Prometheus configuration
docker-compose logs prometheus
```

**Metrics not appearing:**
```bash
# Check API logs
docker-compose logs api

# Verify metrics endpoint
curl -v http://localhost:8000/metrics

# Check Prometheus scrape config
cat monitoring/prometheus/prometheus.yml
```

### **Performance Issues**

**High memory usage:**
```bash
# Check Prometheus memory
docker stats prometheus

# Adjust retention settings
# Edit monitoring/prometheus/prometheus.yml
```

**Slow dashboard loading:**
```bash
# Check Grafana performance
docker stats grafana

# Optimize queries
# Use more specific time ranges
# Reduce panel refresh intervals
```

---

## 📚 Learning Resources

### **Prometheus & Monitoring**
- [Prometheus Documentation](https://prometheus.io/docs/)
- [PromQL Query Language](https://prometheus.io/docs/prometheus/latest/querying/)
- [Prometheus Best Practices](https://prometheus.io/docs/practices/)

### **Grafana & Visualization**
- [Grafana Documentation](https://grafana.com/docs/)
- [Dashboard Design Best Practices](https://grafana.com/docs/grafana/latest/best-practices/)
- [Panel Types and Visualizations](https://grafana.com/docs/grafana/latest/panels/)

### **Operations & Analysis**
- [Prometheus Best Practices](https://prometheus.io/docs/practices/)
- [Monitoring Best Practices](https://sre.google/sre-book/monitoring-distributed-systems/)
- [Time Series Analysis](https://prometheus.io/docs/prometheus/latest/querying/basics/)

---

## 🎓 What You've Built

This observability stack demonstrates:

✅ **Comprehensive Monitoring**: 20+ custom metrics for business and technical monitoring  
✅ **Real-time Dashboards**: Interactive Grafana dashboards with live data  
✅ **Historical Analysis**: Time-series data for trend analysis and insights  
✅ **Production-Ready**: Scalable monitoring solution for production environments  
✅ **Business Intelligence**: Metrics that drive business decisions  
✅ **Performance Optimization**: Data-driven insights for system improvement  

---

## 🚀 Next Steps

### **After Step 1 (Prometheus & Grafana)**
1. **Explore Dashboards**: Navigate through Grafana dashboards
2. **Try PromQL Queries**: Experiment with different Prometheus queries
3. **Customize Metrics**: Add business-specific metrics to the API
4. **Create Custom Dashboards**: Build your own Grafana dashboards

### **After Step 2 (Infrastructure Monitoring)**
1. **Analyze System Metrics**: Use Node Exporter metrics to understand resource usage
2. **Database Performance**: Analyze PostgreSQL Exporter metrics
3. **Capacity Planning**: Use infrastructure metrics for resource planning
4. **Create Infrastructure Dashboards**: Build dashboards for system health

### **After Step 3 (Distributed Tracing)**
1. **Trace Analysis**: Explore different traces in Jaeger
2. **Performance Optimization**: Use traces to identify bottlenecks
3. **Error Debugging**: Use traces to debug issues
4. **Correlate Metrics & Traces**: Combine Prometheus metrics with Jaeger traces

### **Advanced Topics**
1. **Log Aggregation**: Integrate ELK stack for log analysis
2. **Service Mesh**: Monitor Istio service mesh with observability
3. **Machine Learning**: Implement ML-based anomaly detection
4. **Custom Alerting**: Add Alertmanager for Prometheus alerts
5. **Multi-Service Tracing**: Extend tracing to more services

---

## 📄 Project Structure

```
BattleArena_Observability/
├── app/                    # FastAPI application with metrics
│   ├── api.py             # Main API with Prometheus integration
│   ├── models.py          # Database models (5 tables)
│   ├── schemas.py         # Request/response validation
│   ├── database.py        # Database connection
│   ├── config.py          # Configuration management
│   └── metrics.py         # Prometheus metrics definition (20+ metrics)
├── app-jaeger/            # FastAPI application with Jaeger tracing
│   ├── api.py             # Main API with OpenTelemetry/Jaeger integration
│   └── ...                # Same structure as app/
├── simulator/             # Traffic simulation
│   └── simulator.py       # Main simulator logic (includes auto-seeding)
├── simulator-jaeger/      # Traffic simulation with Jaeger tracing
│   └── simulator.py       # Simulator with OpenTelemetry/Jaeger integration
├── monitoring/            # Observability stack configuration
│   ├── prometheus/
│   │   ├── prometheus.yml           # Basic Prometheus config
│   │   ├── prometheus-extended.yml  # With exporters
│   │   └── prometheus-jaeger.yml    # With Jaeger integration
│   └── grafana/
│       ├── dashboards/
│       │   ├── system-overview.json    # Main dashboard
│       │   └── indepth-dashboard.json  # Advanced dashboard
│       └── provisioning/
│           ├── datasources/
│           │   └── prometheus.yml      # Prometheus data source
│           └── dashboards/
│               └── dashboard.yml       # Dashboard provisioning
├── docker-compose.yml           # Step 1: Basic monitoring (Prometheus + Grafana)
├── docker-compose-extended.yml   # Step 2: + Node/Postgres exporters
├── docker-compose-jaeger.yml     # Step 3: + Jaeger distributed tracing
├── Dockerfile                    # API container (basic)
├── Dockerfile.jaeger             # API container (with Jaeger)
├── Dockerfile.simulator           # Simulator container (basic)
├── Dockerfile.simulator.jaeger    # Simulator container (with Jaeger)
├── requirements.txt              # Python dependencies
└── requirements-jaeger.txt        # Additional dependencies for Jaeger
```

---

## 📋 Docker Compose Files Overview

This project includes three Docker Compose configurations for progressive learning:

### **1. Basic Monitoring (`docker-compose.yml`)**
- BattleArena API with Prometheus metrics
- PostgreSQL Database
- Traffic Simulator
- Prometheus (metrics collection)
- Grafana (visualization)

**Use for:** Step 1 - Learning basic application monitoring

### **2. Extended Monitoring (`docker-compose-extended.yml`)**
- Everything from basic monitoring, plus:
- Node Exporter (system metrics)
- PostgreSQL Exporter (database metrics)

**Use for:** Step 2 - Learning infrastructure monitoring

### **3. Complete Stack with Tracing (`docker-compose-jaeger.yml`)**
- Everything from extended monitoring, plus:
- Jaeger (distributed tracing)
- Instrumented API and Simulator with OpenTelemetry

**Use for:** Step 3 - Learning distributed tracing

---

## 🔧 Switching Between Configurations

To switch between different monitoring configurations:

```bash
# Stop current stack
docker-compose -f <current-file>.yml down

# Start new stack
docker-compose -f <new-file>.yml up -d
```

**Note:** Each configuration uses different volume names to avoid conflicts, so you can have multiple stacks running simultaneously if needed (on different ports).

---

## 🎯 Success Criteria

After completing all three steps, you should understand:

### **Step 1 - Basic Monitoring:**
- ✅ How Prometheus collects metrics from applications
- ✅ How to visualize metrics with Grafana dashboards
- ✅ How to query metrics using PromQL
- ✅ How to implement custom Prometheus metrics
- ✅ How to design meaningful business and technical metrics

### **Step 2 - Infrastructure Monitoring:**
- ✅ How to monitor system resources (CPU, memory, disk, network)
- ✅ How to monitor database performance
- ✅ How exporters work and integrate with Prometheus
- ✅ How to achieve complete infrastructure visibility

### **Step 3 - Distributed Tracing:**
- ✅ How distributed tracing works
- ✅ How to trace requests across services
- ✅ How to identify performance bottlenecks using traces
- ✅ How to debug issues with full request context
- ✅ How to correlate traces with metrics for complete observability

---

**🎉 Congratulations! You now have a solid foundation in observability and production monitoring!**

For questions or issues, check the troubleshooting section or explore the monitoring configurations - they're designed to be educational and production-ready.

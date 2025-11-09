# 📊 BattleArena Observability - Production Monitoring Stack

A complete, production-ready observability solution for the BattleArena gaming platform featuring Prometheus metrics collection and Grafana dashboards for comprehensive monitoring.

## 🚀 Quick Start (10 minutes)

### **Start the Complete Observability Stack**
```bash
# 1. Start all services with monitoring
docker-compose up -d

# 2. Wait for services to be ready (30 seconds)
sleep 30

# 3. Access the monitoring stack
open http://localhost:3000  # Grafana (admin/admin123)
open http://localhost:9090  # Prometheus

# 4. View API metrics
curl http://localhost:8000/metrics

# 5. Check API health
curl http://localhost:8000/health
```

**That's it!** You now have a complete observability stack running! 📊

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

### **Immediate Actions**
1. **Explore Dashboards**: Navigate through Grafana dashboards
2. **Analyze Metrics**: Use Prometheus queries to explore data
3. **Customize Metrics**: Add business-specific metrics
4. **Create Dashboards**: Build custom dashboards for your use case

### **Learning Extensions**
1. **Add More Metrics**: Implement additional business metrics
2. **Advanced Queries**: Create complex PromQL queries
3. **Integration**: Connect with external monitoring systems
4. **Performance Analysis**: Use metrics to optimize system performance

### **Advanced Topics**
1. **Distributed Tracing**: Add Jaeger for request tracing
2. **Log Aggregation**: Integrate ELK stack for log analysis
3. **Service Mesh**: Monitor Istio service mesh
4. **Machine Learning**: Implement ML-based anomaly detection
5. **Custom Alerting**: Add external alerting systems if needed

---

## 📄 Project Structure

```
4-battlearena_observability/
├── app/                    # FastAPI application with metrics
│   ├── api.py             # Main API with Prometheus integration
│   ├── models.py          # Database models (5 tables)
│   ├── schemas.py         # Request/response validation
│   ├── database.py        # Database connection
│   ├── config.py          # Configuration management
│   └── metrics.py         # Prometheus metrics definition (20+ metrics)
├── simulator/             # Traffic simulation
│   └── simulator.py       # Main simulator logic (includes auto-seeding)
├── monitoring/            # Observability stack configuration
│   ├── prometheus/
│   │   └── prometheus.yml # Prometheus configuration
│   └── grafana/
│       ├── dashboards/
│       │   ├── system-overview.json    # Main dashboard
│       │   └── indepth-dashboard.json  # Advanced dashboard
│       └── provisioning/
│           ├── datasources/
│           │   └── prometheus.yml      # Prometheus data source
│           └── dashboards/
│               └── dashboard.yml       # Dashboard provisioning
├── docker-compose.yml     # Complete stack with monitoring
├── Dockerfile             # API container
├── Dockerfile.simulator   # Simulator container
└── requirements.txt       # Python dependencies
```

---

## 🔧 Extended Monitoring Stack

This project includes two additional monitoring configurations for enhanced observability:

### **1. Extended Prometheus Stack (`docker-compose-extended.yml`)**

The extended stack adds **Node Exporter** and **PostgreSQL Exporter** for comprehensive infrastructure monitoring:

#### **Additional Services:**
- **Node Exporter** (Port 9100): System-level metrics (CPU, memory, disk, network)
- **PostgreSQL Exporter** (Port 9187): Database-specific metrics (connections, queries, performance)

#### **Enhanced Monitoring Capabilities:**
```bash
# Start the extended monitoring stack
docker-compose -f docker-compose-extended.yml up -d

# Access additional metrics
curl http://localhost:9100/metrics  # Node Exporter
curl http://localhost:9187/metrics  # PostgreSQL Exporter
```

#### **What You Get:**
- **System Metrics**: CPU usage, memory consumption, disk I/O, network traffic
- **Database Metrics**: Connection pools, query performance, cache hit ratios, lock information
- **Infrastructure Health**: Complete visibility into host and database performance
- **Resource Planning**: Track resource utilization for capacity planning

#### **Key Metrics Added:**
```promql
# System Health
node_cpu_seconds_total{cpu="0",mode="idle"}
node_memory_MemAvailable_bytes
node_filesystem_avail_bytes

# Database Performance
pg_stat_database_*  # Database statistics
pg_stat_user_tables_*  # Table performance
pg_locks_*  # Lock information
```

---

### **2. Jaeger Distributed Tracing (`docker-compose-jaeger.yml`)**

The Jaeger stack adds **distributed tracing** for complete request flow visibility:

#### **Tracing Services:**
- **Jaeger UI** (Port 16686): Trace visualization and analysis
- **OTLP Collector**: Modern OpenTelemetry protocol for trace collection
- **Enhanced API**: Instrumented with OpenTelemetry tracing
- **Enhanced Simulator**: Traced traffic generation

#### **Distributed Tracing Features:**
```bash
# Start the Jaeger tracing stack
docker-compose -f docker-compose-jaeger.yml up -d

# Access Jaeger UI
open http://localhost:16686
```

#### **What You Get:**
- **Request Flow Visualization**: See complete request journey across services
- **Performance Analysis**: Identify bottlenecks and slow operations
- **Error Tracking**: Trace errors to their source with full context
- **Service Dependencies**: Understand how services interact
- **Business Context**: Custom attributes for business logic tracing

#### **Trace Examples:**
```
POST /api/players/login
├── player_login (custom span)
│   ├── SELECT battlearena (find player)
│   ├── UPDATE battlearena (update last_login)
│   └── INSERT battlearena (log system event)
└── HTTP Response
```

#### **Custom Business Attributes:**
- `player.id`: Player identifier
- `player.username`: Player username
- `match.type`: Match type (solo/team/tournament)
- `transaction.amount`: Transaction value
- `login.timestamp`: Login time

#### **Key Benefits:**
- **End-to-End Visibility**: Track requests from simulator to database
- **Performance Optimization**: Identify slow database queries and API calls
- **Error Debugging**: See exactly where and why errors occur
- **Business Intelligence**: Correlate technical performance with business metrics
- **Service Architecture**: Understand microservice interactions

---

## 🎯 Success Criteria

After working with this project, you should understand:

- ✅ How to implement Prometheus metrics in applications
- ✅ How to create effective Grafana dashboards
- ✅ How to design meaningful business and technical metrics
- ✅ How to troubleshoot monitoring systems
- ✅ How to scale observability for production environments
- ✅ How to use monitoring data for business insights
- ✅ How to analyze time-series data with PromQL
- ✅ How to optimize system performance using metrics

---

**🎉 Congratulations! You now have a solid foundation in observability and production monitoring!**

For questions or issues, check the troubleshooting section or explore the monitoring configurations - they're designed to be educational and production-ready.

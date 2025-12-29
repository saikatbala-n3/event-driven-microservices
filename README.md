# 🎯 Event-Driven Microservices

> A distributed e-commerce system built with event-driven architecture, RabbitMQ message broker, and full observability stack.

**Status**: 🔵 In Development
**Timeline**: Week 4-5 (Dec 24 - Jan 7, 2025)

---

## 🌟 Overview

This project demonstrates a production-ready event-driven microservices architecture with:
- 4 independent microservices (Order, Inventory, Payment, Notification)
- Asynchronous communication via RabbitMQ
- Distributed tracing with OpenTelemetry + Jaeger
- Full observability with Prometheus & Grafana
- Resilient patterns (retries, circuit breakers, sagas)

---

## 🏗️ Architecture

```
┌─────────────┐     ┌──────────────┐     ┌─────────────┐
│   Client    │────▶│Order Service │────▶│  RabbitMQ   │
└─────────────┘     └──────────────┘     └──────┬──────┘
                                                 │
                    ┌────────────────────────────┼────────────┐
                    │                            │            │
                    ↓                            ↓            ↓
            ┌───────────────┐          ┌─────────────┐  ┌─────────────┐
            │Inventory Svc  │          │Payment Svc  │  │Notification │
            └───────────────┘          └─────────────┘  └─────────────┘
                    │                            │            │
                    └────────────────────────────┴────────────┘
                                    Events Flow
```

---

## 🚀 Quick Start

### Prerequisites
- Docker & Docker Compose
- Python 3.11+
- Git

### Run All Services

```bash
# Clone and navigate
git clone <repo-url>
cd event-driven-microservices

# Start all services
docker compose up -d

# Check service health
docker compose ps
```

**Access Points:**
- Order Service: http://localhost:8001
- Inventory Service: http://localhost:8002
- Payment Service: http://localhost:8003
- Notification Service: http://localhost:8004
- RabbitMQ Management: http://localhost:15672 (guest/guest)
- Jaeger UI: http://localhost:16686
- Prometheus: http://localhost:9090
- Grafana: http://localhost:3000 (admin/admin)

---

## 📦 Microservices

### 1. Order Service (Port 8001)
Handles customer orders and orchestrates the order workflow.

**Endpoints:**
- `POST /api/v1/orders` - Create new order
- `GET /api/v1/orders/{id}` - Get order status
- `GET /api/v1/orders` - List all orders

**Events Published:**
- `OrderCreated`
- `OrderConfirmed`
- `OrderCancelled`

### 2. Inventory Service (Port 8002)
Manages product inventory and reservations.

**Events Consumed:**
- `OrderCreated` → Reserve inventory

**Events Published:**
- `InventoryReserved`
- `InventoryInsufficient`

### 3. Payment Service (Port 8003)
Processes payments for orders.

**Events Consumed:**
- `InventoryReserved` → Process payment

**Events Published:**
- `PaymentProcessed`
- `PaymentFailed`

### 4. Notification Service (Port 8004)
Sends notifications (email, SMS) to customers.

**Events Consumed:**
- `OrderCreated` → Send order confirmation
- `PaymentProcessed` → Send payment receipt
- `OrderCancelled` → Send cancellation notice

---

## 🔄 Event Flow

### Happy Path: Successful Order

1. **User** creates order via Order Service
2. **Order Service** publishes `OrderCreated` event
3. **Inventory Service** receives event, reserves inventory, publishes `InventoryReserved`
4. **Payment Service** receives event, processes payment, publishes `PaymentProcessed`
5. **Notification Service** receives events, sends confirmation emails
6. **Order Service** receives `PaymentProcessed`, marks order as confirmed

### Failure Path: Insufficient Inventory

1. **User** creates order via Order Service
2. **Order Service** publishes `OrderCreated` event
3. **Inventory Service** checks stock, publishes `InventoryInsufficient`
4. **Order Service** receives event, cancels order
5. **Notification Service** sends cancellation email

---

## 🛠️ Tech Stack

**Backend:**
- FastAPI - REST APIs
- RabbitMQ - Message broker
- PostgreSQL - Databases
- SQLAlchemy 2.0 - ORM
- aio-pika - Async RabbitMQ client

**Observability:**
- OpenTelemetry - Tracing instrumentation
- Jaeger - Distributed tracing UI
- Prometheus - Metrics
- Grafana - Dashboards

**Infrastructure:**
- Docker & Docker Compose
- Python 3.11

---

## 📊 Observability

### Distributed Tracing (Jaeger)
View complete request traces across all microservices:
```
http://localhost:16686
```

### Metrics (Prometheus)
Query service metrics:
```
http://localhost:9090
```

### Dashboards (Grafana)
Visualize system health:
```
http://localhost:3000
```

---

## 🧪 Testing

### Create Test Order

```bash
curl -X POST http://localhost:8001/api/v1/orders \
  -H "Content-Type: application/json" \
  -d '{
    "customer_id": "cust_123",
    "items": [
      {"product_id": "prod_001", "quantity": 2},
      {"product_id": "prod_002", "quantity": 1}
    ]
  }'
```

### Check RabbitMQ Queue

```bash
# Access RabbitMQ Management UI
open http://localhost:15672

# Login: guest/guest
# Navigate to Queues tab
```

### View Distributed Trace

```bash
# Create order (get order_id from response)
# Open Jaeger UI
open http://localhost:16686

# Search for traces by service: order-service
```

---

## 🏛️ Design Patterns

### Event-Driven Architecture
- Asynchronous communication between services
- Loose coupling via events
- Pub/Sub pattern with RabbitMQ

### Saga Pattern
- Distributed transaction management
- Compensating transactions on failure
- Choreography-based coordination

### Circuit Breaker
- Prevent cascading failures
- Fail fast on service unavailability
- Automatic recovery

### Retry with Exponential Backoff
- Transient failure handling
- Configurable retry policies
- Dead letter queue for permanent failures

---

## 📁 Project Structure

```
event-driven-microservices/
├── shared/                    # Shared libraries
│   ├── events/               # Event schemas
│   ├── messaging/            # RabbitMQ client
│   └── tracing/              # OpenTelemetry setup
├── services/
│   ├── order-service/        # Order management
│   ├── inventory-service/    # Inventory management
│   ├── payment-service/      # Payment processing
│   └── notification-service/ # Notifications
├── monitoring/
│   ├── prometheus/           # Prometheus config
│   └── grafana/              # Dashboards
├── docker-compose.yml        # Multi-service setup
└── README.md
```

---

## 🎓 Learning Outcomes

**Architectural Patterns:**
- Event-driven architecture
- Microservices decomposition
- Saga pattern for distributed transactions
- CQRS (Command Query Responsibility Segregation)

**Technical Skills:**
- RabbitMQ message broker
- Distributed tracing
- Service-to-service communication
- Event sourcing
- Async message processing

**DevOps:**
- Multi-service orchestration
- Service discovery
- Container networking
- Observability stack setup

---

## 🚀 Future Enhancements

- [ ] API Gateway (Kong/Traefik)
- [ ] Service mesh (Istio/Linkerd)
- [ ] Event sourcing with event store
- [ ] CQRS with read models
- [ ] GraphQL Federation
- [ ] Kubernetes deployment
- [ ] CI/CD pipeline

---

## 📝 License

MIT

## 👤 Author

**Saikat Bala**
- GitHub: [@saikatbala](https://github.com/saikatbala)
- LinkedIn: [saikat-bala](https://www.linkedin.com/in/saikat-bala-6b827299/)

---

*Project 03 of 9 - Backend Engineering Portfolio*

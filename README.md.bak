🛡️ Nerva Engine
================

**A High-Performance, Distributed Task Orchestration Framework**

Nerva is a lightweight, scalable "central nervous system" for distributed task execution. It decouples task triggering from execution, using a **Producer-Consumer** architecture to handle everything from simple pings to heavy computational workloads without blocking your API.

🚀 Core Capabilities
--------------------

*   **Decoupled Orchestration**: API instances handle requests while independent Workers handle the heavy lifting.
    
*   **Task Registry System**: Easily "plug in" new Python functions without modifying the core engine.
    
*   **Relational Persistence**: Full task lifecycle tracking (PENDING → WORKING → COMPLETED) in PostgreSQL.
    
*   **High Availability**: Nginx load balancing across multiple API replicas with a persistent Redis broker.
    
*   **Observability**: Real-time task monitoring via the Flower dashboard.
    
*   **CI/CD Ready**: Automated linting and container builds via GitHub Actions and GHCR.
    

🏗️ Architecture
----------------

The system follows a modern Distributed Microservices pattern:

*   **Gateway**: Nginx acting as a Reverse Proxy/Load Balancer (Port 80).
    
*   **API Tier**: Replicated FastAPI services managing the task lifecycle.
    
*   **Message Broker**: Redis 8 managing the asynchronous task queue.
    
*   **Worker Tier**: Celery Workers executing registered logic (e.g., system checks, data processing).
    
*   **Database**: PostgreSQL 18 storing permanent task records and results.
    
*   **Observability**: Flower (Port 5555) for real-time queue metrics.
    

🛠️ Quick Start
---------------

### 1\. Clone & Configure

```
git clone [https://github.com/gixorian/nerva-engine](https://github.com/gixorian/nerva-engine)
cd nerva-engine
cp .env.example .env
```

> **Note:** Update USER\_ID and GROUP\_ID in .env (find them by running id -u and id -g) to ensure proper volume permissions.

### 2\. Launch the Stack

```
docker compose up -d --build
```

### 3\. Scaling

Nerva is designed to scale. To handle higher task volumes, scale the worker tier horizontally:

```
docker compose up -d --scale worker=3
```

📊 Interaction & Monitoring
---------------------------

### Endpoints

*   **Health Check**: GET /health (Service status)
    
*   **Queue Task**: POST /test-worker?seconds=10 (Triggers a registered debug task)
    
*   **Task Status**: GET /status/{task\_id} (Check progress and results)
    
*   **History**: GET /history (View recent engine activity)
    

### Dashboards

*   **Interactive API Docs**: [http://localhost/docs](http://localhost/docs)
    
*   **Task Monitor (Flower)**: [http://localhost:5555](http://localhost:5555)
    

🔌 The Registry System
----------------------

Nerva treats logic as plugins. To add a new capability, simply define a function and register it in nerva/registry.py:

```
def my_custom_logic(payload):
  # Your code here
  return {"status": "success"}

register_task("MY_NEW_TASK", my_custom_logic)
```

💾 Persistence & Cleanup
------------------------

Nerva uses named volumes for Redis and PostgreSQL. To wipe the engine state and start fresh:

```   
docker compose down -v
```

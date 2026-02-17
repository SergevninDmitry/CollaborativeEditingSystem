# Collaborative Editing System

A microservice-based collaborative document editing platform built with **FastAPI**, **PostgreSQL**, and **Docker**.

The system allows users to:

- register and authenticate
- create and manage documents
- collaborate via document sharing
- maintain document version history
- revert and compare document versions

The project demonstrates a production-style backend architecture using service separation, API Gateway, and async communication between services.

---

## 🏗 Architecture Overview

The system is built using a microservice architecture with a centralized API Gateway:

```
                +----------------------+
                |      Streamlit UI    |
                +----------+-----------+
                           |
                           v
                +----------------------+
                |      API Gateway     |
                +----------+-----------+
                           |
        +------------------+------------------+------------------+------------------+
        |                  |                  |                  |
        v                  v                  v                  v
+---------------+  +---------------+  +---------------+  +---------------+
| Auth Service  |  | User Service  |  | Document Svc  |  |  Version Svc  |
+-------+-------+  +-------+-------+  +-------+-------+  +-------+-------+
        \               |                  |               /
         \              |                  |              /
          +------------------------------------------------+
                              |
                              v
                     +------------------+
                     |    PostgreSQL    |
                     +------------------+
```

### Services

| Service | Responsibility                                                      |
|---|---------------------------------------------------------------------|
| **API Gateway** | Single entry point, authentication forwarding and  request proxying |
| **Auth Service** | Authentication & JWT issuing                                        |
| **User Service** | User management                                                     |
| **Document Service** | Document ownership & sharing                                        |
| **Version Service** | Document versioning and diff/revert logic                           |
| **PostgreSQL** | Shared database                                                     |
| **Streamlit** | Web interface                                                       |

---

## ⚙️ Tech Stack

- **Backend**:
  - FastAPI
  - Python 3.11
  - SQLAlchemy (Async)

- **Infrastructure**:
  - Docker & Docker Compose
  - PostgreSQL

- **Communication**:
  - httpx (async HTTP clients)
  - JWT Authentication

- **Frontend**:
  - Streamlit

---

## 📁 Project Structure
```
services/
│
├── api_gateway/
├── auth_service/
├── user_service/
├── document_service/
└── version_service/

frontend/
shared/
docker-compose.yml
.env.example
```

### Layered service structure

Each service follows a consistent internal architecture:
```
service/
├── api/ # FastAPI routers
├── application/ # business logic (services)
├── infrastructure/ # DB models, integrations
├── dependencies.py
├── config.py
└── main.py

```
Each service is independently deployable and communicates via HTTP APIs.

---

## 🚀 Quick Start

### 1️⃣ Clone repository

```bash
git clone <repo-url>
cd CollaborativeEditingSystem
```
### 2️⃣ Create environment file
```bash
cp .env.example .env
```

### 3️⃣ To run containers in background
```bash
docker compose up --build
```

### 4️⃣ Open applications
| Service | URL |
|---|---|
| API Gateway | http://localhost:8080/docs |
| Streamlit UI | http://localhost:8501 |

## 🔐 Authentication Flow

1. User registers via User Service
2. Login request goes through API Gateway
3. Auth Service validates credentials
4. A JWT access token is issued.
5. The token must be included in the `Authorization: Bearer <token>` header for protected endpoints.


## 📄 Document Workflow

- Users create documents
- Documents belong to an owner
- Documents can be shared with other users
- Every modification creates a version snapshot
- Versions support:
  - history viewing
  - revert
  - diff comparison

## 🔁 Versioning Logic

- The Version Service provides:
  - optimistic concurrency control
  - version history
  - unified diff generation
  - revert-to-version functionality


## 📈 Future Improvements

- WebSocket real-time editing
- Operational Transform / CRDT
- Redis caching layer
- Background workers
- Kubernetes deployment

## 🎯 Educational Goals

This project demonstrates:
- microservice architecture design
- async Python backend development
- API Gateway pattern
- dependency injection in FastAPI
- service isolation
- production-style Docker setup

## 👤 Author

**Sergevnin Dmitrii**  
GitHub: [@SergevninDmitry](https://github.com/SergevninDmitry)

# Aingles Backend

Backend for the Aingles application - Complete REST API with JWT authentication, AI integration, chat system, and educational content management.

## 📋 Table of Contents

- [Overview](#-overview)
- [Features](#-features)
- [Architecture](#-architecture)
- [Technologies](#️-technologies)
- [Installation](#-installation)
- [Configuration](#️-configuration)
- [Usage](#-usage)
- [API Documentation](#-api-documentation)
- [Project Structure](#-project-structure)
- [Deployment](#-deployment)
- [Contributing](#-contributing)

## 🎯 Overview

Aingles Backend is a REST API developed with FastAPI that provides complete features for English learning, including:

- Robust authentication and authorization system with JWT
- AI-powered chat for conversational practice
- Flashcard system (Anki) for memorization
- Automatic aggregation of technology articles
- User and profile management

## ✨ Features

### Authentication & Authorization
- ✅ User registration and login
- ✅ JWT authentication with access and refresh tokens
- ✅ Token blacklist for secure logout
- ✅ Email verification
- ✅ Permission management (AI access)

### AI Chat
- 🤖 Real-time conversations with language models
- 💬 Persistent conversation history
- 📝 Multiple chat sessions per user
- 🔒 Permission-based access control

### Card System
- 📇 Flashcard creation and management
- 🔄 Synchronization with mobile/web application
- 📊 Organization by decks

### Content Aggregation
- 📰 Automatic article import (TechCrunch, TabNews)
- ⏰ Task scheduling with APScheduler
- 🔍 Search and filtering system

## 🛠️ Technologies

### Core
- **[FastAPI](https://fastapi.tiangolo.com/)** - Modern and fast web framework
- **[SQLModel](https://sqlmodel.tiangolo.com/)** - ORM based on SQLAlchemy and Pydantic
- **[SQLite](https://www.sqlite.org/)** - Relational database
- **[Alembic](https://alembic.sqlalchemy.org/)** - Database migrations

### Authentication & Security
- **[python-jose](https://python-jose.readthedocs.io/)** - JWT creation and validation
- **[passlib](https://passlib.readthedocs.io/)** - Password hashing with bcrypt
- **[cryptography](https://cryptography.io/)** - Cryptographic operations

### Integrations
- **[OpenAI](https://platform.openai.com/)** - Language model API
- **[Twilio](https://www.twilio.com/)** - SMS and WhatsApp messaging
- **[BeautifulSoup4](https://www.crummy.com/software/BeautifulSoup/)** - Web scraping

### Scheduling & Background
- **[APScheduler](https://apscheduler.readthedocs.io/)** - Task scheduling

### Environment & Deployment
- **[Docker](https://www.docker.com/)** - Containerization
- **[Nginx](https://nginx.org/)** - Web server and reverse proxy
- **[Uvicorn](https://www.uvicorn.org/)** - ASGI server

## 📦 Installation

### Prerequisites
- Python 3.10+
- pip
- Docker and Docker Compose (optional)

### Local Installation

1. Clone the repository:
```bash
git clone https://github.com/PedroHenriqueDevBR/Aingles-backend.git
cd Aingles-backend
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate  # Windows
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

### Docker Installation

```bash
docker-compose up -d
```

## ⚙️ Configuration

### Environment Variables

1. Copy the example file:
```bash
cp .env.example .env
```

2. Configure the required variables:

### Generate Secret Keys

```bash
# Generate JWT_SECRET
python -c "import secrets; print(secrets.token_urlsafe(32))"

# Generate SECRET_KEY
python -c "import secrets; print(secrets.token_hex(32))"
```

### Database Migrations

```bash
# Create migration
alembic revision --autogenerate -m "migration description"

# Apply migrations
alembic upgrade head

# Revert last migration
alembic downgrade -1
```

## 🚀 Usage

### Development

```bash
# With auto-reload
fastapi dev main.py

# Local production
fastapi run main.py
```

### Production with Docker

```bash
# Start services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

### Access the Application

- **API**: http://localhost:8000
- **Swagger UI**: http://localhost:8000/docs (only in DEBUG mode)
- **ReDoc**: http://localhost:8000/redoc (only in DEBUG mode)

## 🐳 Deployment

### Docker Compose (Recommended)

1. Configure environment variables in `.env`
2. Run:
```bash
docker-compose up -d
```

### Manual Deployment

1. Configure the server (Ubuntu/Debian):
```bash
# Install Python and dependencies
sudo apt update
sudo apt install python3.10 python3-pip nginx

# Clone repository
git clone https://github.com/PedroHenriqueDevBR/Aingles-backend.git
cd Aingles-backend

# Install dependencies
pip install -r requirements.txt

# Configure environment variables
cp .env.example .env
nano .env
```

2. Configure systemd service:
```bash
sudo nano /etc/systemd/system/aingles.service
```

```ini
[Unit]
Description=Aingles FastAPI Application
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/path/to/Aingles-backend
Environment="PATH=/path/to/venv/bin"
ExecStart=/path/to/venv/bin/uvicorn main:app --host 0.0.0.0 --port 8000

[Install]
WantedBy=multi-user.target
```

3. Start service:
```bash
sudo systemctl daemon-reload
sudo systemctl enable aingles
sudo systemctl start aingles
```

## 🤝 Contributing

Contributions are welcome! To contribute:

1. Fork the project
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

### Contribution Guidelines

- Follow the existing code style
- Update documentation when necessary
- Use semantic commits (feat, fix, docs, etc.)

## 👤 Author

**Pedro Henrique**
- GitHub: [@PedroHenriqueDevBR](https://github.com/PedroHenriqueDevBR)

**Note**: This is an actively developed project. Features and documentation may change.

# Gemini Backend Clone

A sophisticated backend system that replicates Gemini-style functionality with OTP-based authentication, user-specific chatrooms, AI-powered conversations via Google Gemini API, and subscription management through Stripe integration.

## 🚀 Features

- **OTP-Based Authentication**: Secure mobile number-based login system with JWT tokens
- **Chatroom Management**: Create and manage multiple AI conversation rooms
- **Google Gemini Integration**: AI-powered conversations with context awareness
- **Subscription System**: Stripe-powered Pro subscriptions with usage limits
- **Async Processing**: Redis-based message queuing for optimal performance
- **Caching Strategy**: Intelligent caching for improved response times
- **Rate Limiting**: Tier-based usage restrictions
- **Cloud Ready**: Multiple deployment options with Docker support

## 📋 Table of Contents

- [Architecture Overview](#architecture-overview)
- [Technology Stack](#technology-stack)
- [API Endpoints](#api-endpoints)
- [Installation & Setup](#installation--setup)
- [Local Development](#local-development)
- [Cloud Deployment](#cloud-deployment)
- [Environment Variables](#environment-variables)
- [Database Schema](#database-schema)
- [Testing](#testing)
- [Performance Considerations](#performance-considerations)
- [Security Features](#security-features)
- [Contributing](#contributing)

## 🏗️ Architecture Overview

The Gemini Backend Clone follows a modern microservices-inspired architecture with clear separation of concerns:

### Core Components

**FastAPI Application**: High-performance async web framework serving RESTful APIs with automatic documentation generation and built-in data validation.

**PostgreSQL Database**: ACID-compliant relational database storing user data, chatrooms, messages, and subscription information with optimized indexing for performance.

**Redis Cache & Queue**: Multi-purpose in-memory data store handling both caching operations and asynchronous message queuing for Gemini API calls.

**Celery Workers**: Distributed task queue processing AI conversations asynchronously to maintain responsive user experience.

**External Integrations**: Seamless integration with Google Gemini API for AI conversations and Stripe API for payment processing.

### Data Flow Architecture

The system implements a sophisticated data flow pattern that ensures optimal performance and user experience. When a user sends a message, the system immediately stores the user message in the database and returns a success response, while simultaneously queuing the Gemini API call for background processing. This approach prevents users from experiencing delays due to external API response times.

The caching layer strategically stores frequently accessed data such as user chatroom lists, which are accessed during dashboard loads but change infrequently. The cache invalidation strategy ensures data consistency while maximizing performance benefits.

### Security Architecture

Authentication follows industry best practices with JWT tokens providing stateless authentication across distributed services. OTP verification adds an additional security layer, while rate limiting prevents abuse and ensures fair resource allocation across subscription tiers.

## 🛠️ Technology Stack

| Component | Technology | Purpose |
|-----------|------------|---------|
| **Backend Framework** | FastAPI | High-performance async API development |
| **Database** | PostgreSQL | Reliable data persistence with ACID compliance |
| **Cache & Queue** | Redis | In-memory caching and message queuing |
| **Task Queue** | Celery | Asynchronous background task processing |
| **Authentication** | JWT | Stateless token-based authentication |
| **AI Integration** | Google Gemini API | Advanced AI conversation capabilities |
| **Payments** | Stripe | Secure subscription and payment processing |
| **Containerization** | Docker | Consistent deployment across environments |
| **Database Migrations** | Alembic | Version-controlled database schema management |

## 📡 API Endpoints

### Authentication Endpoints

| Endpoint | Method | Auth Required | Description |
|----------|--------|---------------|-------------|
| `/auth/signup` | POST | ❌ | Register new user with mobile number |
| `/auth/send-otp` | POST | ❌ | Send OTP to user's mobile number |
| `/auth/verify-otp` | POST | ❌ | Verify OTP and return JWT token |
| `/auth/forgot-password` | POST | ❌ | Send OTP for password reset |
| `/auth/change-password` | POST | ✅ | Change password while logged in |

### User Management

| Endpoint | Method | Auth Required | Description |
|----------|--------|---------------|-------------|
| `/user/me` | GET | ✅ | Get current user details |

### Chatroom Operations

| Endpoint | Method | Auth Required | Description |
|----------|--------|---------------|-------------|
| `/chatroom` | POST | ✅ | Create new chatroom |
| `/chatroom` | GET | ✅ | List user chatrooms (cached) |
| `/chatroom/{id}` | GET | ✅ | Get chatroom details with messages |
| `/chatroom/{id}/message` | POST | ✅ | Send message and get AI response |

### Subscription Management

| Endpoint | Method | Auth Required | Description |
|----------|--------|---------------|-------------|
| `/subscribe/pro` | POST | ✅ | Initiate Pro subscription via Stripe |
| `/subscription/status` | GET | ✅ | Check current subscription tier |
| `/webhook/stripe` | POST | ❌ (Stripe only) | Handle Stripe webhook events |

### System Endpoints

| Endpoint | Method | Auth Required | Description |
|----------|--------|---------------|-------------|
| `/` | GET | ❌ | Root endpoint with API information |
| `/health` | GET | ❌ | Health check for monitoring |
| `/docs` | GET | ❌ | Interactive API documentation |

## 🔧 Installation & Setup

### Prerequisites

Before setting up the Gemini Backend Clone, ensure you have the following installed on your system:

- **Python 3.11+**: The application requires Python 3.11 or higher for optimal performance and compatibility with all dependencies.
- **PostgreSQL 13+**: Database server for persistent data storage.
- **Redis 6+**: In-memory data store for caching and message queuing.
- **Docker & Docker Compose** (optional): For containerized development and deployment.

### Quick Start with Docker

The fastest way to get the application running is using Docker Compose, which handles all service dependencies automatically:

```bash
# Clone the repository
git clone <repository-url>
cd gemini-backend

# Copy environment configuration
cp .env.example .env

# Update .env with your API keys (see Environment Variables section)

# Start all services
docker-compose up -d

# Run database migrations
docker-compose exec app alembic upgrade head

# View logs
docker-compose logs -f app
```

### Manual Installation

For development or custom deployment scenarios, you can set up the application manually:

```bash
# Clone and navigate to project
git clone <repository-url>
cd gemini-backend

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your configuration

# Start PostgreSQL and Redis services
# (Installation varies by operating system)

# Run database migrations
alembic upgrade head

# Start the application
python -m uvicorn app.main:app --reload

# In separate terminals, start Celery worker and beat
celery -A app.services.celery_app worker --loglevel=info
celery -A app.services.celery_app beat --loglevel=info
```



## 💻 Local Development

### Development Workflow

The local development environment is designed to provide a seamless experience with hot reloading, comprehensive logging, and easy debugging capabilities. The development setup includes automatic code reloading, detailed error messages, and access to interactive API documentation.

### Setting Up Development Environment

Use the provided setup script for automated local environment configuration:

```bash
# Make setup script executable and run
chmod +x scripts/setup-local.sh
./scripts/setup-local.sh
```

This script performs the following operations:
- Validates Python version compatibility
- Creates and activates a virtual environment
- Installs all required dependencies
- Copies environment configuration template
- Starts PostgreSQL and Redis services via Docker
- Runs initial database migrations

### Development Server

Start the development server with hot reloading enabled:

```bash
# Activate virtual environment
source venv/bin/activate

# Start FastAPI development server
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Start Celery worker for background tasks
celery -A app.services.celery_app worker --loglevel=info

# Start Celery beat for scheduled tasks (optional)
celery -A app.services.celery_app beat --loglevel=info
```

### API Documentation

FastAPI automatically generates interactive API documentation accessible at:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

These interfaces provide comprehensive API exploration capabilities, including request/response schemas, authentication testing, and live API calls.

### Database Management

The application uses Alembic for database migrations, providing version control for database schema changes:

```bash
# Create new migration
alembic revision --autogenerate -m "Description of changes"

# Apply migrations
alembic upgrade head

# Rollback to previous version
alembic downgrade -1

# View migration history
alembic history
```

### Testing with Postman

Import the provided Postman collection (`postman_collection.json`) for comprehensive API testing:

1. Import the collection into Postman
2. Set the `base_url` variable to your local server (http://localhost:8000)
3. Run the authentication flow to obtain access tokens
4. Test all endpoints with proper authentication

The collection includes automated token management and variable extraction for seamless testing workflows.

## ☁️ Cloud Deployment

The Gemini Backend Clone supports deployment across multiple cloud platforms with platform-specific configurations and deployment scripts.

### Railway Deployment

Railway provides the simplest deployment experience with automatic environment detection and zero-configuration deployments:

```bash
# Install Railway CLI
npm install -g @railway/cli

# Run deployment script
chmod +x scripts/deploy-railway.sh
./scripts/deploy-railway.sh
```

Railway automatically provisions PostgreSQL and Redis databases, configures environment variables, and provides a public URL for your application.

### Render Deployment

Render offers a robust platform with Blueprint-based infrastructure as code:

```bash
# Follow the instructions in the deployment script
chmod +x scripts/deploy-render.sh
./scripts/deploy-render.sh
```

The `render.yaml` configuration file defines the complete infrastructure including web service, PostgreSQL database, and Redis instance.

### Fly.io Deployment

Fly.io provides global edge deployment with excellent performance characteristics:

```bash
# Install Fly CLI and deploy
chmod +x scripts/deploy-fly.sh
./scripts/deploy-fly.sh
```

The deployment includes automatic database provisioning, secret management, and global distribution capabilities.

### AWS ECS Deployment

For enterprise-grade deployments, AWS ECS provides scalable container orchestration:

```bash
# Configure AWS CLI and run deployment
chmod +x scripts/deploy-aws.sh
./scripts/deploy-aws.sh
```

This deployment creates an ECS cluster, ECR repository, task definitions, and Application Load Balancer for production-ready infrastructure.

### Docker Deployment

For custom cloud deployments or on-premises installations:

```bash
# Build Docker image
docker build -t gemini-backend .

# Run with environment variables
docker run -d \
  -p 8000:8000 \
  -e DATABASE_URL="your-database-url" \
  -e REDIS_URL="your-redis-url" \
  -e GEMINI_API_KEY="your-api-key" \
  gemini-backend
```

## 🔐 Environment Variables

The application requires several environment variables for proper operation. Copy `.env.example` to `.env` and configure the following:

### Database Configuration

```env
DATABASE_URL=postgresql://username:password@localhost:5432/gemini_backend
```

The database URL should point to a PostgreSQL instance with appropriate credentials and database name.

### Redis Configuration

```env
REDIS_URL=redis://localhost:6379/0
```

Redis URL for caching and message queue operations. Use database 0 for default configuration.

### JWT Authentication

```env
SECRET_KEY=your-super-secret-jwt-key-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
```

Generate a secure secret key using: `openssl rand -hex 32`

### Google Gemini API

```env
GEMINI_API_KEY=your-gemini-api-key-here
```

Obtain your API key from the Google AI Studio console.

### Stripe Configuration

```env
STRIPE_SECRET_KEY=sk_test_your-stripe-secret-key
STRIPE_PUBLISHABLE_KEY=pk_test_your-stripe-publishable-key
STRIPE_WEBHOOK_SECRET=whsec_your-webhook-secret
STRIPE_PRICE_ID=price_your-pro-subscription-price-id
```

Configure Stripe keys from your Stripe dashboard. Use test keys for development and live keys for production.

### Application Settings

```env
DEBUG=True
HOST=0.0.0.0
PORT=8000
BASIC_DAILY_LIMIT=5
PRO_DAILY_LIMIT=1000
```

Adjust rate limits and debug settings based on your requirements.

## 🗄️ Database Schema

The application uses a well-normalized database schema optimized for performance and data integrity.

### Users Table

The users table serves as the central entity for authentication and subscription management:

```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    mobile_number VARCHAR(15) UNIQUE NOT NULL,
    name VARCHAR(100),
    email VARCHAR(255),
    password_hash VARCHAR(255),
    subscription_tier VARCHAR(20) DEFAULT 'basic',
    daily_message_count INTEGER DEFAULT 0,
    last_message_date DATE,
    stripe_customer_id VARCHAR(255),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### OTP Management

The OTP table handles temporary authentication codes with automatic expiration:

```sql
CREATE TABLE otps (
    id SERIAL PRIMARY KEY,
    mobile_number VARCHAR(15) NOT NULL,
    otp_code VARCHAR(6) NOT NULL,
    purpose VARCHAR(20) NOT NULL,
    expires_at TIMESTAMP NOT NULL,
    is_used BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Chatroom Structure

Chatrooms provide isolated conversation contexts for users:

```sql
CREATE TABLE chatrooms (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Message Storage

Messages store both user inputs and AI responses with conversation context:

```sql
CREATE TABLE messages (
    id SERIAL PRIMARY KEY,
    chatroom_id INTEGER REFERENCES chatrooms(id) ON DELETE CASCADE,
    content TEXT NOT NULL,
    role VARCHAR(20) NOT NULL,
    gemini_response_id VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Subscription Tracking

The subscriptions table manages Stripe integration and billing cycles:

```sql
CREATE TABLE subscriptions (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    stripe_subscription_id VARCHAR(255) UNIQUE,
    status VARCHAR(20) NOT NULL,
    current_period_start TIMESTAMP,
    current_period_end TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Database Indexes

The schema includes strategic indexes for optimal query performance:

```sql
-- User lookup optimization
CREATE INDEX idx_users_mobile_number ON users(mobile_number);
CREATE INDEX idx_users_stripe_customer ON users(stripe_customer_id);

-- OTP verification optimization
CREATE INDEX idx_otps_mobile_purpose ON otps(mobile_number, purpose, is_used);

-- Chatroom queries optimization
CREATE INDEX idx_chatrooms_user_id ON chatrooms(user_id);
CREATE INDEX idx_chatrooms_updated_at ON chatrooms(updated_at DESC);

-- Message retrieval optimization
CREATE INDEX idx_messages_chatroom_id ON messages(chatroom_id);
CREATE INDEX idx_messages_created_at ON messages(created_at);

-- Subscription status queries
CREATE INDEX idx_subscriptions_user_status ON subscriptions(user_id, status);
```


## 🧪 Testing

The application includes comprehensive testing strategies covering unit tests, integration tests, and API endpoint validation.

### Test Structure

The testing framework uses pytest with async support for comprehensive coverage:

```bash
# Install test dependencies (included in requirements.txt)
pip install pytest pytest-asyncio httpx

# Run all tests
pytest

# Run with coverage report
pytest --cov=app --cov-report=html

# Run specific test categories
pytest tests/test_auth.py
pytest tests/test_chatrooms.py
pytest tests/test_subscriptions.py
```

### API Testing with Postman

The provided Postman collection offers comprehensive API testing capabilities:

1. **Authentication Flow Testing**: Complete OTP-based login workflow with automatic token management
2. **Chatroom Operations**: Create, list, and message testing with proper authorization
3. **Subscription Management**: Pro subscription initiation and status checking
4. **Error Handling**: Invalid input validation and error response verification

### Load Testing

For performance validation, use tools like Apache Bench or Locust:

```bash
# Simple load test with Apache Bench
ab -n 1000 -c 10 http://localhost:8000/health

# Advanced load testing with Locust
pip install locust
locust -f tests/load_test.py --host=http://localhost:8000
```

### Database Testing

Database operations are tested with transaction rollbacks to ensure test isolation:

```python
# Example test structure
@pytest.fixture
def db_session():
    connection = engine.connect()
    transaction = connection.begin()
    session = SessionLocal(bind=connection)
    yield session
    session.close()
    transaction.rollback()
    connection.close()
```

## ⚡ Performance Considerations

The Gemini Backend Clone implements several performance optimization strategies to ensure scalability and responsiveness.

### Caching Strategy

The application employs a multi-layered caching approach for optimal performance:

**Chatroom List Caching**: User chatroom lists are cached with a 10-minute TTL since chatrooms are frequently accessed but rarely modified. This significantly reduces database load during dashboard operations.

**User Session Caching**: User subscription status and daily limits are cached for 24 hours to minimize database queries during rate limiting checks.

**Cache Invalidation**: Strategic cache invalidation ensures data consistency while maximizing performance benefits. Chatroom cache is invalidated on creation or deletion, while user session cache is invalidated on subscription changes.

### Asynchronous Processing

The system implements asynchronous processing for external API calls to maintain responsive user experience:

**Message Queue Architecture**: User messages are immediately stored and acknowledged while Gemini API calls are processed in the background via Celery workers.

**Task Status Tracking**: Background tasks include status tracking and error handling to ensure reliable message processing.

**Connection Pooling**: Database and Redis connections use pooling to optimize resource utilization and reduce connection overhead.

### Database Optimization

Several database optimization techniques ensure efficient data operations:

**Strategic Indexing**: Indexes are carefully placed on frequently queried columns including user lookups, chatroom filtering, and message retrieval.

**Query Optimization**: Complex queries use joins and aggregations efficiently, with pagination for large result sets.

**Connection Management**: Database connections use pooling with pre-ping validation and automatic reconnection handling.

### Rate Limiting Implementation

The rate limiting system balances user experience with resource protection:

**Tier-Based Limits**: Basic users are limited to 5 messages per day while Pro users enjoy 1000 messages, encouraging subscription upgrades.

**Daily Reset Logic**: Message counts reset automatically at midnight, with efficient date-based tracking.

**Graceful Degradation**: Rate limit exceeded responses include upgrade suggestions and clear messaging.

### Monitoring and Metrics

Production deployments should include comprehensive monitoring:

**Health Checks**: The `/health` endpoint provides service status for load balancer health checks.

**Logging Strategy**: Structured logging with correlation IDs enables effective debugging and monitoring.

**Performance Metrics**: Key metrics include response times, error rates, cache hit ratios, and queue processing times.

## 🔒 Security Features

The application implements comprehensive security measures following industry best practices.

### Authentication Security

**JWT Token Management**: Tokens use secure algorithms (HS256) with configurable expiration times and proper secret key management.

**OTP Security**: One-time passwords expire after 10 minutes and are marked as used after verification to prevent replay attacks.

**Password Security**: User passwords are hashed using bcrypt with appropriate salt rounds for secure storage.

### API Security

**Input Validation**: All API inputs are validated using Pydantic schemas with type checking and constraint validation.

**SQL Injection Prevention**: SQLAlchemy ORM with parameterized queries prevents SQL injection attacks.

**CORS Configuration**: Cross-origin requests are properly configured for frontend integration while maintaining security.

### Rate Limiting Security

**Abuse Prevention**: Rate limiting prevents API abuse and ensures fair resource allocation across users.

**DDoS Protection**: Request rate limiting provides basic protection against denial-of-service attacks.

**Resource Protection**: Background task queuing prevents resource exhaustion from external API calls.

### Data Protection

**Sensitive Data Handling**: API keys and secrets are managed through environment variables and never stored in code.

**Database Security**: Database connections use encrypted connections and proper credential management.

**Error Handling**: Error responses avoid exposing sensitive system information while providing useful debugging information in development mode.

## 🚀 Queue System Explanation

The asynchronous processing system uses Redis and Celery for reliable background task execution.

### Architecture Overview

The queue system implements a producer-consumer pattern where the FastAPI application produces tasks and Celery workers consume them:

**Task Producer**: FastAPI endpoints queue Gemini API calls immediately after storing user messages.

**Task Consumer**: Celery workers process queued tasks asynchronously, calling external APIs and storing responses.

**Result Backend**: Redis stores task results and status information for monitoring and debugging.

### Task Processing Flow

When a user sends a message, the following sequence occurs:

1. **Immediate Response**: User message is stored in the database and success response returned immediately
2. **Task Queuing**: Gemini API call is queued with message context and conversation history
3. **Background Processing**: Celery worker picks up the task and calls Gemini API with proper error handling
4. **Result Storage**: AI response is stored in the database with proper association to the conversation
5. **Status Updates**: Task status is updated throughout the process for monitoring and debugging

### Error Handling and Retry Logic

The queue system includes robust error handling:

**Automatic Retries**: Failed tasks are automatically retried with exponential backoff to handle temporary API failures.

**Dead Letter Queue**: Tasks that fail repeatedly are moved to a dead letter queue for manual investigation.

**Graceful Degradation**: API failures result in helpful error messages stored as AI responses rather than silent failures.

### Monitoring and Scaling

The queue system provides monitoring capabilities and horizontal scaling options:

**Task Monitoring**: Celery provides built-in monitoring tools for task status, queue lengths, and worker health.

**Horizontal Scaling**: Additional Celery workers can be added to handle increased load without code changes.

**Resource Management**: Task timeouts and memory limits prevent runaway processes from affecting system stability.

## 🔧 Gemini API Integration Overview

The Google Gemini API integration provides advanced AI conversation capabilities with context awareness and error handling.

### Integration Architecture

The Gemini service implements a clean abstraction layer that handles API communication, context management, and error recovery:

**Service Layer**: The `GeminiService` class encapsulates all Gemini API interactions with proper configuration and error handling.

**Context Management**: Conversation history is maintained and passed to the API for contextually aware responses.

**Async Processing**: API calls are processed asynchronously to prevent blocking user interactions.

### Conversation Context

The system maintains conversation context for natural, flowing conversations:

**History Management**: The last 10 messages from each chatroom are included as context for new API calls.

**Context Formatting**: Messages are properly formatted with role indicators (user/assistant) for optimal API performance.

**Memory Efficiency**: Context is limited to prevent excessive token usage while maintaining conversation quality.

### Error Handling and Fallbacks

Robust error handling ensures reliable service even during API issues:

**API Failure Recovery**: Network errors and API failures result in helpful error messages rather than silent failures.

**Rate Limit Handling**: API rate limits are respected with appropriate backoff strategies.

**Fallback Responses**: When the API is unavailable, users receive informative messages explaining the situation.

### Performance Optimization

Several optimizations ensure efficient API usage:

**Request Optimization**: API requests include only necessary context to minimize token usage and response times.

**Caching Considerations**: While responses aren't cached (to maintain conversation freshness), API configuration is cached for performance.

**Monitoring Integration**: API usage metrics are tracked for billing and performance monitoring.

## 🎯 Design Decisions and Assumptions

Several key design decisions shape the architecture and implementation of the Gemini Backend Clone.

### Authentication Design

**OTP-Only Authentication**: The system uses mobile number and OTP for primary authentication, reflecting modern mobile-first authentication patterns. This decision simplifies user onboarding while maintaining security.

**JWT Token Strategy**: Stateless JWT tokens enable horizontal scaling and reduce database load for authentication checks. Token expiration is set to 1 hour to balance security and user experience.

**Password Optional**: Passwords are optional during signup, allowing users to rely solely on OTP authentication if preferred. This reduces friction while maintaining security options.

### Database Design Decisions

**PostgreSQL Choice**: PostgreSQL was selected for its ACID compliance, excellent performance with complex queries, and robust JSON support for future extensibility.

**Normalized Schema**: The database uses a normalized design to ensure data integrity and efficient storage, with strategic denormalization only where performance benefits are significant.

**Soft Deletes**: User accounts use soft deletion (is_active flag) to maintain data integrity and enable account recovery if needed.

### Caching Strategy Decisions

**Redis for Multiple Purposes**: Redis serves both caching and message queue functions to reduce infrastructure complexity while maintaining performance.

**Selective Caching**: Only frequently accessed, slowly changing data is cached to maximize performance benefits while minimizing cache management complexity.

**TTL Strategy**: Cache TTLs are set based on data change frequency and consistency requirements, with shorter TTLs for critical data.

### API Design Philosophy

**RESTful Design**: The API follows REST principles for predictability and ease of integration, with clear resource-based URLs and appropriate HTTP methods.

**Async-First**: All potentially slow operations (external API calls, complex database queries) are designed with asynchronous processing to maintain responsiveness.

**Error Consistency**: All API responses follow consistent error formatting to simplify client-side error handling.

### Subscription Model Assumptions

**Two-Tier System**: The basic/pro tier system is designed for simplicity while providing clear upgrade incentives through usage limits.

**Stripe Integration**: Stripe was chosen for its comprehensive API, webhook system, and global payment support.

**Usage-Based Limits**: Daily message limits encourage engagement while providing clear value differentiation between tiers.

## 🤝 Contributing

Contributions to the Gemini Backend Clone are welcome and encouraged. Please follow these guidelines for effective collaboration.

### Development Setup

1. Fork the repository and create a feature branch
2. Set up the local development environment using the provided scripts
3. Make your changes with appropriate tests
4. Ensure all tests pass and code follows the established patterns
5. Submit a pull request with a clear description of changes

### Code Standards

- Follow PEP 8 style guidelines for Python code
- Use type hints for all function parameters and return values
- Include docstrings for all public functions and classes
- Maintain test coverage above 80% for new code

### Commit Guidelines

- Use clear, descriptive commit messages
- Include issue numbers in commit messages when applicable
- Keep commits focused on single changes or features
- Squash commits before merging to maintain clean history

---

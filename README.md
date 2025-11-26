# Township 311 Request Management System

A comprehensive web application for managing citizen service requests in townships and municipalities. Built with FastAPI (Python) backend and React frontend, featuring secure authentication, file uploads with virus scanning, real-time status tracking, and role-based access control.

## Features

### Core Functionality
- **Citizen Portal**: Submit service requests, track status, upload attachments
- **Staff Dashboard**: Review, assign, and manage requests
- **Admin Controls**: User management and system configuration
- **Real-time Updates**: Live status tracking and notifications
- **File Management**: Secure file uploads with ClamAV virus scanning
- **Comments System**: Internal and public comments on requests

### Security Features
- JWT-based authentication
- Role-based access control (Citizen, Staff, Admin)
- File upload validation and virus scanning
- CORS protection
- Input validation and sanitization
- Secure password hashing with Argon2

### Technical Features
- **Backend**: FastAPI with async SQLAlchemy
- **Frontend**: React with Tailwind CSS
- **Database**: PostgreSQL with PostGIS support
- **File Storage**: Local file system with virus scanning
- **Caching**: Redis for session management
- **Containerization**: Docker and Docker Compose

## Quick Start

### Prerequisites
- Docker and Docker Compose
- Node.js 20+ (for local development)
- Python 3.11+ (for local development)

### Using Docker Compose (Recommended)

1. **Clone and setup**:
   ```bash
   git clone <repository-url>
   cd township-311-system
   cp .env.example .env
   ```

2. **Configure environment**:
   Edit `.env` file with your settings:
   ```bash
   # Update passwords and secret keys
   POSTGRES_PASSWORD=your_secure_password
   SECRET_KEY=your_super_secret_key
   ```

3. **Start the services**:
   ```bash
   docker-compose up -d
   ```

4. **Access the application**:
   - Frontend: http://localhost:8080
   - Backend API: http://localhost:8080/api
   - API Documentation: http://localhost:8080/docs

### Local Development

#### Backend Setup
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

# Set environment variables
export DATABASE_URL="postgresql+asyncpg://311_user:password@localhost:5432/township_311"
export SECRET_KEY="your_secret_key"

# Run the server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

#### Frontend Setup
```bash
cd frontend
npm install
npm run dev
```

## API Documentation

The API documentation is automatically generated and available at:
- Swagger UI: http://localhost:8080/docs
- ReDoc: http://localhost:8080/redoc

### Authentication
All protected endpoints require a Bearer token in the Authorization header:
```
Authorization: Bearer <your_jwt_token>
```

### Key Endpoints

#### Authentication
- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - Login and get JWT token
- `GET /api/auth/me` - Get current user info

#### Service Requests
- `GET /api/requests` - List requests (with filtering)
- `POST /api/requests` - Create new request
- `GET /api/requests/{id}` - Get request details
- `PUT /api/requests/{id}` - Update request (staff only)
- `POST /api/requests/{id}/assign` - Assign request to staff
- `POST /api/requests/{id}/status` - Update request status

#### Attachments
- `POST /api/requests/{id}/attachments` - Upload file
- `GET /api/requests/{id}/attachments` - List attachments

#### Comments
- `POST /api/requests/{id}/comments` - Add comment
- `GET /api/requests/{id}/comments` - List comments

## User Roles

### Citizen
- Submit service requests
- View own requests
- Upload attachments
- Add comments to own requests

### Staff
- All citizen permissions
- View all requests
- Assign requests
- Update request status
- Add internal comments

### Admin
- All staff permissions
- User management
- System configuration

## Configuration

### Environment Variables

#### Database
- `POSTGRES_USER` - Database username
- `POSTGRES_PASSWORD` - Database password
- `POSTGRES_DB` - Database name
- `POSTGRES_PORT` - Database port (default: 5432)

#### Application
- `BACKEND_PORT` - Backend server port (default: 8000)
- `FRONTEND_PORT` - Frontend development server port (default: 5173)
- `SECRET_KEY` - JWT secret key (generate secure random key)
- `JWT_EXPIRATION_MINUTES` - JWT token expiration time (default: 30)

#### File Upload
- `MAX_FILE_SIZE` - Maximum file size in bytes (default: 10MB)
- `ALLOWED_FILE_TYPES` - Comma-separated list of allowed file extensions

#### Security
- `CORS_ORIGINS` - Comma-separated list of allowed CORS origins

### File Upload Configuration

The system supports various file types with automatic virus scanning:
- Documents: PDF, DOC, DOCX
- Images: JPG, JPEG, PNG
- Maximum file size: 10MB per file
- Virus scanning: All files are scanned with ClamAV

## Deployment

### Production Deployment

1. **Update environment variables** in `.env.production`:
   ```bash
   # Generate secure secrets
   SECRET_KEY=$(openssl rand -hex 32)
   POSTGRES_PASSWORD=$(openssl rand -hex 16)
   ```

2. **Build and start services**:
   ```bash
   docker-compose -f docker-compose.yml up -d
   ```

3. **Setup SSL/TLS** (recommended):
   - Configure reverse proxy (nginx/caddy)
   - Setup SSL certificates
   - Update CORS origins

### Docker Services

The system consists of several services:
- **backend**: FastAPI application
- **frontend**: React application
- **db**: PostgreSQL database
- **redis**: Redis cache
- **clamav**: ClamAV virus scanner
- **caddy**: Reverse proxy (optional)

## Monitoring and Maintenance

### Health Checks
- Backend health: `GET /health`
- Database connectivity: Automatic
- File upload system: Automatic

### Logs
```bash
# View all logs
docker-compose logs -f

# View specific service logs
docker-compose logs -f backend
docker-compose logs -f frontend
```

### Database Backup
```bash
# Backup database
docker-compose exec db pg_dump -U 311_user township_311 > backup.sql

# Restore database
docker-compose exec -T db psql -U 311_user township_311 < backup.sql
```

## Development

### Code Structure
```
backend/
├── app/
│   ├── api/          # API endpoints
│   ├── core/         # Core configuration
│   ├── models/       # Database models
│   ├── schemas/      # Pydantic schemas
│   └── services/     # Business logic
├── requirements.txt
└── Dockerfile

frontend/
├── src/
│   ├── components/   # React components
│   ├── contexts/     # React contexts
│   ├── pages/        # Page components
│   └── services/     # API services
├── package.json
└── Dockerfile

infra/
└── caddy/            # Caddy configuration
```

### Testing
```bash
# Backend tests
cd backend
pytest

# Frontend tests
cd frontend
npm test
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

This project is licensed under the MIT License.

## Support

For support and questions:
- Create an issue in the repository
- Check the documentation
- Review the API documentation at `/docs`

## Security

For security issues, please email security@yourtownship.gov instead of creating a public issue.
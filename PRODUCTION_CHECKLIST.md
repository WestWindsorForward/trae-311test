# Township 311 Request Management System - Production Deployment Checklist

## Pre-Deployment Checklist

### 1. Environment Configuration
- [ ] Update `.env` file with production values
- [ ] Change `SECRET_KEY` to a secure random value
- [ ] Update `POSTGRES_PASSWORD` to a secure password
- [ ] Configure proper CORS origins for production domain
- [ ] Set up email configuration (SMTP settings)
- [ ] Configure file upload limits and allowed types

### 2. Security Hardening
- [ ] Enable HTTPS with SSL certificates
- [ ] Configure firewall rules
- [ ] Set up rate limiting
- [ ] Enable audit logging
- [ ] Configure backup encryption
- [ ] Review and update CORS settings

### 3. Database Security
- [ ] Create dedicated database user with limited permissions
- [ ] Enable SSL for database connections
- [ ] Configure database backups
- [ ] Set up database monitoring
- [ ] Review and optimize database indexes

### 4. File Storage Security
- [ ] Configure secure file upload directory
- [ ] Set appropriate file permissions
- [ ] Enable virus scanning for all uploads
- [ ] Configure file retention policies
- [ ] Set up file backup procedures

## Deployment Steps

### 1. Infrastructure Setup
```bash
# Clone repository
git clone <your-repo-url>
cd township-311-system

# Copy and configure environment
cp .env.example .env
# Edit .env with production values

# Make deployment script executable
chmod +x deploy.sh
```

### 2. Deploy Application
```bash
# Run deployment script
./deploy.sh

# Verify deployment
docker-compose ps
curl http://localhost:8080/health
```

### 3. Database Initialization
```bash
# Create database tables
docker-compose exec backend python -c "
from app.core.database import engine
from app.models.models import Base
import asyncio

async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

asyncio.run(init_db())
"
```

### 4. Create Initial Admin User
```bash
# Create admin user (replace with your details)
curl -X POST http://localhost:8080/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@yourtownship.gov",
    "password": "secure_admin_password",
    "full_name": "System Administrator",
    "role": "admin"
  }'
```

## Post-Deployment Verification

### 1. Service Health Checks
- [ ] Backend API responds to health check
- [ ] Frontend loads without errors
- [ ] Database connections are working
- [ ] File upload functionality works
- [ ] Email notifications work (if configured)

### 2. Security Verification
- [ ] HTTPS is working properly
- [ ] Authentication is required for protected routes
- [ ] File uploads are scanned for viruses
- [ ] Database is not accessible from external networks
- [ ] Admin endpoints require admin privileges

### 3. Functionality Testing
- [ ] User registration works
- [ ] User login works
- [ ] Service request creation works
- [ ] File upload works
- [ ] Request status updates work
- [ ] Comments system works
- [ ] Search and filtering works

## Monitoring and Maintenance

### 1. Monitoring Setup
- [ ] Set up application monitoring (Prometheus/Grafana)
- [ ] Configure log aggregation (ELK stack or similar)
- [ ] Set up database monitoring
- [ ] Configure disk space monitoring
- [ ] Set up SSL certificate expiration alerts

### 2. Backup Procedures
- [ ] Configure automated database backups
- [ ] Set up file system backups
- [ ] Test backup restoration procedures
- [ ] Document backup retention policies

### 3. Security Updates
- [ ] Schedule regular security updates
- [ ] Monitor security advisories for dependencies
- [ ] Plan for security patch deployment
- [ ] Review access logs regularly

## Performance Optimization

### 1. Database Optimization
- [ ] Review and optimize slow queries
- [ ] Configure connection pooling
- [ ] Set up read replicas if needed
- [ ] Monitor database performance metrics

### 2. Application Optimization
- [ ] Configure caching (Redis)
- [ ] Optimize static file serving
- [ ] Set up CDN for static assets
- [ ] Monitor application performance

### 3. Infrastructure Optimization
- [ ] Configure load balancing if needed
- [ ] Set up auto-scaling policies
- [ ] Optimize container resource limits
- [ ] Monitor system resources

## Troubleshooting

### Common Issues

1. **Database Connection Issues**
   - Check database container status
   - Verify connection string in .env
   - Check firewall rules

2. **File Upload Issues**
   - Verify upload directory permissions
   - Check ClamAV container status
   - Review file size limits

3. **Authentication Issues**
   - Verify SECRET_KEY is set correctly
   - Check JWT token expiration
   - Review user permissions

4. **Performance Issues**
   - Monitor database query performance
   - Check for memory leaks
   - Review application logs

### Log Locations
```bash
# Backend logs
docker-compose logs backend

# Frontend logs
docker-compose logs frontend

# Database logs
docker-compose logs db

# All services
docker-compose logs -f
```

## Support and Maintenance Contacts

- **System Administrator**: [Your contact info]
- **Database Administrator**: [Your contact info]
- **Security Team**: [Your contact info]
- **Development Team**: [Your contact info]

## Emergency Procedures

### Service Outage
1. Check service status: `docker-compose ps`
2. Review logs for errors
3. Restart services if needed: `docker-compose restart`
4. Contact support team if issues persist

### Security Incident
1. Isolate affected systems
2. Review access logs
3. Contact security team
4. Follow incident response procedures

### Data Recovery
1. Stop application services
2. Restore from latest backup
3. Verify data integrity
4. Restart services

---

**Last Updated**: [Current Date]
**Version**: 1.0.0
**Next Review**: [30 days from current date]
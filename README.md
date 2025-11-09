# Blog Platform Backend API

A comprehensive, production-ready blogging platform backend built with FastAPI and PostgreSQL.

## Features

- **User Authentication**: Registration, login, password reset, and email verification
- **Blog Posts**: Create, read, update, delete posts with categories and tags
- **Comments**: Nested comments on posts with approval system
- **Search & Filtering**: Full-text search, filter by category/tags with pagination
- **Rate Limiting**: Protection against abuse on auth endpoints
- **Soft Deletes**: Audit trail with deleted_at timestamps
- **Comprehensive Audit Trail**: Track who added/updated records and when
- **Email Notifications**: HTML-based email templates via SMTP
- **CORS Support**: Configured for cross-origin requests
- **API Documentation**: Interactive Swagger UI at `/docs`
- **Structured Logging**: Environment-based log level configuration

## Tech Stack

- **Framework**: FastAPI
- **Database**: PostgreSQL with SQLAlchemy ORM
- **Authentication**: JWT with python-jose
- **Email**: SMTP with Jinja2 templates
- **Validation**: Pydantic v2
- **Rate Limiting**: slowapi
- **Migrations**: Alembic
- **Testing**: pytest with pytest-asyncio
- **Deployment**: Docker & Docker Compose

## Project Structure

```
.
├── app/
│   ├── core/              # Configuration, database, security
│   │   ├── config.py      # Settings management
│   │   ├── database.py    # Database connection & session
│   │   ├── security.py    # JWT & password handling
│   │   └── logging.py     # Logging configuration
│   ├── models/            # SQLAlchemy ORM models
│   │   ├── base.py        # Base model with audit columns
│   │   └── models.py      # User, Post, Comment, Category, Tag models
│   ├── schemas/           # Pydantic request/response models
│   ├── routes/            # API endpoints (v1)
│   │   ├── auth.py        # Authentication endpoints
│   │   ├── posts.py       # Post CRUD operations
│   │   ├── comments.py    # Comment management
│   │   ├── categories.py  # Category management
│   │   └── tags.py        # Tag management
│   ├── services/          # Business logic
│   │   ├── service.py     # CRUD services
│   │   └── email_service.py # Email handling
│   ├── utils/             # Helper functions
│   │   └── helpers.py     # Utilities and response formatting
│   └── templates/         # Email templates
│       └── emails/        # HTML email templates
├── alembic/               # Database migrations
├── tests/                 # Test suite
├── main.py                # FastAPI application entry point
├── requirements.txt       # Python dependencies
├── docker-compose.yml     # Docker Compose configuration
├── Dockerfile             # Docker image configuration
└── README.md              # This file

```

## Setup Instructions

### Prerequisites

- Python 3.11+
- PostgreSQL 12+
- Docker & Docker Compose (optional)

### Local Development

1. **Clone and navigate to the project:**
   ```bash
   cd /Users/apple/Documents/Work/dockr_demo
   ```

2. **Create virtual environment:**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables:**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

5. **Run database migrations:**
   ```bash
   alembic upgrade head
   ```

6. **Start the server:**
   ```bash
   uvicorn main:app --reload
   ```

   The API will be available at `http://localhost:8000`
   - API Documentation: `http://localhost:8000/docs`
   - ReDoc: `http://localhost:8000/redoc`

### Docker Setup

1. **Build and run with Docker Compose:**
   ```bash
   docker-compose up -d
   ```

2. **Run migrations in container:**
   ```bash
   docker-compose exec fastapi_app alembic upgrade head
   ```

3. **Access the API:**
   ```
   http://localhost:8000
   ```

## API Endpoints

### Authentication (`/api/v1/auth`)

- `POST /signup` - Register new user
- `POST /signin` - User login
- `POST /forgot-password` - Request password reset
- `POST /reset-password` - Reset password with token
- `POST /change-password` - Change password (authenticated)

### Posts (`/api/v1/posts`)

- `POST /` - Create new post (authenticated)
- `GET /` - List published posts (paginated, filterable)
- `GET /{post_id}` - Get post details
- `GET /search/{search_query}` - Search posts
- `GET /user/{user_id}` - Get user's posts
- `PUT /{post_id}` - Update post (author only)
- `DELETE /{post_id}` - Delete post (author only)

### Comments (`/api/v1/comments`)

- `POST /post/{post_id}` - Create comment (authenticated)
- `GET /{comment_id}` - Get comment details
- `GET /post/{post_id}` - List comments on post
- `PUT /{comment_id}` - Update comment (author only)
- `DELETE /{comment_id}` - Delete comment (author only)

### Categories (`/api/v1/categories`)

- `POST /` - Create category (authenticated)
- `GET /` - List categories
- `GET /{category_id}` - Get category details
- `DELETE /{category_id}` - Delete category (authenticated)

### Tags (`/api/v1/tags`)

- `POST /` - Create tag (authenticated)
- `GET /` - List tags
- `GET /{tag_id}` - Get tag details
- `DELETE /{tag_id}` - Delete tag (authenticated)

## Configuration

Edit `.env` file to configure:

| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE_URL` | PostgreSQL connection string | Required |
| `SECRET_KEY` | JWT secret key | Required |
| `SMTP_HOST` | Email SMTP server | smtp.gmail.com |
| `SMTP_PORT` | Email SMTP port | 587 |
| `SMTP_USER` | Email account | Required |
| `SMTP_PASSWORD` | Email password/token | Required |
| `CORS_ORIGINS` | Allowed origins (comma-separated) | localhost:3000,localhost:8000 |
| `DEBUG` | Debug mode | False |
| `LOG_LEVEL` | Logging level (DEBUG, INFO, WARNING, ERROR) | INFO |

## Database Models

### User
- email, username, full_name, password
- Profile fields: bio, profile_image_url
- Status: is_active, is_verified

### Post
- title, slug, content, excerpt
- Relationships: author (User), category (Category), tags (Tag)
- Publication: is_published, published_at
- Meta: view_count, featured_image_url

### Comment
- content, post_id, author_id
- Nested comments: parent_comment_id
- Approval: is_approved

### Category
- name, slug, description

### Tag
- name, slug

### Audit Columns (All Tables)
- `date_added` - Creation timestamp
- `date_updated` - Last update timestamp
- `added_by` - User ID who created the record
- `updated_by` - User ID who last updated
- `deleted_at` - Soft delete timestamp

## Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app tests/

# Run specific test file
pytest tests/test_auth.py
```

## Email Configuration

### Gmail Setup

1. Enable 2-Factor Authentication on your Google Account
2. Generate an App Password: https://myaccount.google.com/apppasswords
3. Use the 16-character password in `.env`:
   ```
   SMTP_USER=your-email@gmail.com
   SMTP_PASSWORD=xxxx xxxx xxxx xxxx
   ```

### Other Providers

- **SendGrid**: Use API key in SMTP password field
- **Mailgun**: Configure SMTP credentials
- **Development**: Configure mock email service

## Rate Limiting

Auth endpoints are rate-limited to prevent brute force attacks:
- `/signup` - 100 requests per minute
- `/signin` - 100 requests per minute  
- `/forgot-password` - 100 requests per minute

Configure via `.env`:
```
RATE_LIMIT_ENABLED=True
RATE_LIMIT_REQUESTS=100
RATE_LIMIT_PERIOD=60
```

## Production Deployment

### Pre-deployment Checklist

- [ ] Change `SECRET_KEY` to a strong random value
- [ ] Set `DEBUG=False`
- [ ] Configure real SMTP credentials
- [ ] Update `CORS_ORIGINS` for your frontend domain
- [ ] Use a production database
- [ ] Set up HTTPS/SSL
- [ ] Configure proper logging and monitoring
- [ ] Run database migrations: `alembic upgrade head`

### Deployment Options

1. **Docker**: Use provided Dockerfile and docker-compose.yml
2. **Cloud Platforms**: AWS, GCP, Azure, Heroku, Railway
3. **VPS**: Deploy with Nginx reverse proxy and Gunicorn

### Example with Gunicorn

```bash
gunicorn main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

## Development

### Code Style

- Python 3.11+
- Type hints throughout
- Follow PEP 8 standards
- Use `black` for formatting (future enhancement)

### Adding New Routes

1. Create new file in `app/routes/`
2. Define router with `/api/v1/` prefix
3. Include in `main.py`
4. Add corresponding services and models

### Adding New Database Models

1. Add model to `app/models/models.py`
2. Inherit from `BaseModel` for audit columns
3. Create migration: `alembic revision --autogenerate -m "Add new model"`
4. Review and adjust migration file
5. Run: `alembic upgrade head`

## Troubleshooting

### Database Connection Issues

```bash
# Test database connection
PGPASSWORD=password psql -h localhost -U postgres -d blog_db
```

### Email Not Sending

- Verify SMTP credentials
- Check firewall/network policies
- Review application logs: `logs/app.log`
- Enable debug mode for more details

### Migration Issues

```bash
# Reset migrations (development only)
alembic downgrade base
alembic upgrade head

# Check migration status
alembic current
alembic history
```

## API Response Format

### Success Response
```json
{
  "success": true,
  "message": "Operation successful",
  "data": { }
}
```

### Error Response
```json
{
  "success": false,
  "message": "Error message",
  "detail": "Detailed error information",
  "status_code": 400
}
```

## Contributing

1. Fork the repository
2. Create feature branch: `git checkout -b feature/amazing-feature`
3. Commit changes: `git commit -m 'Add amazing feature'`
4. Push to branch: `git push origin feature/amazing-feature`
5. Open Pull Request

## License

This project is licensed under the MIT License - see LICENSE file for details.

## Support

For issues and questions:
- GitHub Issues: [Project Issues]
- Email: support@blogplatform.com
- Documentation: [API Docs](http://localhost:8000/docs)

---

Built with ❤️ using FastAPI

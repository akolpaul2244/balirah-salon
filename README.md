# Balirah Beauty Salon — Django Web Application

Production-ready Django 5 web application for Balirah Beauty Salon, a premium barber shop and nails parlor in Kampala, Uganda.

---

## Tech Stack

- **Backend:** Django 5.0, Python 3.11+
- **Database:** PostgreSQL
- **Cache / Broker:** Redis
- **Task Queue:** Celery + Celery Beat
- **API:** Django REST Framework
- **SMS:** Africa's Talking
- **Email:** SMTP (Gmail / any provider)
- **Deployment:** Gunicorn + WhiteNoise (Render / Railway / VPS)

---

## Project Structure

```
balirah_salon/
├── balirah_salon/          # Project config
│   ├── settings/
│   │   ├── base.py
│   │   ├── development.py
│   │   └── production.py
│   ├── urls.py
│   ├── celery.py
│   ├── wsgi.py
│   └── asgi.py
├── apps/
│   ├── core/               # Home, About, Contact, Settings, Sitemaps
│   ├── accounts/           # Custom User, Auth, Profile
│   ├── services/           # Service Categories, Services, Promotions
│   ├── bookings/           # Appointments, Time Slots, Availability
│   ├── team/               # Stylists
│   ├── gallery/            # Gallery Categories and Images
│   ├── blog/               # Blog Posts and Categories
│   ├── notifications/      # SMS, Email, Campaigns, Logs
│   ├── testimonials/       # Client Reviews
│   └── faqs/               # FAQs
├── templates/              # HTML templates (to be created)
├── static/                 # CSS, JS, Images
├── media/                  # User-uploaded files
├── manage.py
├── requirements.txt
├── Procfile
├── gunicorn.conf.py
└── render.yaml
```

---

## Local Setup

### 1. Clone and create virtual environment

```bash
git clone <repo-url>
cd balirah_salon
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure environment

```bash
cp .env.example .env
# Edit .env with your values
```

### 4. Create PostgreSQL database

```sql
CREATE DATABASE balirah_salon_dev;
CREATE USER postgres WITH PASSWORD 'yourpassword';
GRANT ALL PRIVILEGES ON DATABASE balirah_salon_dev TO postgres;
```

### 5. Run migrations

```bash
python manage.py migrate
```

### 6. Seed sample data

```bash
python manage.py seed_data
```

### 7. Create superuser

```bash
python manage.py createsuperuser
```

### 8. Collect static files

```bash
python manage.py collectstatic
```

### 9. Start Redis (required for caching and Celery)

```bash
redis-server
```

### 10. Start Celery worker (separate terminal)

```bash
celery -A balirah_salon worker --loglevel=info
```

### 11. Start Celery Beat scheduler (separate terminal)

```bash
celery -A balirah_salon beat --loglevel=info
```

### 12. Run development server

```bash
python manage.py runserver
```

---

## Running Tests

```bash
python manage.py test apps.core apps.accounts apps.services apps.bookings --verbosity=2
```

---

## Deployment to Render

1. Push your repo to GitHub.
2. Create a new Web Service on [render.com](https://render.com).
3. Set environment variables from `.env.example` in the Render dashboard.
4. Render will detect `render.yaml` and create the web service, worker, beat, database, and Redis automatically.

---

## Admin Panel

Access at `/admin/`. Key sections:

| Section | What you manage |
|---|---|
| Salon Settings | Name, contact, social links, SEO, legal pages |
| Opening Hours | Per-day opening and closing times |
| Services | Categories, services, pricing, promotions |
| Team | Stylists, roles, specialisations |
| Bookings | Appointments, time slots, blocked slots |
| Gallery | Categories and images |
| Blog | Posts and categories |
| Notifications | SMS logs, email logs, campaigns |
| Testimonials | Approve and feature client reviews |
| FAQs | Questions and categories |
| Contact Messages | Inbox from the contact form |

---

## SMS Notifications

Set `SMS_PROVIDER=africas_talking` in production and provide your Africa's Talking credentials.

In development, set `SMS_PROVIDER=console` to print SMS messages to the terminal instead of sending them.

Automated SMS events:
- Appointment confirmation (immediate)
- 24-hour reminder
- 2-hour reminder
- Cancellation notice
- Re-engagement (configurable days after service)
- Birthday promotion (daily at 8 AM)
- Bulk campaigns (from admin panel)

---

## API Endpoints

Base URL: `/api/v1/`

| Endpoint | Methods | Description |
|---|---|---|
| `services/` | GET | List all active services |
| `services/<id>/` | GET | Service detail |
| `service-categories/` | GET | Categories with services |
| `stylists/` | GET | List active stylists |
| `stylists/?service=<id>` | GET | Stylists available for a service |
| `appointments/` | GET, POST | User's appointments |
| `appointments/<id>/` | GET, DELETE | Appointment detail / cancel |
| `slots/` | GET | Available time slots |
| `testimonials/` | GET, POST | Approved reviews / submit review |

---

## Future Enhancements

- Online payments (MTN Mobile Money, Airtel Money, Stripe)
- Real-time notifications with Django Channels / WebSockets
- Loyalty points and rewards system
- Staff mobile app
- Multi-branch support
- Analytics dashboard with appointment and revenue charts
- Instagram feed integration
- Google Calendar sync for stylists

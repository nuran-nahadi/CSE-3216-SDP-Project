# LIN: AI-Powered Personal Life Manager

LIN is a unified web application that empowers users to effortlessly track and reflect on key aspects of their daily lives—tasks, events, expenses, and personal reflections—while leveraging advanced language models to automate data entry, analysis, and insights generation.


## 🗂 Core Features

1. **In-Built Calendar**  
   - **Create / View Events**: schedule events with title, description, start/end datetime, location, and tags  
   - **Natural-Language Entry**: "Lunch with Sarah tomorrow at noon" → auto-populate fields  
   - **List / Filter**: retrieve upcoming or past events, filter by date range or tag  

2. **To-Do List**  
   - **Task CRUD**: create, read, update, and delete tasks  
   - **Prioritization & Status**: set priority (low/medium/high), due date, completion status  
   - **Natural-Language Commands**: "Remind me to call mom on Friday" → task + reminder  

3. **Expense Tracker**  
   - **Log Purchases**: amount, currency, category (food, transport, bills, etc.), date, optional notes  
   - **Voice-Driven Entry**: "I spent $12.50 on coffee today" → auto-categorize  
   - **List & Summaries**: view expenses by date range, category breakdown, monthly totals  

4. **Journal**  
   - **Daily Entries**: free-form text, mood tag (e.g., 😊, 😐, 😞), optional images  
   - **AI-Assisted Analysis**: sentiment score, keyword extraction, entry summaries  
   - **Search & Filter**: by date, mood, or keyword  

---

## 📊 Insights & Recommendations

- **Performance Metrics**  
  - Task completion rate (% completed on time)  
  - Logging consistency (days in a row with any entry)  
  - Mood trends (weekly/monthly sentiment averages)  
  - Spending patterns (category-wise trends)

- **Personalized Suggestions**  
  - Auto-generated tips, e.g.:  
    - "Batch low-priority tasks on Wednesdays"  
    - "Your coffee spending spiked this week—consider brewing at home"  

- **Interactive Dashboard**  
  - Visual cards (e.g., "Tasks Today," "Expenses This Week")  
  - Sparklines for trends  
  - Highlights feed with key insights and suggestions  

---

## 🔧 Tech Stack

- **Framework**: FastAPI  
- **ORM**: SQLAlchemy 
- **Database**: PostgreSQL  
- **AI Services**: Google Gemini for NLU & insights  
- **Authentication**: OAuth2 / JWT  
<!-- - **Background Tasks**: Celery + Redis (voice transcription, sentiment analysis)   -->
- **Deployment**: Docker 
- **Design Patterns**: Singleton Pattern for database and configuration management

---

## 🏗️ Architecture & Design Patterns

### Singleton Pattern Implementation

The backend implements the **Singleton Pattern** for critical system components to ensure:

- **Single Database Connection Pool**: Efficient resource management
- **Centralized Configuration**: Unified settings access across the application
- **Service Management**: Centralized service location and status monitoring

#### Core Singleton Components:

1. **ConfigManager** (`app/core/config_manager.py`)
   - Manages all application configuration
   - Environment variable handling
   - Runtime configuration updates

2. **DatabaseManager** (`app/core/database_manager.py`)
   - Single database connection pool
   - Session management and health checks
   - Connection monitoring and reset capabilities

3. **ServiceManager** (`app/core/service_manager.py`)
   - Service locator pattern implementation
   - Application status monitoring
   - Centralized service access

#### Usage in FastAPI Routes:

```python
from fastapi import Depends
from app.core.dependencies import get_database_session, get_config_manager

@router.get("/example")
def example_endpoint(
    db: Session = Depends(get_database_session),
    config = Depends(get_config_manager)
):
    return {"debug": config.is_debug_mode()}
```

#### System Monitoring:

- **Health Check**: `/health` - Enhanced with system status
- **System Status**: `/system/status` - Comprehensive application status
- **Database Info**: `/system/database/info` - Connection pool monitoring
- **Configuration**: `/system/config/settings` - Runtime configuration view

For detailed information, see [SINGLETON_PATTERN_GUIDE.md](./SINGLETON_PATTERN_GUIDE.md)

---

## 🗄️ Data Models

### User
- `id: UUID` (Primary Key)
- `username: String` (Unique)
- `email: String` (Unique)
- `first_name: String`
- `last_name: String`
- `hashed_password: String`
- `is_verified: Boolean` (Default: False)
- `profile_picture_url: String` (Optional)
- `timezone: String` (Default: UTC)
- `created_at: DateTime`
- `updated_at: DateTime`

### Event
- `id: UUID` (Primary Key)
- `user_id: UUID` (Foreign Key → User.id)
- `title: String` (Required)
- `description: Text` (Optional)
- `start_time: DateTime` (Required)
- `end_time: DateTime` (Required)
- `location: String` (Optional)
- `tags: JSON[]` (Optional)
- `is_all_day: Boolean` (Default: False)
- `reminder_minutes: Integer` (Optional, minutes before event)
- `recurrence_rule: String` (Optional, RRULE format)
- `color: String` (Optional, hex color code)
- `created_at: DateTime`
- `updated_at: DateTime`

### Task
- `id: UUID` (Primary Key)
- `user_id: UUID` (Foreign Key → User.id)
- `title: String` (Required)
- `description: Text` (Optional)
- `due_date: DateTime` (Optional)
- `priority: Enum('low', 'medium', 'high')` (Default: 'medium')
- `status: Enum('pending', 'in_progress', 'completed', 'cancelled')` (Default: 'pending')
- `is_completed: Boolean` (Default: False)
- `completion_date: DateTime` (Optional)
- `estimated_duration: Integer` (Optional, in minutes)
- `actual_duration: Integer` (Optional, in minutes)
- `tags: JSON[]` (Optional)
- `parent_task_id: UUID` (Optional, for subtasks)
- `created_at: DateTime`
- `updated_at: DateTime`

### Expense
- `id: UUID` (Primary Key)
- `user_id: UUID` (Foreign Key → User.id)
- `amount: Decimal(10,2)` (Required)
- `currency: String` (Default: 'Taka')
- `category: Enum('food', 'transport', 'entertainment', 'bills', 'shopping', 'health', 'education', 'travel', 'other')` (Required)
- `subcategory: String` (Optional)
- `merchant: String` (Optional)
- `description: Text` (Optional)
- `date: Date` (Required)
- `payment_method: Enum('cash', 'credit_card', 'debit_card', 'bank_transfer', 'digital_wallet', 'other')`
- `receipt_url: String` (Optional)
- `is_recurring: Boolean` (Default: False)
- `recurrence_rule: String` (Optional)
- `tags: JSON[]` (Optional)
- `created_at: DateTime`
- `updated_at: DateTime`

### JournalEntry
- `id: UUID` (Primary Key)
- `user_id: UUID` (Foreign Key → User.id)
- `title: String` (Optional)
- `content: Text` (Required)
- `mood: Enum('very_happy', 'happy', 'neutral', 'sad', 'very_sad', 'angry', 'excited', 'anxious', 'grateful')` (Optional)
- `sentiment_score: Float` (Range: -1.0 to 1.0, calculated by AI)
- `keywords: JSON[]` (Extracted by AI)
- `summary: Text` (Generated by AI)
- `weather: String` (Optional)
- `location: String` (Optional)
- `created_at: DateTime`
- `updated_at: DateTime`

### Notification
- `id: UUID` (Primary Key)
- `user_id: UUID` (Foreign Key → User.id)
- `title: String` (Required)
- `message: Text` (Required)
- `type: Enum('task_reminder', 'event_reminder', 'expense_alert', 'insight', 'system')` (Required)
- `related_entity_type: String` (Optional: 'task', 'event', 'expense', 'journal')
- `related_entity_id: UUID` (Optional)
- `is_read: Boolean` (Default: False)
- `scheduled_for: DateTime` (Optional, for future delivery)
- `delivered_at: DateTime` (Optional)
- `created_at: DateTime`

### UserPreferences
- `id: UUID` (Primary Key)
- `user_id: UUID` (Foreign Key → User.id, Unique)
- `default_task_priority: Enum('low', 'medium', 'high')` (Default: 'medium')
- `default_expense_currency: String` (Default: 'USD')
- `notification_settings: JSON` (Email, push, in-app preferences)
- `theme: Enum('light', 'dark', 'auto')` (Default: 'auto')
- `language: String` (Default: 'en')
- `date_format: String` (Default: 'YYYY-MM-DD')
- `time_format: Enum('12h', '24h')` (Default: '12h')
- `week_start_day: Enum('monday', 'sunday')` (Default: 'monday')
- `ai_insights_enabled: Boolean` (Default: True)
- `created_at: DateTime`
- `updated_at: DateTime`

### AIInsight
- `id: UUID` (Primary Key)
- `user_id: UUID` (Foreign Key → User.id)
- `type: Enum('productivity', 'spending', 'mood', 'habits', 'recommendations')` (Required)
- `title: String` (Required)
- `content: Text` (Required)
- `data_points: JSON` (Underlying data used for insight)
- `confidence_score: Float` (Range: 0.0 to 1.0)
- `priority: Enum('low', 'medium', 'high')` (Default: 'medium')
- `is_dismissed: Boolean` (Default: False)
- `valid_until: DateTime` (Optional, for time-sensitive insights)
- `created_at: DateTime`

---

## 📡 API Endpoints

### Authentication
- `POST /auth/signup` → Register new user
- `POST /auth/login` → Login and get JWT token
- `POST /auth/logout` → Logout (invalidate token)
- `POST /auth/refresh` → Refresh JWT token
- `POST /auth/forgot-password` → Request password reset
- `POST /auth/reset-password` → Reset password with token
- `GET  /auth/verify-email/{token}` → Verify email address
- `POST /auth/resend-verification` → Resend verification email

### User Profile
- `GET    /users/me` → Get current user profile
- `PUT    /users/me` → Update user profile
- `POST   /users/me/avatar` → Upload profile picture
- `DELETE /users/me/avatar` → Remove profile picture
- `GET    /users/me/preferences` → Get user preferences
- `PUT    /users/me/preferences` → Update user preferences
- `DELETE /users/me` → Delete user account

### Events
- `GET    /events` → List events (filters: `start_date`, `end_date`, `tags`, `search`)
- `POST   /events` → Create new event
- `GET    /events/{id}` → Get specific event
- `PUT    /events/{id}` → Update event
- `DELETE /events/{id}` → Delete event
- `GET    /events/calendar/{year}/{month}` → Get calendar view for month
<!-- - `POST   /events/{id}/duplicate` → Duplicate event -->
- `GET    /events/upcoming` → Get upcoming events (next 7 days)

### Tasks
- `GET    /tasks` → List tasks (filters: `status`, `priority`, `due_date`, `tags`, `search`)
- `POST   /tasks` → Create new task
- `GET    /tasks/{id}` → Get specific task
- `PUT    /tasks/{id}` → Update task
- `DELETE /tasks/{id}` → Delete task
- `PATCH  /tasks/{id}/complete` → Mark task as complete
- `GET    /tasks/today` → Get today's tasks
- `GET    /tasks/overdue` → Get overdue tasks
<!-- - `POST   /tasks/{id}/subtasks` → Create subtask
- `GET    /tasks/{id}/subtasks` → Get task subtasks -->

### Expenses
- `GET    /expenses` → List expenses (filters: `start_date`, `end_date`, `category`, `min_amount`, `max_amount`, `search`)
- `POST   /expenses` → Create new expense
- `GET    /expenses/{id}` → Get specific expense
- `PUT    /expenses/{id}` → Update expense
- `DELETE /expenses/{id}` → Delete expense
- `GET    /expenses/summary` → Get spending summary (by period/category)
- `GET    /expenses/categories` → Get expense categories with totals
- `GET    /expenses/monthly/{year}/{month}` → Get monthly expenses
- `GET    /expenses/recurring` → Get recurring expenses
<!-- - `POST   /expenses/bulk` → Bulk import expenses (CSV)
- `GET    /expenses/export` → Export expenses (CSV/PDF) -->

### Journal
- `GET    /journal` → List journal entries (filters: `start_date`, `end_date`, `mood`, `search`)
- `POST   /journal` → Create new journal entry (triggers AI analysis)
- `GET    /journal/{id}` → Get specific journal entry
- `PUT    /journal/{id}` → Update journal entry
- `DELETE /journal/{id}` → Delete journal entry
<!-- - `POST   /journal/{id}/images` → Upload images to journal entry
- `DELETE /journal/{id}/images/{image_id}` → Remove image from entry -->
- `POST   /journal/analyze` → Trigger AI analysis for existing entries
- `GET    /journal/stats` → Get journaling statistics

### Notifications
- `GET    /notifications` → List notifications (filters: `is_read`, `type`)
- `PATCH  /notifications/{id}/read` → Mark notification as read
- `PATCH  /notifications/read-all` → Mark all notifications as read
- `DELETE /notifications/{id}` → Delete notification
- `POST   /notifications/test` → Send test notification

### Insights & Analytics
- `GET /insights/dashboard` → Get dashboard overview
- `GET /insights/tasks` → Task completion rates and trends
- `GET /insights/expenses` → Spending patterns and analysis
- `GET /insights/journal` → Mood trends and journaling patterns
- `GET /insights/productivity` → Productivity metrics and patterns
- `GET /insights/suggestions` → AI-generated personalized suggestions
- `GET /insights/goals` → Goal tracking and progress
- `POST /insights/refresh` → Trigger AI insight generation

### AI Services
- `POST   /events/parse` → Parse natural language into event data
- `POST   /expenses/parse` → Parse natural language into expense data
- `POST   /expenses/{id}/receipt` → Upload receipt image
- `POST   /tasks/parse` → Parse natural language into task data
- `POST   /journal/parse` → Parse natural language into journal data
- `GET    /journal/mood-trends` → Get mood trends over time


- `POST /ai/parse-text` → Parse natural language input
- `POST /ai/analyze-sentiment` → Analyze text sentiment
- `POST /ai/extract-keywords` → Extract keywords from text
- `POST /ai/summarize` → Summarize long text
- `POST /ai/transcribe` → Transcribe audio to text
- `POST /ai/chat` → Chat with AI assistant about data

### Search & Voice
- `GET  /search` → Global search across all data types
- `POST /voice/transcribe` → Transcribe voice input
- `POST /voice/command` → Process voice command

<!-- ### Export & Backup
- `GET  /export/all` → Export all user data
- `GET  /export/tasks` → Export tasks data
- `GET  /export/events` → Export events data
- `GET  /export/expenses` → Export expenses data
- `GET  /export/journal` → Export journal data
- `POST /backup/create` → Create data backup
- `GET  /backup/download/{backup_id}` → Download backup file -->
<!-- 
### System & Health
- `GET /health` → API health check
- `GET /version` → API version info
- `GET /stats` → System statistics (admin only) -->

---

## 🔐 Authentication & Authorization

- **JWT Tokens**: Access tokens (15min) + Refresh tokens (7 days)
- **Role-based Access**: User roles for future admin features
- **Rate Limiting**: API rate limits per user/endpoint
- **CORS**: Configured for frontend domains
- **Input Validation**: Pydantic models for request/response validation

---

## 📱 Response Formats

All endpoints return JSON with consistent structure:
```json
{
  "success": true,
  "data": {...},
  "message": "Operation completed successfully",
  "meta": {
    "timestamp": "2025-06-21T10:30:00Z",
    "pagination": {...}
  }
}
```

Error responses:
```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid input data",
    "details": {...}
  }
}
```
Configuration Guide
===================

This document provides comprehensive information about configuring the Django News Application. Proper configuration is essential for development, testing, and production environments.

Configuration Overview
----------------------

The News Application uses Django's settings system with environment-specific configurations. The main configuration areas include:

* **Database Configuration**: MySQL database settings and connection parameters
* **Authentication & Security**: JWT tokens, secret keys, and security settings
* **Media & Static Files**: File upload and static asset configuration
* **API Configuration**: Django REST Framework and CORS settings
* **Email Configuration**: SMTP settings for notifications (if implemented)
* **Environment Variables**: Secure configuration through environment files
* **Third-Party Integrations**: Twitter API configuration for social features

Django Settings Structure
-------------------------

Settings File Location
~~~~~~~~~~~~~~~~~~~~~~

The main settings file is located at:

.. code-block:: text

   News/settings.py

This file contains all Django configuration including:

* Database connections
* Installed applications
* Middleware configuration
* Authentication backends
* API framework settings

**Required Imports**:

.. code-block:: python

   from pathlib import Path
   import os
   from dotenv import load_dotenv
   from datetime import timedelta

   # Load environment variables from .env file
   load_dotenv()

   # Build paths inside the project like this: BASE_DIR / 'subdir'.
   BASE_DIR = Path(__file__).resolve().parent.parent

Core Settings
~~~~~~~~~~~~~

**Secret Key**

.. code-block:: python

   SECRET_KEY = os.getenv(
       'SECRET_KEY',
       'django-insecure-%^%^=&!2rse8=b2@mquuwi^v9wf^j)vnl&t*(_i&hcd_vlii^t'
   )

**Debug Mode**

.. code-block:: python

   DEBUG = os.getenv('DEBUG', 'True') == 'True'

**Allowed Hosts**

.. code-block:: python

   ALLOWED_HOSTS = (
       os.getenv('ALLOWED_HOSTS', '').split(',')
       if os.getenv('ALLOWED_HOSTS') else []
   )

**Additional Core Settings**

.. code-block:: python

   # URL configuration
   ROOT_URLCONF = 'News.urls'
   
   # WSGI application
   WSGI_APPLICATION = 'News.wsgi.application'
   
   # Default auto field type
   DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

**Templates Configuration**

.. code-block:: python

   TEMPLATES = [
       {
           'BACKEND': 'django.template.backends.django.DjangoTemplates',
           'DIRS': [BASE_DIR / 'templates'],
           'APP_DIRS': True,
           'OPTIONS': {
               'context_processors': [
                   'django.template.context_processors.debug',
                   'django.template.context_processors.request',
                   'django.contrib.auth.context_processors.auth',
                   'django.contrib.messages.context_processors.messages',
                   'django.template.context_processors.media',
               ],
           },
       },
   ]

Database Configuration
----------------------

MySQL Database Settings
~~~~~~~~~~~~~~~~~~~~~~~~

The application uses MySQL as the primary database. Configuration is handled through Django's database settings:

.. code-block:: python

   DATABASES = {
       'default': {
           'ENGINE': 'django.db.backends.mysql',
           'NAME': os.getenv('DB_NAME', 'news_application_db'),
           'USER': os.getenv('DB_USER', 'root'),
           'PASSWORD': os.getenv('DB_PASSWORD', ''),
           'HOST': os.getenv('DB_HOST', 'localhost'),
           'PORT': os.getenv('DB_PORT', '3306'),
           'OPTIONS': {
               'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
           },
       }
   }

**Database Requirements**:

* MySQL 5.7+ or MySQL 8.0+
* Database charset: utf8mb4
* Collation: utf8mb4_unicode_ci

**Database Creation**:

.. code-block:: sql

   CREATE DATABASE news_application_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
   CREATE USER 'root'@'localhost' IDENTIFIED BY 'your_mysql_password';
   GRANT ALL PRIVILEGES ON news_application_db.* TO 'root'@'localhost';
   FLUSH PRIVILEGES;

Environment Variables
~~~~~~~~~~~~~~~~~~~~~

For security and flexibility, use environment variables for sensitive database information:

.. code-block:: python

   import os
   
   DATABASES = {
       'default': {
           'ENGINE': 'django.db.backends.mysql',
           'NAME': os.environ.get('DB_NAME', 'news_application_db'),
           'USER': os.environ.get('DB_USER', 'root'),
           'PASSWORD': os.environ.get('DB_PASSWORD', ''),
           'HOST': os.environ.get('DB_HOST', 'localhost'),
           'PORT': os.environ.get('DB_PORT', '3306'),
           'OPTIONS': {
               'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
           },
       }
   }

**.env File Example**:

.. code-block:: text

   DB_NAME=news_application_db
   DB_USER=root
   DB_PASSWORD=your_mysql_password
   DB_HOST=localhost
   DB_PORT=3306
   SECRET_KEY=your-very-long-secret-key-here
   DEBUG=True
   LANGUAGE_CODE=en-us
   TIME_ZONE=UTC
   
   # Email settings
   EMAIL_HOST=sandbox.smtp.mailtrap.io
   EMAIL_PORT=2525
   EMAIL_HOST_USER=your_mailtrap_user
   EMAIL_HOST_PASSWORD=your_mailtrap_password
   EMAIL_USE_TLS=True
   DEFAULT_FROM_EMAIL=your-app@example.com
   
   # Twitter API (optional)
   TWITTER_API_KEY=your_twitter_api_key
   TWITTER_API_SECRET=your_twitter_api_secret
   TWITTER_ACCESS_TOKEN=your_access_token
   TWITTER_ACCESS_TOKEN_SECRET=your_access_token_secret
   TWITTER_BEARER_TOKEN=your_bearer_token
   TWITTER_ENABLED=True

Installed Applications
----------------------

Required Django Apps
~~~~~~~~~~~~~~~~~~~~~

The application requires the following Django apps to be installed:

.. code-block:: python

   INSTALLED_APPS = [
       'django.contrib.admin',
       'django.contrib.auth',
       'django.contrib.contenttypes',
       'django.contrib.sessions',
       'django.contrib.messages',
       'django.contrib.staticfiles',
       
       # Third-party apps
       'rest_framework',
       'rest_framework_simplejwt',
       
       # Local apps
       'News_app',
   ]

**App Descriptions**:

* **django.contrib.admin**: Django admin interface for content management
* **django.contrib.auth**: User authentication system (extended by CustomUser)
* **rest_framework**: Django REST Framework for API functionality
* **rest_framework_simplejwt**: JWT authentication for API endpoints
* **News_app**: Main application containing all news-related functionality

Third-Party Package Requirements
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Install required packages via pip:

.. code-block:: bash

   pip install django>=5.2.4
   pip install djangorestframework>=3.16.0
   pip install djangorestframework-simplejwt>=5.5.1
   pip install mysqlclient>=2.2.7
   pip install Pillow>=11.3.0
   pip install python-dotenv>=1.1.1
   pip install tweepy>=4.16.0
   pip install requests>=2.32.4
   pip install oauthlib>=3.3.1
   pip install requests-oauthlib>=2.0.0

Authentication & Security
-------------------------

JWT Token Configuration
~~~~~~~~~~~~~~~~~~~~~~~

JSON Web Token settings for API authentication:

.. code-block:: python

   from datetime import timedelta
   
   SIMPLE_JWT = {
       'ACCESS_TOKEN_LIFETIME': timedelta(minutes=60),
       'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
       'ROTATE_REFRESH_TOKENS': True,
       'BLACKLIST_AFTER_ROTATION': True,
   }

**Token Lifetime Settings**:

* **Access Token**: 60 minutes (for API requests)
* **Refresh Token**: 7 days (for token renewal)
* **Token Rotation**: Enabled for security
* **Blacklisting**: Old tokens are blacklisted after rotation

**Login Redirect**:

.. code-block:: python

   LOGIN_REDIRECT_URL = '/'

Custom User Model
~~~~~~~~~~~~~~~~~

Configure Django to use the custom user model:

.. code-block:: python

   AUTH_USER_MODEL = 'News_app.CustomUser'

**Authentication Backends**:

.. code-block:: python

   AUTHENTICATION_BACKENDS = [
       'django.contrib.auth.backends.ModelBackend',
   ]

Password Validation
~~~~~~~~~~~~~~~~~~~

Password strength requirements:

.. code-block:: python

   AUTH_PASSWORD_VALIDATORS = [
       {
           'NAME': (
               'django.contrib.auth.password_validation.'
               'UserAttributeSimilarityValidator'
           ),
       },
       {
           'NAME': (
               'django.contrib.auth.password_validation.MinimumLengthValidator'
           ),
       },
       {
           'NAME': (
               'django.contrib.auth.password_validation.CommonPasswordValidator'
           ),
       },
       {
           'NAME': (
               'django.contrib.auth.password_validation.NumericPasswordValidator'
           ),
       },
   ]

Django REST Framework Configuration
-----------------------------------

DRF Settings
~~~~~~~~~~~~

Core Django REST Framework configuration:

.. code-block:: python

   REST_FRAMEWORK = {
       'DEFAULT_AUTHENTICATION_CLASSES': [
           'rest_framework.authentication.SessionAuthentication',
           'rest_framework_simplejwt.authentication.JWTAuthentication',
       ],
       'DEFAULT_PERMISSION_CLASSES': [
           'rest_framework.permissions.IsAuthenticated',
       ],
       'DEFAULT_PAGINATION_CLASS': (
           'rest_framework.pagination.PageNumberPagination'
       ),
       'PAGE_SIZE': 20,
       'DEFAULT_RENDERER_CLASSES': [
           'rest_framework.renderers.BrowsableAPIRenderer',
           'rest_framework.renderers.JSONRenderer',
       ],
   }

**Configuration Breakdown**:

* **Authentication**: Session authentication primary, JWT tokens for API
* **Permissions**: Authenticated users required by default
* **Renderers**: Browsable API for development, JSON for production
* **Pagination**: 20 items per page

API Permissions
~~~~~~~~~~~~~~~

Custom permission classes are implemented in the application:

.. code-block:: python

   # In views.py
   from rest_framework.permissions import IsAuthenticated
   from django.contrib.auth.decorators import login_required

**Role-Based Permissions**:

* **Readers**: Can view published content, comment, subscribe
* **Journalists**: Can create and manage own content
* **Editors**: Can approve/reject all content, manage all articles

CORS Configuration
~~~~~~~~~~~~~~~~~~

The application currently does not include CORS headers middleware. If you need to integrate with a frontend application running on a different domain/port, you can add CORS support:

.. code-block:: bash

   pip install django-cors-headers

Add to INSTALLED_APPS:

.. code-block:: python

   INSTALLED_APPS = [
       # ... other apps
       'corsheaders',
   ]

Add to MIDDLEWARE:

.. code-block:: python

   MIDDLEWARE = [
       'corsheaders.middleware.CorsMiddleware',
       'django.middleware.security.SecurityMiddleware',
       # ... other middleware
   ]

CORS settings for development:

.. code-block:: python

   CORS_ALLOWED_ORIGINS = [
       "http://localhost:3000",  # React development server
       "http://127.0.0.1:3000",
   ]

   # For development only
   CORS_ALLOW_ALL_ORIGINS = False  # Set to True only in development

Media & Static Files
--------------------

Static Files Configuration
~~~~~~~~~~~~~~~~~~~~~~~~~~

Configuration for CSS, JavaScript, and other static assets:

.. code-block:: python

   STATIC_URL = 'static/'
   STATIC_ROOT = BASE_DIR / 'staticfiles'

**Static Files Structure**:

.. code-block:: text

   News_app/static/news_app/
   ├── styles.css
   └── (other static files)

Media Files Configuration
~~~~~~~~~~~~~~~~~~~~~~~~~

Configuration for user-uploaded files (article images):

.. code-block:: python

   MEDIA_URL = '/media/'
   MEDIA_ROOT = BASE_DIR / 'media'

**Media Files Structure**:

.. code-block:: text

   media/
   └── article_images/
       ├── image1.jpg
       ├── image2.png
       └── (uploaded article images)

**File Upload Settings**:

The application uses Django's default file upload settings. You can customize these if needed:

.. code-block:: python

   # Maximum file size (5MB) - optional settings
   FILE_UPLOAD_MAX_MEMORY_SIZE = 5242880
   DATA_UPLOAD_MAX_MEMORY_SIZE = 5242880

   # Allowed image formats - custom validation in models/forms
   ALLOWED_IMAGE_EXTENSIONS = ['.jpg', '.jpeg', '.png', '.gif']

Middleware Configuration
------------------------

Required Middleware
~~~~~~~~~~~~~~~~~~~

Essential middleware for the application:

.. code-block:: python

   MIDDLEWARE = [
       'django.middleware.security.SecurityMiddleware',
       'django.contrib.sessions.middleware.SessionMiddleware',
       'django.middleware.common.CommonMiddleware',
       'django.middleware.csrf.CsrfViewMiddleware',
       'django.contrib.auth.middleware.AuthenticationMiddleware',
       'django.contrib.messages.middleware.MessageMiddleware',
       'django.middleware.clickjacking.XFrameOptionsMiddleware',
   ]

**Middleware Functions**:

* **SecurityMiddleware**: Basic security headers
* **SessionMiddleware**: Session handling for web interface
* **CommonMiddleware**: Common HTTP features
* **CsrfViewMiddleware**: CSRF protection
* **AuthenticationMiddleware**: User authentication
* **MessageMiddleware**: Django messages framework
* **XFrameOptionsMiddleware**: Clickjacking protection

Internationalization & Localization
------------------------------------

Language & Timezone
~~~~~~~~~~~~~~~~~~~~

Localization settings:

.. code-block:: python

   LANGUAGE_CODE = os.getenv('LANGUAGE_CODE', 'en-us')
   TIME_ZONE = os.getenv('TIME_ZONE', 'UTC')
   USE_I18N = True
   USE_TZ = True

**Timezone Considerations**:

* All timestamps stored in UTC
* Convert to local timezone in frontend/templates
* Article publication times use timezone-aware datetimes

Email Configuration
-------------------

SMTP Settings
~~~~~~~~~~~~~

The application includes email functionality using SMTP configuration. The default setup uses Mailtrap for testing:

.. code-block:: python

   EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
   EMAIL_HOST = os.getenv('EMAIL_HOST', 'sandbox.smtp.mailtrap.io')
   EMAIL_PORT = int(os.getenv('EMAIL_PORT', '2525'))
   EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER', 'your_mailtrap_user')
   EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD', 'your_mailtrap_password')
   EMAIL_USE_TLS = os.getenv('EMAIL_USE_TLS', 'True') == 'True'
   DEFAULT_FROM_EMAIL = os.getenv('DEFAULT_FROM_EMAIL', 'test@example.com')

**Email Environment Variables**:

.. code-block:: text

   EMAIL_HOST=sandbox.smtp.mailtrap.io
   EMAIL_PORT=2525
   EMAIL_HOST_USER=your_mailtrap_user
   EMAIL_HOST_PASSWORD=your_mailtrap_password
   EMAIL_USE_TLS=True
   DEFAULT_FROM_EMAIL=your-app@example.com

**Production Email Settings**:

For production, configure with your actual SMTP provider:

.. code-block:: python

   # Gmail example
   EMAIL_HOST = 'smtp.gmail.com'
   EMAIL_PORT = 587
   EMAIL_USE_TLS = True
   EMAIL_HOST_USER = 'your-email@gmail.com'
   EMAIL_HOST_PASSWORD = 'your-app-password'

Third-Party Integrations
------------------------

Twitter API Configuration
~~~~~~~~~~~~~~~~~~~~~~~~~

The application includes Twitter integration for social features. Configure Twitter API credentials:

.. code-block:: python

   TWITTER_API_KEY = os.getenv('TWITTER_API_KEY')
   TWITTER_API_SECRET = os.getenv('TWITTER_API_SECRET')
   TWITTER_ACCESS_TOKEN = os.getenv('TWITTER_ACCESS_TOKEN')
   TWITTER_ACCESS_TOKEN_SECRET = os.getenv('TWITTER_ACCESS_TOKEN_SECRET')
   TWITTER_BEARER_TOKEN = os.getenv('TWITTER_BEARER_TOKEN')
   TWITTER_ENABLED = os.getenv('TWITTER_ENABLED', 'True') == 'True'

**Twitter Environment Variables**:

.. code-block:: text

   TWITTER_API_KEY=your_twitter_api_key
   TWITTER_API_SECRET=your_twitter_api_secret
   TWITTER_ACCESS_TOKEN=your_access_token
   TWITTER_ACCESS_TOKEN_SECRET=your_access_token_secret
   TWITTER_BEARER_TOKEN=your_bearer_token
   TWITTER_ENABLED=True

**Getting Twitter API Credentials**:

1. Create a Twitter Developer account at https://developer.twitter.com/
2. Create a new Twitter App
3. Generate API keys and access tokens
4. Add credentials to your environment variables
5. Set ``TWITTER_ENABLED=False`` to disable Twitter features if needed

Logging Configuration
---------------------

Application Logging
~~~~~~~~~~~~~~~~~~~

The application does not include logging configuration by default. If you want to add logging for debugging and monitoring, you can configure it as follows:

.. code-block:: python

   LOGGING = {
       'version': 1,
       'disable_existing_loggers': False,
       'formatters': {
           'verbose': {
               'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
               'style': '{',
           },
           'simple': {
               'format': '{levelname} {message}',
               'style': '{',
           },
       },
       'handlers': {
           'file': {
               'level': 'INFO',
               'class': 'logging.FileHandler',
               'filename': 'news_app.log',
               'formatter': 'verbose',
           },
           'console': {
               'level': 'DEBUG',
               'class': 'logging.StreamHandler',
               'formatter': 'simple',
           },
       },
       'root': {
           'handlers': ['console', 'file'],
           'level': 'INFO',
       },
       'loggers': {
           'News_app': {
               'handlers': ['console', 'file'],
               'level': 'DEBUG',
               'propagate': False,
           },
       },
   }

**Log Levels**:

* **DEBUG**: Detailed debugging information
* **INFO**: General application information
* **WARNING**: Warning messages
* **ERROR**: Error conditions
* **CRITICAL**: Critical errors

Environment-Specific Configuration
-----------------------------------

Development Settings
~~~~~~~~~~~~~~~~~~~~

Settings for local development:

.. code-block:: python

   # Development-specific settings
   DEBUG = True
   ALLOWED_HOSTS = ['localhost', '127.0.0.1']
   
   # Less restrictive CORS for development
   CORS_ALLOW_ALL_ORIGINS = True
   
   # Database with local MySQL
   DATABASES = {
       'default': {
           'ENGINE': 'django.db.backends.mysql',
           'NAME': 'news_app_dev',
           'USER': 'dev_user',
           'PASSWORD': 'dev_password',
           'HOST': 'localhost',
           'PORT': '3306',
       }
   }

Production Settings
~~~~~~~~~~~~~~~~~~~

Settings for production deployment:

.. code-block:: python

   # Production-specific settings
   DEBUG = False
   ALLOWED_HOSTS = ['your-domain.com', 'www.your-domain.com']
   
   # Secure CORS settings
   CORS_ALLOWED_ORIGINS = [
       "https://your-frontend-domain.com",
   ]
   
   # Production database
   DATABASES = {
       'default': {
           'ENGINE': 'django.db.backends.mysql',
           'NAME': os.environ.get('DB_NAME'),
           'USER': os.environ.get('DB_USER'),
           'PASSWORD': os.environ.get('DB_PASSWORD'),
           'HOST': os.environ.get('DB_HOST'),
           'PORT': os.environ.get('DB_PORT', '3306'),
           'OPTIONS': {
               'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
           },
       }
   }
   
   # Security settings
   SECURE_BROWSER_XSS_FILTER = True
   SECURE_CONTENT_TYPE_NOSNIFF = True
   SECURE_HSTS_SECONDS = 31536000
   SECURE_HSTS_INCLUDE_SUBDOMAINS = True
   SECURE_HSTS_PRELOAD = True

Testing Configuration
~~~~~~~~~~~~~~~~~~~~~~

Settings for running tests:

.. code-block:: python

   # Test database (uses SQLite for speed)
   if 'test' in sys.argv:
       DATABASES = {
           'default': {
               'ENGINE': 'django.db.backends.sqlite3',
               'NAME': ':memory:',
           }
       }

URL Configuration
-----------------

Main URL Configuration
~~~~~~~~~~~~~~~~~~~~~~

The main URL configuration in `News/urls.py`:

.. code-block:: python

   from django.contrib import admin
   from django.urls import path, include
   from django.conf import settings
   from django.conf.urls.static import static
   from rest_framework_simplejwt.views import (
       TokenObtainPairView,
       TokenRefreshView,
   )

   urlpatterns = [
       path('admin/', admin.site.urls),
       path('', include('News_app.urls')),
       path('api/auth/login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
       path('api/auth/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
   ]

   # Serve media files during development
   if settings.DEBUG:
       urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

Application URL Configuration
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The News_app URL configuration includes:

* Web interface URLs (Django templates)
* API endpoints (Django REST Framework)  
* JWT authentication endpoints (login, refresh tokens)
* Media file serving (development only)

Configuration Validation
-------------------------

Settings Validation
~~~~~~~~~~~~~~~~~~~

Validate your configuration with Django's built-in checks:

.. code-block:: bash

   python manage.py check
   python manage.py check --deploy  # Production readiness check

**Common Configuration Issues**:

* Missing environment variables
* Incorrect database credentials
* CORS configuration problems
* Missing static file directories
* Incorrect media file permissions

Database Connection Testing
~~~~~~~~~~~~~~~~~~~~~~~~~~~

Test database connectivity:

.. code-block:: bash

   python manage.py dbshell  # Connect to database directly
   python manage.py migrate --dry-run  # Test migrations without applying

**Database Health Checks**:

.. code-block:: python

   # In Django shell
   from django.db import connection
   cursor = connection.cursor()
   cursor.execute("SELECT 1")
   print("Database connection successful")

Configuration Best Practices
-----------------------------

Security Best Practices
~~~~~~~~~~~~~~~~~~~~~~~~

**Environment Variables**:
- Store sensitive data in environment variables
- Use `.env` files for local development
- Never commit secrets to version control

**Secret Key Management**:
- Generate unique secret keys for each environment
- Use cryptographically secure random generation
- Rotate keys periodically in production

**Database Security**:
- Use dedicated database users with minimal privileges
- Enable SSL/TLS for database connections in production
- Regular database backups and security updates

**API Security**:
- Use HTTPS in production
- Implement rate limiting
- Validate and sanitize all inputs
- Regular security audits

Performance Optimization
~~~~~~~~~~~~~~~~~~~~~~~~

**Database Optimization**:
- Use connection pooling in production
- Implement proper indexing strategies
- Monitor query performance
- Use read replicas for high-traffic applications

**Caching Configuration**:

The application does not include caching by default. For production environments, you can add Redis caching:

.. code-block:: python

   CACHES = {
       'default': {
           'BACKEND': 'django.core.cache.backends.redis.RedisCache',
           'LOCATION': 'redis://127.0.0.1:6379/1',
       }
   }

**Static File Optimization**:
- Use CDN for static files in production
- Enable gzip compression
- Implement proper caching headers

Monitoring & Maintenance
~~~~~~~~~~~~~~~~~~~~~~~~

**Application Monitoring**:
- Implement application performance monitoring (APM)
- Set up error tracking and alerting
- Monitor database performance
- Track API usage and performance

**Regular Maintenance**:
- Keep Django and dependencies updated
- Regular security patches
- Database maintenance and optimization
- Log rotation and cleanup

Next Steps
----------

* Review the :doc:`installation` guide to set up your development environment
* Check the :doc:`models` documentation to understand the database schema
* See the :doc:`api` documentation for API endpoint configuration

**Configuration Checklist**:

1. ✅ Database configuration and connection
2. ✅ Environment variables setup
3. ✅ JWT authentication configuration
4. ✅ Static and media files configuration
5. ✅ CORS configuration for frontend
6. ✅ Security settings for production
7. ✅ Logging and monitoring setup
8. ✅ Email configuration for notifications
9. ✅ Twitter API integration setup

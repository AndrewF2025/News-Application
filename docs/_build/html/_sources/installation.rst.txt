Installation & Setup
====================

This guide will help you set up the Django News Application on your local machine for development and testing purposes.

Prerequisites
-------------

Before you begin, ensure you have the following installed:

* **Python 3.13+** (recommended)
* **Git** for version control
* **pip** (Python package installer)
* **virtualenv** or **venv** for virtual environments

Required:
* **MySQL Server** (application uses MySQL by default)

Optional but recommended:
* **VS Code** or your preferred IDE
* **MySQL Workbench** (for database management)

Installation Steps
------------------

1. Clone the Repository
~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: text

   git clone <repository-url>
   cd "News Application Project"

Or download and extract the project files to your desired location.

2. Create Virtual Environment
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: text

   python -m venv .venv

3. Activate Virtual Environment
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Windows (cmd):**

.. code-block:: text

   .venv\Scripts\activate

**Windows (PowerShell):**

.. code-block:: text

   .venv\Scripts\Activate.ps1

**Linux/Mac:**

.. code-block:: text

   source .venv/bin/activate

4. Install Dependencies
~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: text

   pip install -r requirements.txt

This will install all required packages including:
* Django 5.2.4
* Django REST Framework
* Django CORS Headers
* MySQLclient
* Pillow
* Tweepy
* Django REST Framework SimpleJWT
* python-dotenv
* And other dependencies

5. Environment Configuration
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The project includes a `.env.example` file with all necessary environment variables. 

**Copy the example file:**

.. code-block:: text

   copy .env.example .env

**Then edit the `.env` file** with your specific values:

.. code-block:: text

   # Django Settings
   SECRET_KEY=your-secret-key-here
   DEBUG=True
   ALLOWED_HOSTS=localhost,127.0.0.1

   # Database (Required - MySQL)
   DB_NAME=news_application_db
   DB_USER=root
   DB_PASSWORD=your_mysql_password
   DB_HOST=localhost
   DB_PORT=3306

   # Email Settings (Mailtrap for testing)
   EMAIL_HOST=sandbox.smtp.mailtrap.io
   EMAIL_PORT=2525
   EMAIL_HOST_USER=your_mailtrap_user
   EMAIL_HOST_PASSWORD=your_mailtrap_password
   EMAIL_USE_TLS=True
   DEFAULT_FROM_EMAIL=test@example.com

   # Twitter API (Optional)
   TWITTER_API_KEY=your_twitter_api_key
   TWITTER_API_SECRET=your_twitter_api_secret
   TWITTER_ACCESS_TOKEN=your_access_token
   TWITTER_ACCESS_TOKEN_SECRET=your_access_token_secret
   TWITTER_BEARER_TOKEN=your_bearer_token
   TWITTER_ENABLED=True

   # Localization (Optional)
   LANGUAGE_CODE=en-us
   TIME_ZONE=UTC

**Required Settings to Update:**

* **SECRET_KEY**: Generate a new Django secret key
* **DB_PASSWORD**: Your MySQL root password
* **EMAIL_HOST_USER** & **EMAIL_HOST_PASSWORD**: Your Mailtrap credentials (optional)
* **Twitter API keys**: Only if you want Twitter integration (optional)

.. note::
   You can use the application with just the database settings configured. 
   Email and Twitter settings are optional for basic functionality.

6. Database Setup
~~~~~~~~~~~~~~~~~

**Important:** This application uses a custom User model, so database setup must be done carefully.

**Install and Start MySQL:**

1. Install MySQL Server if not already installed
2. Start MySQL service
3. Create the database (see MySQL Configuration section below)

**Run Migrations:**

.. code-block:: text

   python manage.py makemigrations
   python manage.py migrate

**Create Superuser:**

.. code-block:: text

   python manage.py createsuperuser

Follow the prompts to create an admin account.

7. Collect Static Files
~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: text

   python manage.py collectstatic

8. Test the Installation
~~~~~~~~~~~~~~~~~~~~~~~~

Start the development server:

.. code-block:: text

   python manage.py runserver

Visit http://localhost:8000 to see the application running.

Database Configuration
----------------------

MySQL (Required)
~~~~~~~~~~~~~~~~

This application requires MySQL and uses a custom User model. Follow these steps:

1. **Install MySQL Server**
2. **Create Database:**

   .. code-block:: sql

      CREATE DATABASE news_application_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
      CREATE USER 'news_user'@'localhost' IDENTIFIED BY 'your_password';
      GRANT ALL PRIVILEGES ON news_application_db.* TO 'news_user'@'localhost';
      FLUSH PRIVILEGES;

   **Or use root user (for development):**

   .. code-block:: sql

      CREATE DATABASE news_application_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

3. **Update .env file** with your MySQL credentials
4. **Run migrations** as described above

.. note::
   The application uses ``CustomUser`` model from ``News_app.CustomUser``. 
   Do not run migrations until MySQL is properly configured.

Verification
------------

After installation, verify everything works:

Admin Panel
~~~~~~~~~~~

1. Go to http://localhost:8000/admin
2. Login with your superuser credentials
3. You should see the Django admin interface with News app models

API Endpoints
~~~~~~~~~~~~~

Test the API by visiting:
* http://localhost:8000/api/ - API root (DRF browsable API)
* http://localhost:8000/api/articles/ - Articles endpoint
* http://localhost:8000/api/categories/ - Categories endpoint
* http://localhost:8000/api/users/ - Users endpoint
* http://localhost:8000/api/auth/login/ - JWT token authentication

Static Files
~~~~~~~~~~~~

Verify static files are loading by checking:
* CSS styles are applied
* Admin interface looks correct

Troubleshooting
---------------

Common Issues
~~~~~~~~~~~~~

**Port 8000 already in use:**

.. code-block:: text

   python manage.py runserver 8001

**Database connection errors:**
* **Check your .env file configuration**
* **Ensure MySQL is running** (required for this application)
* **Verify database exists** (news_application_db)
* **Check MySQL credentials and permissions**

**MySQLclient installation issues:**
* **Windows**: May need Microsoft C++ Build Tools
* **Linux**: ``sudo apt-get install python3-dev default-libmysqlclient-dev build-essential``
* **macOS**: ``brew install mysql``

**Missing dependencies:**

.. code-block:: text

   pip install --upgrade -r requirements.txt

**Permission errors:**
* Ensure virtual environment is activated
* Check file permissions in project directory

**Static files not loading:**

.. code-block:: text

   python manage.py collectstatic --clear

Getting Help
~~~~~~~~~~~~

If you encounter issues:

1. Check the Django debug output in the terminal
2. Verify all environment variables are set correctly
3. Ensure all dependencies are installed
4. Check the Django documentation for specific errors

Next Steps
----------

Once installation is complete, you can:

* Explore the :doc:`api` documentation to understand available endpoints
* Review the :doc:`models` to understand the data structure
* Check :doc:`configuration` for advanced settings

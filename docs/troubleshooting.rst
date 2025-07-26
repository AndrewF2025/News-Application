Troubleshooting Guide
=====================

This guide provides solutions to common issues encountered when running the Django News Application on Windows using the built-in development server and MySQL. Only issues relevant to this setup are included.

Application Won't Start
-----------------------

**Symptoms:**
- Application window/console does not appear
- Error messages in Command Prompt or PowerShell
- No response on expected port (e.g., http://localhost:8000)

**Steps to Diagnose:**
1. Check if the Python process is running:

    - Open Task Manager (Ctrl+Shift+Esc) and look for `python.exe` or `pythonw.exe`.

2. View application logs:
   - Check the `logs` directory in your project folder (e.g., `C:\path\to\project\logs\django.log`).

3. Test Django manually:
   - Open Command Prompt, activate your virtual environment, and run:

    ::
    cd C:\path\to\project
    venv\Scripts\activate
    python manage.py runserver

**Common Causes:**
- Incorrect environment variables
- Database connection issues
- Missing dependencies
- Syntax errors in settings files

Database Connection Issues
--------------------------

**Symptoms:**
- Application cannot connect to MySQL
- Database errors in logs or console

**Steps to Diagnose:**
1. Test MySQL connection:

   - Use MySQL Workbench or run in Command Prompt:

    ::
    mysql -u newsapp_user -p news_application_prod

2. Check MySQL service status:
   - Open Services (services.msc) and ensure MySQL is running.

3. View MySQL error logs:
   - Default path: `C:\ProgramData\MySQL\MySQL Server X.X\Data\` (check for `.err` files)

**Common Causes:**
- Incorrect credentials in `.env.production`
- MySQL not running
- Firewall blocking port 3306
- Database user permissions

Static and Media Files Issues
-----------------------------

**Symptoms:**
- Images or CSS not loading
- 404 errors for static/media files

**Steps to Diagnose:**
1. Check file permissions:

   - Right-click the static/media folders, go to Properties > Security, and ensure the user running the server has Read access.

2. Confirm collectstatic ran successfully:
   - In Command Prompt:

    ::
    python manage.py collectstatic --noinput

3. Verify static and media root paths in `settings.py`

Other Common Issues
-------------------

- **Environment Variables Not Loaded:**
  - Ensure `.env.production` exists and is referenced in your settings file. On Windows, use `python-dotenv` or set variables in the system environment.
- **Email Not Sending:**
  - Check SMTP credentials and email backend settings in `settings.py`.
- **Twitter API Errors:**
  - Verify API keys and network connectivity.

Contact and Support
-------------------

If you encounter issues not covered here, consult the :doc:`installation` guide, check the application logs, and review the Sphinx documentation for further troubleshooting steps.

# News-Application

News Application project using Django

## Getting Started

### About `.env.example`

This project includes a `.env.example` file in the root directory. This file contains all the environment variables required to run the application, such as database credentials, secret keys, email settings, and API keys.

**How to use:**

- Copy `.env.example` to `.env` in the project root:
  ```sh
  cp .env.example .env
  ```
- Edit the `.env` file and fill in the required values for your local setup or production environment.
- The `.env` file is used by the Django application when running locally with venv or with Docker using `--env-file .env`.
- For Docker Compose, environment variables are set in `docker-compose.yml` and not loaded from `.env` by default.

**Never commit your `.env` file with real secrets to a public repository.**

You can run this project using either a Python virtual environment (venv) or Docker.

---

### Option 1: Using Python venv

1. **Clone the repository:**
   ```sh
   git clone https://github.com/yourusername/News-Application.git
   cd News-Application
   ```

2. **Create and activate a virtual environment:**
   ```sh
   python -m venv venv
   venv\Scripts\activate  # On Windows
   # source venv/bin/activate  # On macOS/Linux
   ```

3. **Install dependencies:**
   ```sh
   pip install -r requirements.txt
   ```

4. **Configure environment variables:**
   - Copy `.env.example` to `.env` and fill in the required values.

5. **Apply migrations:**
   ```sh
   python manage.py migrate
   ```

6. **Create a superuser (optional, for admin access):**
   ```sh
   python manage.py createsuperuser
   ```

7. **Run the development server:**
   ```sh
   python manage.py runserver
   ```

---

### Option 2: Using Docker


1. **Clone the repository:**
   ```sh
   git clone https://github.com/yourusername/News-Application.git
   cd News-Application
   ```

2. **Ensure Docker is installed and running.**

3. **Build the Docker image:**
   ```sh
   docker build -t /news-app .
   ```

4. **Edit environment variables:**
   - The Docker Compose setup uses environment variables defined directly in `docker-compose.yml` (not from `.env`).
   - If you need to change database credentials, secret keys, or API keys, edit them in the `environment:` section of the `web` and `db` services in `docker-compose.yml`.

5. **Start the app and database:**
   ```sh
   docker-compose up --build
   ```
   This will build the images (if needed), start the MySQL database, and run the Django app.

6. **Apply migrations (in a new terminal):**
   ```sh
   docker-compose exec web python manage.py migrate
   ```

7. **Create a superuser (optional, for admin access):**
   ```sh
   docker-compose exec web python manage.py createsuperuser
   ```

8. **Access the application:**
   - Open your browser to [http://localhost:8000](http://localhost:8000)

---

### Option 3: Running Docker with Docker Playground
You can use an online Docker environment such as [Play with Docker](https://labs.play-with-docker.com/) or GitHub Codespaces to run this project without installing Docker locally. **You must use Docker Compose to run both the app and the MySQL database.**

1. **Open Play with Docker:**
   - Go to [https://labs.play-with-docker.com/](https://labs.play-with-docker.com/)
   - Start a new session and create an instance.

2. **Clone the repository:**
   ```sh
   git clone https://github.com/yourusername/News-Application.git
   cd News-Application
   ```

3. **Edit environment variables:**
   - The Docker Compose setup uses environment variables defined directly in `docker-compose.yml` (not from `.env`).
   - If you need to change database credentials, secret keys, or API keys, edit them in the `environment:` section of the `web` and `db` services in `docker-compose.yml`.
   - The `.env` file is only used by Django when running locally with venv or `docker run --env-file ...`.


4. **Start and run the app and database with Docker Compose (In a Background Terminal):**
   ```sh
   docker-compose up -d --build
   ```
   This will build the images (If required) start the MySQL database, and run the Django app.

5. **Apply migrations:**
   ```sh
   docker-compose exec web python manage.py migrate
   ```

6. **Create a superuser (optional, for admin access):**
   ```sh
   docker-compose exec web python manage.py createsuperuser
   ```

7. **Access the application:**
   - Use the web preview or port forwarding feature provided by the playground to open [http://localhost:8000](http://localhost:8000) in your browser.

**Note:** Online Docker playgrounds are temporary and may have resource or time limits. For persistent development, use Docker locally or a cloud-based dev environment like GitHub Codespaces.
---

**Note:** For production, configure your environment variables and database settings securely.

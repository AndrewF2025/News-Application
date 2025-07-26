URL Routing Explanation
=======================

This document provides a comprehensive explanation of the URL routing and structure for the Django News Application. It is intended for maintainers and developers who need to understand how requests are mapped to views and APIs throughout the project.

URL Design Overview
-------------------

The News Application uses Django's URL routing system to map incoming HTTP requests to the appropriate views and API endpoints. The URL configuration is organized for clarity, maintainability, and RESTful best practices.

Core Principles:

* **Separation of Concerns**: Web views, API endpoints, and admin routes are organized in separate URL patterns and modules.
* **RESTful API Structure**: API endpoints follow REST conventions for resource access and manipulation.
* **Namespacing**: App-specific URLs are namespaced to avoid conflicts and improve reverse URL resolution.
* **Extensibility**: The URL structure is designed to be easily extended for new features or apps.

Main URL Patterns
-----------------

The main URL configuration is defined in ``News/urls.py`` and includes:

* **Admin Interface**: `/admin/` — Django admin site for managing all models
* **Authentication**: `/accounts/` — User login, logout, password management
* **News App**: `/` — Main app routes for articles, categories, publishers, newsletters, comments, and user profiles
* **API Endpoints**: `/api/` — REST API endpoints for all major resources (articles, categories, users, newsletters, publishers, comments, subscriptions)
* **Static & Media Files**: `/static/`, `/media/` — Served in development for assets and uploads

API URL Patterns
----------------

API endpoints are grouped under the `/api/` prefix and follow resource-based patterns:

* `/api/articles/` — List, create, retrieve, update, delete articles
* `/api/categories/` — List, create, retrieve, update, delete categories
* `/api/publishers/` — List, create, retrieve, update, delete publishers
* `/api/newsletters/` — List, create, retrieve, update, delete newsletters
* `/api/comments/` — List, create, retrieve, update, delete comments
* `/api/users/` — User registration, profile, and management
* `/api/auth/` — JWT authentication endpoints (login, refresh)
* `/api/subscriptions/` — Manage user subscriptions to publishers/journalists

Web View URL Patterns
---------------------

Web-facing views (HTML pages) are mapped to user-friendly routes:

* `/` — Home page (article list or dashboard)
* `/articles/<id>/` — Article detail view
* `/categories/` — Category list and detail
* `/publishers/` — Publisher list and detail
* `/newsletters/` — Newsletter list and detail
* `/profile/` — User profile and settings
* `/login/`, `/logout/`, `/register/` — Authentication views
* `/admin/` — Admin dashboard

URL Namespacing and Reverse Resolution
--------------------------------------

- App URLs are included with namespaces (e.g., ``namespace='news_app'``) for clarity and to support Django's ``reverse()`` and ``url`` template tag.
- API endpoints may use DRF's routers for automatic URL generation and viewset mapping.

Extending and Customizing URLs
------------------------------

- To add new features, define new views and add corresponding URL patterns in the appropriate ``urls.py`` file.
- Use Django's ``include()`` to modularize URL patterns for each app.
- For custom API endpoints, add routes to the DRF router or define explicit paths as needed.

Best Practices
--------------

- Keep URL patterns flat and resource-oriented for APIs.
- Use named URL patterns for maintainability and reverse lookups.
- Document custom or non-standard routes in code comments or this explanation file.
- Avoid hardcoding URLs in templates or code; use ``reverse()`` or ``url`` tags.

Summary
-------

The URL routing structure in the News Application is designed for clarity, scalability, and RESTful best practices. It supports both web and API clients, and is easily extensible for future growth.
.. Django News Application documentation master file, created by
   sphinx-quickstart on Thu Jul 24 13:12:27 2025.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Django News Application Documentation
======================================

Overview
--------

The Django News Application is a comprehensive content management system built with Django and Django REST Framework. It provides a complete platform for managing news articles, user interactions, and newsletter subscriptions.

Key Features
~~~~~~~~~~~~

**Content Management**
  * Create, edit, and manage news articles
  * Category-based article organization
  * Image handling with media management
  * Publisher and staff management system

**User System**
  * User registration and authentication
  * Profile management
  * Role-based permissions (Admin, Staff, Regular users)
  * JWT token authentication for API access

**Interactive Features**
  * Comment system for articles
  * Newsletter subscription management
  * Social media integration (Twitter)
  * Search and filtering capabilities

**API Access**
  * RESTful API endpoints
  * JSON Web Token authentication
  * Cross-origin resource sharing (CORS) support

Technology Stack
~~~~~~~~~~~~~~~~

* **Backend Framework**: Django 5.2.4
* **API Framework**: Django REST Framework 3.16.0
* **Database**: MySQL (SQLite for development)
* **Authentication**: JWT tokens + Django sessions
* **Image Processing**: Pillow 11.3.0
* **Social Integration**: Tweepy 4.16.0
* **Environment Management**: python-dotenv

Target Audience
~~~~~~~~~~~~~~~

This documentation is designed for:

* **Developers** looking to understand, modify, or extend the codebase
* **System Administrators** setting up and deploying the application
* **API Consumers** integrating with the news application's REST API
* **Content Managers** using the admin interface to manage articles and users

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   installation
   troubleshooting
   configuration
   models_explanation
   models
   api_serializers_explanation
   api_serializers
   tests_api_explanation
   tests_api
   urls_explanation
   api
   forms_explanation
   forms
   views_explanation
   views
   admin_explanation
   admin

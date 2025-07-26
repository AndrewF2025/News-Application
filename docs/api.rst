REST API Documentation
======================

This document provides comprehensive information about the Django News Application REST API. The API follows REST principles and returns JSON responses.

Base URL
--------

All API endpoints are accessible from:

.. code-block:: text

   http://localhost:8000/api/

Authentication
--------------

The API supports two authentication methods:

JWT Token Authentication (Recommended)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Primary method for API access**

1. **Obtain Token:**

   .. code-block:: text

    POST /api/auth/login/
    Content-Type: application/json

    {
    "username": "your_username",
    "password": "your_password"
    }

   **Response:**

   .. code-block:: json

    {
    "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
    }

2. **Use Token in Requests:**

   .. code-block:: text

      GET /api/articles/
      Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...

3. **Refresh Token:**

   .. code-block:: text

      POST /api/auth/refresh/
      Content-Type: application/json

      {
        "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
      }

Session Authentication
~~~~~~~~~~~~~~~~~~~~~~

**Used by the web interface**

Automatically handled when logged in through the Django admin or web interface.

User Registration
~~~~~~~~~~~~~~~~~

**Create a new user account:**

    .. code-block:: text

   POST /api/register/
   Content-Type: application/json

   {
        "username": "newuser",
        "email": "user@example.com",
        "password": "securepassword",
        "first_name": "John",
        "last_name": "Doe",
        "role": "reader"
        }

API Endpoints
-------------

Users
~~~~~

**List Users**

.. code-block:: text

   GET /api/users/

**Response:**

.. code-block:: text

   {
      "count": 25,
      "next": "http://localhost:8000/api/users/?page=2",
      "previous": null,
      "results": [
        {
            "id": 1,
            "username": "editor1",
            "email": "editor@example.com",
            "first_name": "Editor",
            "last_name": "User",
            "role": "editor"
        }
      ]
   }


**Get User Details**

.. code-block:: text

   GET /api/users/{id}/

**Create User**

.. code-block:: text

   POST /api/users/
   Content-Type: application/json
   Authorization: Bearer your-jwt-token

   {
     "username": "newuser",
     "email": "user@example.com",
     "first_name": "John",
     "last_name": "Doe",
     "role": "reader",
     "password": "securepassword"
   }

**Update User**

.. code-block:: text

   PUT /api/users/{id}/
   Content-Type: application/json
   Authorization: Bearer your-jwt-token

   {
     "first_name": "Updated First Name",
     "last_name": "Updated Last Name",
     "email": "updated@example.com"
   }

**Delete User**

.. code-block:: text

   DELETE /api/users/{id}/
   Authorization: Bearer your-jwt-token

**Get Current User Profile**

.. code-block:: text

   GET /api/users/me/
   Authorization: Bearer your-jwt-token

**Get Users by Role**

.. code-block:: text

   GET /api/users/by_role/?role=journalist
   Authorization: Bearer your-jwt-token

**Query Parameters:**
* ``role`` - Filter users by role (reader, journalist, editor)

Articles
~~~~~~~~

**List Articles**

.. code-block:: text

   GET /api/articles/

**Query Parameters:**
* ``page`` - Page number (default: 1)

**Note:** Currently, the API does not support filtering by category, publisher, or search functionality. Articles are filtered based on user role permissions:

- **Readers**: Only see published and approved articles
- **Journalists**: See their own articles + published approved articles  
- **Editors**: See all articles

**Example:**

.. code-block:: text

   GET /api/articles/?page=2

**Response:**

.. code-block:: text

   {
    "count": 50,
    "next": "http://localhost:8000/api/articles/?page=3",
    "previous": "http://localhost:8000/api/articles/?page=1",
    "results": [
        {
        "id": 1,
        "title": "Breaking News Article",
        "content": "Article content here...",
        "author": {
            "id": 2,
            "username": "journalist1",
            "first_name": "Jane",
            "last_name": "Reporter"
        },
        "category": {
          "id": 1,
          "name": "Politics",
          "description": "Political news and analysis"
        },
        "publisher": {
          "id": 1,
          "name": "Daily News",
          "description": "Local news publisher"
        },
        "image": "/media/article_images/news_image.jpg",
        "created_date": "2025-01-15T09:00:00Z",
        "published_date": "2025-01-15T10:30:00Z",
        "updated_date": "2025-01-15T10:35:00Z",
        "is_approved": true,
        "is_published": true,
        "is_independent": false
       }
       ]
    }

**Get Article Details**

.. code-block:: text

   GET /api/articles/{id}/

**Create Article**

.. code-block:: text

   POST /api/articles/
   Content-Type: multipart/form-data
   Authorization: Bearer your-jwt-token

   {
    "title": "New Article Title",
    "content": "Article content here...",
    "category": 1,
    "publisher": 1,
    "image": (binary file data),
    "is_independent": false
   }

**Update Article**

.. code-block:: text

   PUT /api/articles/{id}/
   Content-Type: application/json
   Authorization: Bearer your-jwt-token

   {
    "title": "Updated Article Title",
    "content": "Updated content...",
    "is_published": true
   }

**Delete Article**

.. code-block:: text

   DELETE /api/articles/{id}/
   Authorization: Bearer your-jwt-token

**Approve Article (Editor Only)**

.. code-block:: text

   POST /api/articles/{id}/approve/
   Authorization: Bearer your-jwt-token

**Response:**

.. code-block:: json

   {
    "message": "Article approved successfully"
   }

**Publish Article**

.. code-block:: text

   POST /api/articles/{id}/publish/
   Authorization: Bearer your-jwt-token

**Response:** Returns the updated article data with `is_published: true` and `published_date` set.

**Get My Articles**

.. code-block:: text

   GET /api/articles/my_articles/
   Authorization: Bearer your-jwt-token

**Get Pending Approval (Editor Only)**

.. code-block:: text

   GET /api/articles/pending_approval/
   Authorization: Bearer your-jwt-token

Categories
~~~~~~~~~~

**List Categories**

.. code-block:: text

   GET /api/categories/

**Response:**

.. code-block:: json

   [
    {
      "id": 1,
      "name": "Politics",
      "description": "Political news and analysis"
    },
    {
        "id": 2,
        "name": "Technology",
        "description": "Tech news and innovations"
    }
   ]

**Get Category Details**

.. code-block:: text

   GET /api/categories/{id}/

**Create Category**

.. code-block:: text

   POST /api/categories/
   Content-Type: application/json
   Authorization: Bearer your-jwt-token

   {
    "name": "Sports",
    "description": "Sports news and updates"
   }

**Update Category**

.. code-block:: text

   PUT /api/categories/{id}/
   Content-Type: application/json
   Authorization: Bearer your-jwt-token

   {
    "name": "Updated Category Name",
    "description": "Updated description"
   }

**Delete Category**

.. code-block:: text

   DELETE /api/categories/{id}/
   Authorization: Bearer your-jwt-token

Publishers
~~~~~~~~~~

**List Publishers**

.. code-block:: text

   GET /api/publishers/

**Response:**

.. code-block:: json

   [
    {
       "id": 1,
       "name": "Daily News",
       "description": "Local news publisher",
       "created_date": "2025-01-01T00:00:00Z"
    }
   ]

**Get Publisher Details**

.. code-block:: text

   GET /api/publishers/{id}/

**Create Publisher**

.. code-block:: text

   POST /api/publishers/
   Content-Type: application/json
   Authorization: Bearer your-jwt-token

   {
    "name": "New Publisher",
    "description": "Description of the new publisher"
   }

**Update Publisher**

.. code-block:: text

   PUT /api/publishers/{id}/
   Content-Type: application/json
   Authorization: Bearer your-jwt-token

   {
    "name": "Updated Publisher Name",
    "description": "Updated description"
   }

**Delete Publisher**

.. code-block:: text

   DELETE /api/publishers/{id}/
   Authorization: Bearer your-jwt-token

**Add Editor to Publisher**

.. code-block:: text

   POST /api/publishers/{id}/add_editor/
   Content-Type: application/json
   Authorization: Bearer your-jwt-token

   {
    "user_id": 5
   }

**Response:**

.. code-block:: json

   {
    "message": "Editor added successfully"
   }

**Add Journalist to Publisher**

.. code-block:: text

   POST /api/publishers/{id}/add_journalist/
   Content-Type: application/json
   Authorization: Bearer your-jwt-token

   {
    "user_id": 3
   }

**Response:**

.. code-block:: json

   {
    "message": "Journalist added successfully"
   }

Comments
~~~~~~~~

**List Comments**

.. code-block:: text

   GET /api/comments/

**Query Parameters:**
* ``article`` - Filter comments by article ID
* ``page`` - Page number (default: 1)

**Example:**

.. code-block:: text

   GET /api/comments/?article=5

**Get Comment Details**

.. code-block:: text

   GET /api/comments/{id}/

**Create Comment (via ViewSet)**

.. code-block:: text

   POST /api/comments/
   Content-Type: application/json
   Authorization: Bearer your-jwt-token

   {
    "article": 1,
    "content": "This is a great article!"
   }

**Create Comment on Article (Custom Endpoint)**

.. code-block:: text

   POST /api/articles/{article_id}/comments/create/
   Content-Type: application/json
   Authorization: Bearer your-jwt-token

   {
    "content": "This is a great article!"
   }

**Update Comment**

.. code-block:: text

   PUT /api/comments/{id}/
   Content-Type: application/json
   Authorization: Bearer your-jwt-token

   {
    "content": "Updated comment content"
   }

**Delete Comment**

.. code-block:: text

   DELETE /api/comments/{id}/
   Authorization: Bearer your-jwt-token

**Note:** Users can only edit/delete their own comments. Editors can delete any comment.

Newsletters
~~~~~~~~~~~

**List Newsletters**

.. code-block:: text

   GET /api/newsletters/

**Create Newsletter**

.. code-block:: text

   POST /api/newsletters/
   Content-Type: application/json
   Authorization: Bearer your-jwt-token

   {
    "title": "Weekly Newsletter",
    "content": "Newsletter content...",
    "publisher_id": 1
   }

**Get Newsletter Details**

.. code-block:: text

   GET /api/newsletters/{id}/

**Update Newsletter**

.. code-block:: text

   PUT /api/newsletters/{id}/
   Content-Type: application/json
   Authorization: Bearer your-jwt-token

   {
    "title": "Updated Newsletter Title",
    "content": "Updated content...",
    "is_published": true
   }

**Delete Newsletter**

.. code-block:: text

   DELETE /api/newsletters/{id}/
   Authorization: Bearer your-jwt-token

**Approve Newsletter (Editor Only)**

.. code-block:: text

   POST /api/newsletters/{id}/approve/
   Authorization: Bearer your-jwt-token

**Response:**

.. code-block:: json

   {
    "message": "Newsletter approved successfully"
   }

**Publish Newsletter**

.. code-block:: text

   POST /api/newsletters/{id}/publish/
   Authorization: Bearer your-jwt-token

**Response:** Returns the updated newsletter data with `is_published: true` and `published_date` set.

**Get My Newsletters**

.. code-block:: text

   GET /api/newsletters/my_newsletters/
   Authorization: Bearer your-jwt-token

Subscriptions
~~~~~~~~~~~~~

**List User Subscriptions**

.. code-block:: text

   GET /api/subscriptions/
   Authorization: Bearer your-jwt-token

**Create Subscription**

.. code-block:: text

   POST /api/subscriptions/create/
   Content-Type: application/json
   Authorization: Bearer your-jwt-token

   {
    "publisher": 1
   }

Or subscribe to a journalist:

.. code-block:: text

   POST /api/subscriptions/create/
   Content-Type: application/json
   Authorization: Bearer your-jwt-token

   {
    "journalist": 2
   }

**Remove Subscription**

.. code-block:: text

   POST /api/subscriptions/remove/
   Content-Type: application/json
   Authorization: Bearer your-jwt-token

   {
    "publisher": 1
   }

Or remove journalist subscription:

.. code-block:: text

   POST /api/subscriptions/remove/
   Content-Type: application/json
   Authorization: Bearer your-jwt-token

   {
    "journalist": 2
   }

**Get Subscribed Content**

.. code-block:: text

   GET /api/subscriptions/content/
   Authorization: Bearer your-jwt-token

**Get Subscribable Users**

.. code-block:: text

   GET /api/subscriptions/subscribable/
   Authorization: Bearer your-jwt-token

User Account Management
~~~~~~~~~~~~~~~~~~~~~~~

**Change Password**

.. code-block:: text

   POST /api/password/change/
   Content-Type: application/json
   Authorization: Bearer your-jwt-token

   {
     "old_password": "current_password",
     "new_password": "new_secure_password"
   }

**Reset Password**

.. code-block:: text

   POST /api/password/reset/
   Content-Type: application/json

   {
     "email": "user@example.com"
   }

Permissions and Authorization
-----------------------------

User Roles
~~~~~~~~~~

The application supports three user roles with varying permissions:

* **Editor**: Can manage all content, approve articles/newsletters, and moderate content
* **Journalist**: Can create articles and newsletters, manage their own content
* **Reader**: Can read content, comment on articles, and manage subscriptions

Endpoint Permissions
~~~~~~~~~~~~~~~~~~~~

**Public Access (No Authentication Required):**
* ``POST /api/register/`` - User registration
* ``POST /api/auth/login/`` - Obtain JWT token  
* ``POST /api/auth/refresh/`` - Refresh JWT token
* ``POST /api/password/reset/`` - Request password reset

**Note:** All other endpoints require authentication. Articles, categories, publishers, etc. require a valid JWT token or active session.

**Authenticated Users (All Roles):**
* ``GET /api/users/`` - List users (limited fields)
* ``GET /api/users/me/`` - Get current user profile
* ``GET /api/users/by_role/`` - Get users by role
* ``GET /api/articles/`` - Read articles (filtered by role)
* ``GET /api/categories/`` - Read categories
* ``GET /api/publishers/`` - Read publishers
* ``GET /api/newsletters/`` - Read newsletters (filtered by role)
* ``GET /api/comments/`` - Read comments
* ``POST /api/articles/{id}/comments/create/`` - Create comments
* ``POST /api/comments/`` - Create comments (via ViewSet)
* ``PUT /api/comments/{id}/`` - Update own comments
* ``DELETE /api/comments/{id}/`` - Delete own comments
* ``GET /api/subscriptions/`` - View own subscriptions
* ``POST /api/subscriptions/create/`` - Create subscriptions
* ``POST /api/subscriptions/remove/`` - Remove subscriptions
* ``GET /api/subscriptions/content/`` - Get subscribed content
* ``GET /api/subscriptions/subscribable/`` - Get subscribable users
* ``POST /api/password/change/`` - Change password

**Journalists:**
* ``POST /api/articles/`` - Create articles
* ``PUT/PATCH /api/articles/{id}/`` - Update own articles
* ``DELETE /api/articles/{id}/`` - Delete own articles
* ``POST /api/articles/{id}/publish/`` - Publish own articles
* ``GET /api/articles/my_articles/`` - Get own articles
* ``POST /api/newsletters/`` - Create newsletters
* ``PUT/PATCH /api/newsletters/{id}/`` - Update own newsletters
* ``POST /api/newsletters/{id}/publish/`` - Publish own newsletters  
* ``GET /api/newsletters/my_newsletters/`` - Get own newsletters

**Editors:**
* All Journalist permissions plus:
* ``PUT/PATCH /api/articles/{id}/`` - Update any article
* ``DELETE /api/articles/{id}/`` - Delete any article
* ``POST /api/articles/{id}/approve/`` - Approve articles
* ``GET /api/articles/pending_approval/`` - View pending articles
* ``POST /api/newsletters/{id}/approve/`` - Approve newsletters
* ``POST /api/categories/`` - Create categories
* ``PUT/PATCH /api/categories/{id}/`` - Update categories
* ``DELETE /api/categories/{id}/`` - Delete categories
* ``POST /api/publishers/`` - Create publishers
* ``PUT/PATCH /api/publishers/{id}/`` - Update publishers
* ``DELETE /api/publishers/{id}/`` - Delete publishers
* ``POST /api/publishers/{id}/add_editor/`` - Add editors to publishers
* ``POST /api/publishers/{id}/add_journalist/`` - Add journalists to publishers
* ``POST /api/users/`` - Create users
* ``PUT/PATCH /api/users/{id}/`` - Update users
* ``DELETE /api/users/{id}/`` - Delete users
* Content approval and moderation functions

Pagination
----------

All list endpoints support pagination with the following parameters:

* **page**: Page number (default: 1)
* **page_size**: Items per page (default: 20)

**Example Response:**

.. code-block:: text

   {
     "count": 150,
     "next": "http://localhost:8000/api/articles/?page=3",
     "previous": "http://localhost:8000/api/articles/?page=1",
     "results": [...]
   }

Error Handling
--------------

The API returns standard HTTP status codes and JSON error responses:

**Authentication Errors (401):**

.. code-block:: json

   {
     "detail": "Authentication credentials were not provided."
   }

**Permission Errors (403):**

.. code-block:: json

   {
     "detail": "You do not have permission to perform this action."
   }

**Validation Errors (400):**

.. code-block:: json

   {
     "title": ["This field is required."],
     "email": ["Enter a valid email address."]
   }

**Not Found Errors (404):**

.. code-block:: json

   {
     "detail": "Not found."
   }

Rate Limiting
-------------

The API currently does not implement rate limiting, but it's recommended for production use to prevent abuse.

CORS Support
------------

The API includes CORS (Cross-Origin Resource Sharing) support via ``django-cors-headers``, allowing web applications from different domains to access the API.

Testing the API
---------------

**Using curl:**

.. code-block:: bash

   # Get JWT token
   curl -X POST http://localhost:8000/api/auth/login/ \
     -H "Content-Type: application/json" \
     -d '{"username": "admin", "password": "password"}'

   # Use token to access protected endpoint
   curl -X GET http://localhost:8000/api/articles/ \
     -H "Authorization: Bearer YOUR_ACCESS_TOKEN"

**Using Python requests:**

.. code-block:: python

   import requests

   # Login and get token
   response = requests.post('http://localhost:8000/api/auth/login/', {
       'username': 'admin',
       'password': 'password'
   })
   token = response.json()['access']

   # Use token for API calls
   headers = {'Authorization': f'Bearer {token}'}
   articles = requests.get('http://localhost:8000/api/articles/', headers=headers)

**Browsable API:**

Visit http://localhost:8000/api/ in your browser to use Django REST Framework's browsable API interface for testing endpoints interactively.

You can also access the DRF authentication interface at http://localhost:8000/api-auth/ for session-based authentication during development.

Next Steps
----------

* Review the :doc:`models` documentation to understand the data structure
* Check :doc:`configuration` for API-specific settings
* See :doc:`installation` for setting up the development environment

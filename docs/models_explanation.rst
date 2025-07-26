Database Models Explanation
===========================

This document provides comprehensive information about the Django News Application database schema and models. The application uses a well-structured relational database design that supports role-based content management, user subscriptions, and editorial workflows.

Database Design Overview
------------------------

The News Application follows a content management system (CMS) design pattern with the following core principles:

* **Role-Based Access Control**: Users have specific roles (Reader, Journalist, Editor) with different permissions
* **Content Workflow**: Articles and newsletters require approval before publication
* **Publisher System**: Organizations can have multiple staff members creating content
* **Subscription Model**: Users can follow publishers or individual journalists
* **Content Categorization**: Articles are organized by categories for better discovery

Entity Relationship Summary
~~~~~~~~~~~~~~~~~~~~~~~~~~~

The main entities and their relationships:

* **CustomUser** - Extended user model with roles and permissions
* **Article** - Main content model with approval workflow
* **Newsletter** - Publication model with similar workflow to articles
* **Publisher** - Organization model with staff relationships
* **Category** - Content classification system
* **Comment** - User engagement and feedback system
* **Subscription** - User following system for publishers/journalists
* **PublisherStaff** - Many-to-many relationship for publisher employees

User Management Models
----------------------

CustomUser
~~~~~~~~~~

**Purpose**: Extended Django user model with role-based permissions for the news application.

**Table**: ``news_app_customuser``

**Key Features**:
- Three distinct user roles with different capabilities
- Custom permission methods for content management
- Automatic cleanup when roles change

.. code-block:: python

   class CustomUser(AbstractUser):
       ROLE_CHOICES = [
           ('reader', 'Reader'),
           ('editor', 'Editor'), 
           ('journalist', 'Journalist'),
       ]
       
       role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='reader')

**Fields**:

.. list-table::
   :header-rows: 1
   :widths: 20 15 15 50

   * - Field Name
     - Type
     - Constraints
     - Description
   * - ``username``
     - CharField
     - unique, max_length=150
     - Inherited from AbstractUser
   * - ``email``
     - EmailField
     - max_length=254
     - User's email address
   * - ``first_name``
     - CharField
     - max_length=150
     - User's first name
   * - ``last_name``
     - CharField
     - max_length=150
     - User's last name
   * - ``role``
     - CharField
     - max_length=20, choices
     - User role: reader/editor/journalist
   * - ``is_active``
     - BooleanField
     - default=True
     - Account activation status
   * - ``date_joined``
     - DateTimeField
     - auto_now_add=True
     - Account creation timestamp

**Relationships**:

* **authored_articles** (reverse FK): Articles written by this user
* **authored_newsletters** (reverse FK): Newsletters created by this user
* **approved_articles** (reverse FK): Articles approved by this editor
* **approved_newsletters** (reverse FK): Newsletters approved by this editor
* **comments** (reverse FK): Comments posted by this user
* **subscriptions** (reverse FK): User's subscriptions to publishers/journalists
* **journalist_subscriptions** (reverse FK): Subscriptions to this journalist
* **publisherstaff_set** (reverse FK): Publisher staff memberships for this user

**Custom Methods**:

* ``can_approve_articles()``: Returns True if user is an editor
* ``can_manage_content()``: Returns True if user can manage content (editors only)
* ``save()``: Custom save method that handles role-specific cleanup

**Role Descriptions**:

* **Reader**: Can read published content, comment, and subscribe to publishers/journalists
* **Journalist**: Can create articles and newsletters, publish own content
* **Editor**: Can approve/reject content, manage all articles and newsletters

PublisherStaff
~~~~~~~~~~~~~~

**Purpose**: Junction table connecting publishers with their staff members (editors and journalists).

**Table**: ``news_app_publisherstaff``

.. code-block:: python

   class PublisherStaff(models.Model):
       publisher = models.ForeignKey('Publisher', on_delete=models.CASCADE)
       user = models.ForeignKey('CustomUser', on_delete=models.CASCADE)
       role = models.CharField(max_length=20, choices=[...])
       date_joined = models.DateField(auto_now_add=True)

**Fields**:

.. list-table::
   :header-rows: 1
   :widths: 20 15 15 50

   * - Field Name
     - Type
     - Constraints
     - Description
   * - ``publisher``
     - ForeignKey
     - CASCADE
     - Publisher organization
   * - ``user``
     - ForeignKey
     - CASCADE
     - Staff member (editor/journalist)
   * - ``role``
     - CharField
     - max_length=20, choices
     - Staff role: editor/journalist
   * - ``date_joined``
     - DateField
     - auto_now_add=True
     - Date when user joined publisher

Content Models
--------------

Article
~~~~~~~

**Purpose**: Main content model representing news articles with full editorial workflow.

**Table**: ``news_app_article``

**Key Features**:
- Editorial approval workflow
- Optional publisher association
- Category classification
- Image support
- Independent article support

.. code-block:: python

   class Article(models.Model):
       title = models.CharField(max_length=200)
       content = models.TextField()
       author = models.ForeignKey(CustomUser, ...)
       publisher = models.ForeignKey(Publisher, null=True, blank=True, ...)
       category = models.ForeignKey(Category, null=True, blank=True, ...)
       # ... approval and publication fields

**Fields**:

.. list-table::
   :header-rows: 1
   :widths: 20 15 15 50

   * - Field Name
     - Type
     - Constraints
     - Description
   * - ``title``
     - CharField
     - max_length=200
     - Article headline
   * - ``content``
     - TextField
     - 
     - Main article content
   * - ``author``
     - ForeignKey
     - CASCADE, related_name='authored_articles'
     - Journalist who wrote the article
   * - ``publisher``
     - ForeignKey
     - CASCADE, related_name='articles', null=True, blank=True
     - Optional publisher organization
   * - ``category``
     - ForeignKey
     - SET_NULL, null=True, blank=True
     - Article category for classification
   * - ``created_date``
     - DateTimeField
     - auto_now_add=True
     - Article creation timestamp
   * - ``published_date``
     - DateTimeField
     - null=True, blank=True
     - Publication timestamp
   * - ``updated_date``
     - DateTimeField
     - auto_now=True
     - Last modification timestamp
   * - ``is_approved``
     - BooleanField
     - default=False
     - Editorial approval status
   * - ``approved_by``
     - ForeignKey
     - SET_NULL, null=True, limit_choices_to={'role': 'editor'}, related_name='approved_articles'
     - Editor who approved the article
   * - ``approval_date``
     - DateTimeField
     - null=True, blank=True
     - Approval timestamp
   * - ``is_published``
     - BooleanField
     - default=False
     - Publication status
   * - ``image``
     - ImageField
     - upload_to='article_images/', blank=True, null=True
     - Optional featured image
   * - ``is_independent``
     - BooleanField
     - default=False
     - Independent article (not tied to publisher)

**Relationships**:

* **author**: ForeignKey to CustomUser (journalist)
* **publisher**: ForeignKey to Publisher (optional)
* **category**: ForeignKey to Category (optional)
* **approved_by**: ForeignKey to CustomUser (editor)
* **comments** (reverse FK): Comments on this article

**Meta Options**:

* **Ordering**: ``['-created_date']`` (newest first)

Newsletter
~~~~~~~~~~

**Purpose**: Newsletter model for periodic publications with similar workflow to articles.

**Table**: ``news_app_newsletter``

**Key Features**:
- Similar approval workflow to articles
- Publisher association
- Independent newsletter support

.. code-block:: python

   class Newsletter(models.Model):
       title = models.CharField(max_length=200)
       content = models.TextField()
       author = models.ForeignKey(CustomUser, ...)
       publisher = models.ForeignKey(Publisher, null=True, blank=True, ...)
       # ... approval and publication fields

**Fields**:

.. list-table::
   :header-rows: 1
   :widths: 20 15 15 50

   * - Field Name
     - Type
     - Constraints
     - Description
   * - ``title``
     - CharField
     - max_length=200
     - Newsletter title/subject
   * - ``content``
     - TextField
     - 
     - Newsletter content
   * - ``author``
     - ForeignKey
     - CASCADE, related_name='authored_newsletters'
     - Journalist who created the newsletter
   * - ``publisher``
     - ForeignKey
     - CASCADE, related_name='newsletters', null=True, blank=True
     - Optional publisher organization
   * - ``created_date``
     - DateTimeField
     - auto_now_add=True
     - Creation timestamp
   * - ``published_date``
     - DateTimeField
     - null=True, blank=True
     - Publication timestamp
   * - ``updated_date``
     - DateTimeField
     - auto_now=True
     - Last modification timestamp
   * - ``is_approved``
     - BooleanField
     - default=False
     - Editorial approval status
   * - ``approved_by``
     - ForeignKey
     - SET_NULL, null=True, limit_choices_to={'role': 'editor'}, related_name='approved_newsletters'
     - Editor who approved the newsletter
   * - ``approval_date``
     - DateTimeField
     - null=True, blank=True
     - Approval timestamp
   * - ``is_published``
     - BooleanField
     - default=False
     - Publication status
   * - ``is_independent``
     - BooleanField
     - default=False
     - Independent newsletter

**Relationships**:

* **author**: ForeignKey to CustomUser (journalist)
* **publisher**: ForeignKey to Publisher (optional)
* **approved_by**: ForeignKey to CustomUser (editor)

**Meta Options**:

* **Ordering**: ``['-created_date']`` (newest first)

Comment
~~~~~~~

**Purpose**: User comments and engagement on articles.

**Table**: ``news_app_comment``

.. code-block:: python

   class Comment(models.Model):
       article = models.ForeignKey(Article, ...)
       author = models.ForeignKey(CustomUser, ...)
       content = models.TextField()
       created_date = models.DateTimeField(auto_now_add=True)
       updated_date = models.DateTimeField(auto_now=True)

**Fields**:

.. list-table::
   :header-rows: 1
   :widths: 20 15 15 50

   * - Field Name
     - Type
     - Constraints
     - Description
   * - ``article``
     - ForeignKey
     - CASCADE, related_name='comments'
     - Article being commented on
   * - ``author``
     - ForeignKey
     - CASCADE, related_name='comments'
     - User who posted the comment
   * - ``content``
     - TextField
     - 
     - Comment text content
   * - ``created_date``
     - DateTimeField
     - auto_now_add=True
     - Comment creation timestamp
   * - ``updated_date``
     - DateTimeField
     - auto_now=True
     - Last edit timestamp

**Relationships**:

* **article**: ForeignKey to Article
* **author**: ForeignKey to CustomUser

**Meta Options**:

* **Ordering**: ``['-created_date']`` (newest first)

Organization Models
-------------------

Publisher
~~~~~~~~~

**Purpose**: Represents news publisher organizations that employ journalists and editors.

**Table**: ``news_app_publisher``

.. code-block:: python

   class Publisher(models.Model):
       name = models.CharField(max_length=200)
       description = models.TextField(blank=True)
       created_date = models.DateTimeField(auto_now_add=True)

**Fields**:

.. list-table::
   :header-rows: 1
   :widths: 20 15 15 50

   * - Field Name
     - Type
     - Constraints
     - Description
   * - ``name``
     - CharField
     - max_length=200
     - Publisher organization name
   * - ``description``
     - TextField
     - blank=True
     - Detailed description of publisher
   * - ``created_date``
     - DateTimeField
     - auto_now_add=True
     - Publisher creation timestamp

**Relationships**:

* **articles** (reverse FK): Articles published by this organization
* **newsletters** (reverse FK): Newsletters published by this organization
* **publisherstaff_set** (reverse FK): Staff members of this publisher
* **subscription_set** (reverse FK): Subscriptions to this publisher

**Meta Options**:

* **Ordering**: ``['name']`` (alphabetical)

Category
~~~~~~~~

**Purpose**: Content classification system for organizing articles by topic.

**Table**: ``news_app_category``

.. code-block:: python

   class Category(models.Model):
       name = models.CharField(max_length=100)
       description = models.TextField(blank=True)

**Fields**:

.. list-table::
   :header-rows: 1
   :widths: 20 15 15 50

   * - Field Name
     - Type
     - Constraints
     - Description
   * - ``name``
     - CharField
     - max_length=100
     - Category name
   * - ``description``
     - TextField
     - blank=True
     - Category description

**Relationships**:

* **article_set** (reverse FK): Articles in this category

**Meta Options**:

* **Ordering**: ``['name']`` (alphabetical)
* **verbose_name_plural**: ``"Categories"``

Subscription System
-------------------

Subscription
~~~~~~~~~~~~

**Purpose**: Manages user subscriptions to publishers or individual journalists.

**Table**: ``news_app_subscription``

**Key Features**:
- Flexible subscription model (publisher OR journalist)
- Prevents duplicate subscriptions
- Supports both organizational and individual following

.. code-block:: python

   class Subscription(models.Model):
    subscriber = models.ForeignKey('CustomUser', ...)
    publisher = models.ForeignKey('Publisher', null=True, blank=True, ...)
    journalist = models.ForeignKey('CustomUser', null=True, blank=True, ...)
    # Only one of publisher or journalist should be set


**Fields**:

.. list-table::
   :header-rows: 1
   :widths: 20 15 15 50

   * - Field Name
     - Type
     - Constraints
     - Description
   * - ``subscriber``
     - ForeignKey
     - CASCADE, related_name='subscriptions'
     - User who is subscribing
   * - ``publisher``
     - ForeignKey
     - CASCADE, null=True, blank=True
     - Publisher being followed (optional)
   * - ``journalist``
     - ForeignKey
     - CASCADE, null=True, blank=True, related_name='journalist_subscriptions'
     - Journalist being followed (optional)

**Relationships**:

* **subscriber**: ForeignKey to CustomUser (the follower)
* **publisher**: ForeignKey to Publisher (optional)
* **journalist**: ForeignKey to CustomUser (optional, related_name='journalist_subscriptions')

**Business Rules**:

* Either ``publisher`` OR ``journalist`` must be set, but not both
* A user cannot subscribe to the same publisher/journalist multiple times
* Readers can subscribe to both publishers and journalists
* Journalists and editors cannot subscribe (enforced in views)

Model Relationships
-------------------

Entity Relationship Diagram
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Core Relationships**:

.. code-block:: text

   CustomUser (1) -----> (*) Article (author)
   CustomUser (1) -----> (*) Newsletter (author)
   CustomUser (1) -----> (*) Comment (author)
   CustomUser (1) -----> (*) Article (approved_by)
   CustomUser (1) -----> (*) Newsletter (approved_by)
   
   Publisher (1) -----> (*) Article
   Publisher (1) -----> (*) Newsletter
   Publisher (1) -----> (*) PublisherStaff
   
   Category (1) -----> (*) Article
   
   Article (1) -----> (*) Comment
   
   CustomUser (1) -----> (*) Subscription (subscriber)
   Publisher (1) -----> (*) Subscription (publisher)
   CustomUser (1) -----> (*) Subscription (journalist)
   
   CustomUser (1) -----> (*) PublisherStaff (user)

**Relationship Types**:

* **One-to-Many**: Most relationships are one-to-many (ForeignKey)
* **Many-to-Many**: Publisher-User relationship through PublisherStaff
* **Optional Relationships**: Articles can exist without publishers or categories
* **Self-Referencing**: Subscription model allows users to follow other users

Database Constraints and Validations
-------------------------------------

Field Constraints
~~~~~~~~~~~~~~~~~

**Not Null Constraints**:
- All primary keys and required foreign keys
- User role field (has default value)
- Article/Newsletter title and content
- Comment content

**Unique Constraints**:
- User username (inherited from AbstractUser)
- No explicit unique constraints on business fields

**Check Constraints**:
- User role must be one of: 'reader', 'editor', 'journalist'
- PublisherStaff role must be one of: 'editor', 'journalist'

**Length Constraints**:
- User role: 20 characters max
- Article/Newsletter title: 200 characters max
- Publisher name: 200 characters max
- Category name: 100 characters max

Foreign Key Constraints
~~~~~~~~~~~~~~~~~~~~~~~~

**CASCADE Deletions**:
- Deleting a user cascades to their articles, newsletters, comments
- Deleting a publisher cascades to associated articles, newsletters, staff
- Deleting an article cascades to its comments

**SET_NULL Deletions**:
- Deleting a category sets article.category to NULL
- Deleting an approving editor sets approved_by to NULL

**PROTECT Deletions**:
- No explicit PROTECT constraints (using CASCADE or SET_NULL)

Business Logic Constraints
~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Role-Based Constraints**:
- Only editors can approve articles/newsletters (limit_choices_to)
- Subscription logic prevents certain roles from subscribing
- Custom save methods enforce role-specific cleanup

**Workflow Constraints**:
- Articles/newsletters must be approved before publication
- Published content must have a published_date
- Approval requires an approving editor and approval_date

**Data Integrity**:
- Subscription model enforces publisher OR journalist (not both)
- Independent content can exist without publisher association
- Comment threads are maintained through article foreign key

Performance Considerations
--------------------------

Database Indexes
~~~~~~~~~~~~~~~~~

**Automatic Indexes**:
- Primary keys (id fields)
- Foreign key fields
- Unique fields (username)

**Recommended Custom Indexes**:

.. code-block:: sql

   -- For article queries by publication status
   CREATE INDEX idx_article_published ON news_app_article(is_published, is_approved);
   
   -- For user role-based queries
   CREATE INDEX idx_user_role ON news_app_customuser(role);
   
   -- For article date-based queries
   CREATE INDEX idx_article_dates ON news_app_article(created_date, published_date);
   
   -- For subscription lookups
   CREATE INDEX idx_subscription_lookup ON news_app_subscription(subscriber_id, publisher_id, journalist_id);

Query Optimization
~~~~~~~~~~~~~~~~~~

**Common Query Patterns**:

* **Published Articles**: Filter by ``is_published=True`` and ``is_approved=True``
* **User's Content**: Filter by ``author`` foreign key
* **Publisher Content**: Filter by ``publisher`` foreign key with staff validation
* **Category Browsing**: Join with Category model
* **Comment Threads**: Order by ``created_date`` with article grouping

**Select Related Optimization**:

.. code-block:: python

   # Efficient article queries
   Article.objects.select_related('author', 'publisher', 'category', 'approved_by')
   
   # Efficient comment queries  
   Comment.objects.select_related('author', 'article')
   
   # Efficient subscription queries
   Subscription.objects.select_related('subscriber', 'publisher', 'journalist')

Data Migration Considerations
-----------------------------

**Schema Evolution**:
- Role field added to extend Django's user model
- Independent content support added via boolean flags
- Approval workflow requires careful data migration for existing content

**Backward Compatibility**:
- Model changes maintain foreign key relationships
- Default values ensure new fields don't break existing data
- Migration scripts handle role assignment for existing users

Next Steps
----------

* Review the :doc:`api` documentation to understand how these models are exposed via REST API
* Check :doc:`configuration` for database-specific settings
* See :doc:`installation` for database setup instructions
* Explore :doc:`troubleshooting` for common database-related issues
Views Explanation
=================

This document provides a comprehensive overview of the views in the Django News Application. It explains the purpose, workflow, permissions, and design decisions behind each major view, similar to the models explanation.

View Architecture Overview
--------------------------

The application uses:
* **Function-based views** for simple logic and template rendering
* **Class-based views** for reusable, extensible logic
* **Django REST Framework API views and viewsets** for RESTful endpoints

View Categories and Responsibilities
------------------------------------

**Article Views**
~~~~~~~~~~~~~~~~~
- List, detail, create, edit, delete articles
- Approval workflow for editors
- Permissions: Only journalists can create, only editors can approve, all users can view published

**Newsletter Views**
~~~~~~~~~~~~~~~~~~~~
- Similar to articles: create, approve, publish
- Permissions: Journalists create, editors approve

**User and Publisher Management Views**
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
- Registration, login, profile edit, role assignment
- Publisher staff management (add/remove staff, assign roles)
- Permissions: Only admins/editors can manage staff

**Comment Views**
~~~~~~~~~~~~~~~~~
- Add, edit, delete comments on articles
- Permissions: Only comment authors can edit/delete

**API Views (DRF)**
~~~~~~~~~~~~~~~~~~~
- CRUD endpoints for articles, categories, users, newsletters
- JWT authentication endpoints for login and token refresh
- Permissions: Role-based, enforced via DRF permission classes

**Admin Views**
~~~~~~~~~~~~~~~
- Custom admin pages for managing users, publishers, and content
- Permissions: Superusers and editors only

Key Decorators and Mixins
-------------------------
- `@login_required`: Ensures user is authenticated
- `@role_required(role)`: Restricts access to users with a specific role
- `@editor_required`: Restricts access to editors
- Custom mixins for shared logic (pagination, permission checks)

Business Rules and Workflow Constraints
---------------------------------------
- Only editors can approve or publish content
- Only authors or editors can delete content
- Role-based redirects (e.g., superusers redirected to admin home)
- Approval required before publication

View Relationships and URL Patterns
-----------------------------------
.. list-table::
   :header-rows: 1
   :widths: 30 30 40

   * - View Name
     - URL Pattern
     - Purpose/Permissions
   * - ArticleListView
     - /articles/
     - List all published articles (all users)
   * - ArticleCreateView
     - /articles/create/
     - Create new article (journalists only)
   * - ArticleApproveView
     - /articles/<id>/approve/
     - Approve article (editors only)
   * - CommentCreateView
     - /articles/<id>/comment/
     - Add comment (authenticated users)
   * - API: ArticleViewSet
     - /api/articles/
     - CRUD for articles (role-based permissions)
   * - ... (add more as needed)
     -
     -

Extending and Customizing Views
-------------------------------
- Add new views by subclassing Django or DRF base classes
- Register new URLs in `News_app/urls.py`
- Use or extend existing permission decorators/mixins

Performance and Best Practices
------------------------------
- Use pagination for large querysets
- Use `select_related`/`prefetch_related` for related data
- Keep business logic in views thin; use services/helpers for complex logic

View Constraints and Validations
--------------------------------
- **Authentication Required**: Most views require users to be logged in; enforced via decorators or DRF permissions.
- **Role Checks**: Decorators and permission classes ensure only users with the correct role can access/modify certain resources.
- **Object Ownership**: Edit/delete actions check that the user is the owner (author) or has elevated permissions (editor/admin).
- **Form/Data Validation**: Web views use Django forms for input validation; API views use DRF serializers.
- **Approval Workflow**: Articles and newsletters must be approved before publication; enforced in both web and API views.

Permissions Matrix
------------------
.. list-table::
   :header-rows: 1
   :widths: 20 20 20 20 20

   * - View/Action
     - Reader
     - Journalist
     - Editor
     - Admin
   * - View Articles
     - ✓
     - ✓
     - ✓
     - ✓
   * - Create Article
     - ✗
     - ✓
     - ✓
     - ✓
   * - Approve Article
     - ✗
     - ✗
     - ✓
     - ✓
   * - Delete Article
     - ✗ (own comments only)
     - ✓ (own)
     - ✓
     - ✓
   * - Manage Users
     - ✗
     - ✗
     - ✗
     - ✓
   * - Manage Publisher Staff
     - ✗
     - ✗
     - ✓
     - ✓
   * - Access Admin
     - ✗
     - ✗
     - ✓
     - ✓

View Extensibility
------------------
- **Adding New Views**: Subclass Django or DRF base classes, or create new function-based views as needed.
- **Custom Decorators**: Implement new decorators for advanced permission logic.
- **Reusable Mixins**: Use mixins for shared logic (pagination, filtering, etc.).
- **API Versioning**: DRF supports versioned endpoints for backward compatibility.
- **Template Inheritance**: Web views use Django template inheritance for consistent UI.

Troubleshooting and Debugging
-----------------------------
- **Common Issues**:
  - Permission denied errors: Check user roles and decorators.
  - Object not found: Ensure correct object IDs and user ownership.
  - Validation errors: Review form/serializer error messages.
  - API authentication failures: Check JWT tokens and DRF settings.
- **Debugging Tips**:
  - Use Django debug toolbar for web views.
  - Use DRF's browsable API for testing endpoints.
  - Check logs for error traces (see logging configuration).

Next Steps
----------
- See :doc:`views` for code-level API documentation
- Review :doc:`urls_explanation` for routing details
- Check :doc:`models_explanation` for data relationships
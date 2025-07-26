Admin Interface Explanation
===========================

This document explains the design, rationale, and customizations of the Django admin interface for the News Application. It complements the API autodoc in ``admin.rst`` by providing context and best practices for maintainers and developers.

-----------------------------
Admin Architecture & Overview
-----------------------------

The Django admin is used to manage all major models in the application, with custom admin classes for each. Customizations focus on usability, filtering, and efficient data management for staff and superusers.

Key goals:
- Expose all important models for CRUD operations
- Provide clear list displays and search/filter options
- Add custom fields (e.g., user roles) to admin forms
- Protect important fields as read-only where needed

----------------------------------
Model-by-Model Admin Customization
----------------------------------

**CustomUserAdmin**
    - Extends Django's ``UserAdmin`` for the custom user model
    - Adds ``role`` to list display, filters, and forms
    - Custom fieldsets and add_fieldsets to include ``role``
    - Improves user management for different roles

**PublisherAdmin**
    - Shows publisher name and creation date
    - Searchable by name and description

**CategoryAdmin**
    - Shows category name and description
    - Searchable by name

**ArticleAdmin**
    - List display: title, author, publisher, category, approval/publish status, created date
    - Filters: approval, publish status, category, publisher, created date
    - Search: title, content, author username
    - Read-only: created/updated dates
    - Date hierarchy for quick navigation

**NewsletterAdmin**
    - List display: title, author, publisher, approval/publish status, created date
    - Filters: approval, publish status, publisher, created date
    - Search: title, content, author username
    - Read-only: created/updated dates
    - Date hierarchy for quick navigation

**CommentAdmin**
    - List display: author, article, created date
    - Filter: created date
    - Search: content, author username, article title
    - Read-only: created/updated dates

**PublisherStaffAdmin**
    - List display: publisher, user, role, date joined
    - Filters: role, publisher
    - Search: user username, publisher name

**SubscriptionAdmin**
    - List display: subscriber, publisher, journalist
    - Filters: publisher, journalist
    - Search: subscriber username, publisher name, journalist username

------------------------------
Best Practices & Extensibility
------------------------------

- Use ``list_display`` and ``list_filter`` to make admin efficient for staff
- Add ``readonly_fields`` for audit fields (created/updated)
- Use ``search_fields`` for quick lookup of related objects
- Extend admin classes for custom actions or permissions as needed
- Use ``fieldsets`` and ``add_fieldsets`` to organize complex forms

---------------
Troubleshooting
---------------

- If a model is missing from admin, ensure it is registered with ``@admin.register``
- For custom user fields, add them to ``fieldsets`` and ``add_fieldsets``
- If filters/search do not work, check field names and related lookups
- For read-only fields, ensure they are included in ``readonly_fields``

-------------
Summary Table
-------------

======================  =========================  =============================
Admin Class             Model/Class                Key Customizations
======================  =========================  =============================
CustomUserAdmin         CustomUser                 role in display/filter/forms
PublisherAdmin          Publisher                  name, created_date, search
CategoryAdmin           Category                   name, description, search
ArticleAdmin            Article                    full display, filters, search, readonly, date hierarchy
NewsletterAdmin         Newsletter                 full display, filters, search, readonly, date hierarchy
CommentAdmin            Comment                    display, filter, search, readonly
PublisherStaffAdmin     PublisherStaff             display, filter, search
SubscriptionAdmin       Subscription               display, filter, search
======================  =========================  =============================

-------------------
Extending the Admin
-------------------

To add new admin features (custom actions, permissions, inlines), subclass the relevant admin class and override methods or add attributes. For advanced use, refer to Django's admin documentation.

Forms Explanation
=================

This document provides a detailed explanation of the forms used in the News Application, their design rationale, validation logic, and best practices. It complements the API autodoc in ``forms.rst`` by offering context and guidance for developers and maintainers.

--------------
Forms Overview
--------------

The application uses Django's ``ModelForm`` and ``UserCreationForm`` to handle user input for all major models. Each form encapsulates validation, field configuration, and user experience for its domain object. Forms are designed to:

- Enforce business rules and data integrity at the input layer
- Provide clear, user-friendly field labels and help texts
- Support extensibility for custom validation and widgets

------------------------
Form-by-Form Explanation
------------------------

**CustomUserChangeForm**
    - Updates existing users (admin or profile edit)
    - Fields: username, email, first_name, last_name
    - Inherits from ``ModelForm``; can be extended for custom validation

**CustomUserCreationForm**
    - Registers new users (admin or self-registration)
    - Fields: username, email, first_name, last_name, role
    - Inherits from ``UserCreationForm``; adds ``role`` field
    - Used for both admin and user-facing registration

**PublisherForm**
    - Creates/edits publishers
    - Fields: name, description
    - Simple ``ModelForm``; can be extended for publisher-specific validation

**CategoryForm**
    - Creates/edits categories
    - Fields: name, description
    - Simple ``ModelForm``

**ArticleForm**
    - Creates/edits articles
    - Fields: title, content, publisher, category, image, is_independent
    - Handles file uploads (image)
    - Can be extended for custom clean/validation logic (e.g., image type)

**NewsletterForm**
    - Creates/edits newsletters
    - Fields: title, content, publisher, is_independent
    - Similar to ArticleForm, but for newsletters

**CommentForm**
    - Creates/edits comments
    - Field: content
    - Minimal form, but can be extended for spam filtering or moderation

**PublisherStaffForm**
    - Assigns staff to publishers
    - Fields: publisher, user, role
    - Used for publisher management workflows

**SubscriptionForm**
    - Manages subscriptions
    - Fields: subscriber, publisher, journalist
    - Used for user subscription management

--------------------------
Validation & Extensibility
--------------------------

- All forms use Django's built-in validation. Custom validation can be added via ``clean_<field>()`` or ``clean()`` methods.
- File/image fields are handled by Django's file upload system; ensure MEDIA settings are correct.
- Forms can be extended with custom widgets, help_text, and error_messages for improved UX.

--------------
Best Practices
--------------

- Always validate user input at the form level, not just in views.
- Use ``ModelForm`` for model-backed forms to reduce boilerplate and ensure consistency.
- Add custom validation for business rules that go beyond model constraints.
- Use ``help_text`` and ``label`` for user-friendly forms.

---------------
Troubleshooting
---------------

- If a form does not save, check for missing required fields or validation errors (use ``form.errors`` in views).
- For file/image uploads, verify MEDIA_ROOT and MEDIA_URL are set and the form is ``enctype='multipart/form-data'``.
- For custom user fields (like ``role``), ensure they are included in the form's ``fields`` and the model.

-------------
Summary Table
-------------

======================  =========================  =============================
Form Name               Model/Class                Key Fields
======================  =========================  =============================
CustomUserChangeForm    CustomUser                 username, email, first_name, last_name
CustomUserCreationForm  CustomUser                 username, email, first_name, last_name, role
PublisherForm           Publisher                  name, description
CategoryForm            Category                   name, description
ArticleForm             Article                    title, content, publisher, category, image, is_independent
NewsletterForm          Newsletter                 title, content, publisher, is_independent
CommentForm             Comment                    content
PublisherStaffForm      PublisherStaff             publisher, user, role
SubscriptionForm        Subscription               subscriber, publisher, journalist
======================  =========================  =============================

---------------
Extending Forms
---------------

To add new fields or validation, subclass the relevant form and override ``Meta.fields`` or add ``clean_<field>()`` methods. For advanced use, customize widgets or add JavaScript for dynamic form behavior.

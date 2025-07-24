# News_app/forms.py
from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm
from .models import (
    Publisher, Category, Article, Newsletter, Comment,
    PublisherStaff, Subscription
)

CustomUser = get_user_model()


class CustomUserChangeForm(forms.ModelForm):
    """
    Form for updating existing users.
    Inherits from Django's UserChangeForm and includes
    additional fields like role.

    :param username: Username of the user
    :param email: Email address of the user
    :param first_name: First name of the user
    :param last_name: Last name of the user
    """
    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'first_name', 'last_name')


class CustomUserCreationForm(UserCreationForm):
    """
    Form for creating new users.
    Inherits from Django's UserCreationForm and adds fields like role.
    Used for user registration and admin user creation.

    :param username: Username of the user
    :param email: Email address of the user
    :param first_name: First name of the user
    :param last_name: Last name of the user
    :param role: Role of the user
    """
    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'first_name', 'last_name', 'role')


class PublisherForm(forms.ModelForm):
    """
    Form for creating and updating Publisher instances.
    Allows input of publisher name and description.

    :param name: Name of the publisher
    :param description: Description of the publisher
    """
    class Meta:
        model = Publisher
        fields = ['name', 'description']


class CategoryForm(forms.ModelForm):
    """
    Form for creating and updating Category instances.
    Allows input of category name and description.

    :param name: Name of the category
    :param description: Description of the category
    """
    class Meta:
        model = Category
        fields = ['name', 'description']


class ArticleForm(forms.ModelForm):
    """
    Form for creating and updating Article instances.
    Includes fields for title, content, publisher, category, image,
    and independence.

    :param title: Title of the article
    :param content: Content of the article
    :param publisher: Publisher of the article
    :param category: Category of the article
    :param image: Image associated with the article
    :param is_independent: Whether the article is independent
    """
    class Meta:
        model = Article
        fields = [
            'title', 'content', 'publisher', 'category',
            'image', 'is_independent'
        ]


class NewsletterForm(forms.ModelForm):
    """
    Form for creating and updating Newsletter instances.
    Includes fields for title, content, publisher, and independence.

    :param title: Title of the newsletter
    :param content: Content of the newsletter
    :param publisher: Publisher of the newsletter
    :param is_independent: Whether the newsletter is independent
    """
    class Meta:
        model = Newsletter
        fields = [
            'title', 'content', 'publisher', 'is_independent'
        ]


class CommentForm(forms.ModelForm):
    """
    Form for creating and updating Comment instances.
    Only includes the content field for user comments.

    :param content: Content of the comment
    """
    class Meta:
        model = Comment
        fields = ['content']


class PublisherStaffForm(forms.ModelForm):
    """
    Form for assigning staff to a publisher.
    Includes fields for publisher, user, and staff role.

    :param publisher: Publisher to assign staff to
    :param user: User being assigned
    :param role: Role of the staff member
    """
    class Meta:
        model = PublisherStaff
        fields = ['publisher', 'user', 'role']


class SubscriptionForm(forms.ModelForm):
    """
    Form for managing subscriptions.
    Allows input of subscriber, publisher, and journalist fields.

    :param subscriber: User subscribing
    :param publisher: Publisher being subscribed to
    :param journalist: Journalist being followed
    """
    class Meta:
        model = Subscription
        fields = ['subscriber', 'publisher', 'journalist']

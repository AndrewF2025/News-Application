# News_app/views.py
# --------- Imports ---------
from django.views.decorators.http import require_POST, require_GET
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from rest_framework import viewsets, status
from rest_framework.views import APIView
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.contrib.auth import get_user_model, login
from django.db.models import Q
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.core.paginator import Paginator
from django.http import HttpResponseForbidden
from .models import (
    Article, Newsletter, Publisher, Category, Comment,
    Subscription, PublisherStaff, CustomUser
)
from .serializers import (
    UserSerializer,
    UserCreateSerializer,
    CategorySerializer,
    PublisherSerializer,
    ArticleSerializer,
    ArticleCreateSerializer,
    NewsletterSerializer,
    CommentSerializer,
    ArticleApprovalSerializer,
    NewsletterApprovalSerializer
)
from .forms import (
    CustomUserCreationForm,
    ArticleForm,
    PublisherForm,
    CategoryForm,
    CommentForm,
    NewsletterForm,
    CustomUserChangeForm
)
from django.utils import timezone
from .functions.twitter_service import twitter_service
from functools import wraps
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth.password_validation import validate_password


# --------- Helper Functions ---------
User = get_user_model()


# ----- Decorators -----
# Decorator to redirect superusers to admin home
def superuser_redirect(view_func):
    """
    Redirect superusers to the admin home page for template views.
    """
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        # If user is authenticated and is a superuser
        if request.user.is_authenticated and request.user.is_superuser:
            # Redirect to admin_home
            return redirect('admin_home')
        # Else, proceed with the view
        return view_func(request, *args, **kwargs)
    return _wrapped_view


# Role Required Decorator
def role_required(role):
    """
    Restrict access to users with a specific role.
    """
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            """
            Inner wrapper to enforce role-based access.
            """
            # If user is a superuser
            if request.user.is_superuser:
                # Redirect to admin_home
                return redirect('admin_home')
            # If user is not authenticated or doesn't have the required role
            if not request.user.is_authenticated or request.user.role != role:
                # Deny access
                return HttpResponseForbidden(
                    f"Only {role}s can access this page."
                )
            # Else, proceed with the view
            return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator


# Editor Required Decorator
def editor_required(view_func):
    """
    Restrict access to users who can manage content (editors).
    """
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        """
        Inner wrapper to enforce editor access.
        """
        # If user is not authenticated or cannot manage content
        if (
            not request.user.is_authenticated or
            not request.user.can_manage_content()
        ):
            # Deny access
            return HttpResponseForbidden("Only editors can access this page.")
        # Else, allow the user to proceed to the original view
        return view_func(request, *args, **kwargs)
    return _wrapped_view


# ----- Subscription Helpers -----
# Helper functions for subscriptions
def get_subscribed_publishers(user):
    """
    Return a QuerySet of publishers the user is subscribed to.
    """
    # Return publishers the user is subscribed to
    return Publisher.objects.filter(
        id__in=Subscription.objects.filter(
            subscriber=user, publisher__isnull=False
        ).values_list('publisher_id', flat=True)
    )


# Helper function to get subscribed journalists
def get_subscribed_journalists(user):
    """
    Return a QuerySet of journalists the user is subscribed to.
    """
    # Return journalists the user is subscribed to
    return CustomUser.objects.filter(
        id__in=Subscription.objects.filter(
            subscriber=user, journalist__isnull=False
        ).values_list('journalist_id', flat=True)
    )


# Helper function for admin check
def is_admin(user):
    """
    Return True if the user is authenticated and is a superuser (admin).
    """
    # Return True if user is authenticated and is a superuser
    return user.is_authenticated and user.is_superuser


# ----- Shared Content Helpers -----
# Shared function to paginate queryset
def paginate_queryset(request, queryset, per_page=10, page_param='page'):
    """
    Paginate a queryset for the given request and return the page object.
    """
    # Create paginator for the queryset
    paginator = Paginator(queryset, per_page)
    page_number = request.GET.get(page_param)
    page_obj = paginator.get_page(page_number)
    # Return the paginated page object
    return page_obj


# Shared function to get display role for user
def get_display_role(user):
    """
    Return the display role string for a user (Admin or role display).
    """
    # If user is a superuser
    if user.is_superuser:
        # Return 'Admin' as role
        return 'Admin'
    # If not, return their role display
    return user.get_role_display()


# Shared Publish Content Helper
def publish_content(request, obj, obj_type, staff_check=None):
    """
    Publish articles or newsletters, with permission checks and
    notifications.
    """
    # If user is a superuser
    if request.user.is_superuser:
        # Redirect to admin_home
        return redirect('admin_home')
    user = request.user
    # If user cannot manage content
    if not user.can_manage_content():
        # Deny access
        return HttpResponseForbidden(f"Only editors can publish {obj_type}s.")
    # If object is independent
    if hasattr(obj, 'is_independent') and obj.is_independent:
        # Any editor can publish independent articles/newsletters
        # If object is not approved
        if not obj.is_approved:
            # Show error and redirect
            messages.error(
                request,
                f"{obj_type.capitalize()} must be approved before publishing."
            )
            # Redirect to pending approvals
            return redirect('pending_approvals')
        # Else, publish the object
        obj.is_published = True
        obj.published_date = timezone.now()
        obj.save()
        # Notify subscribers (email and Twitter)
        notify_subscribers(obj, obj_type)
        messages.success(
            request,
            f"Independent {obj_type} published successfully!"
        )
        # Redirect to pending approvals
        return redirect('pending_approvals')
    # Else, object is not independent
    else:
        # Only editors who are staff of the publisher can publish
        # If staff_check is provided
        if staff_check:
            # If user is not staff for this publisher
            if not staff_check(user, obj):
                # Deny access
                return HttpResponseForbidden(
                    "You are not staff for this publisher."
                )
        # If object is not approved
        if not obj.is_approved:
            # Show error and redirect
            messages.error(
                request,
                f"{obj_type.capitalize()} must be approved before publishing."
            )
            # Redirect to pending approvals
            return redirect('pending_approvals')
        # Else, publish the object
        obj.is_published = True
        obj.published_date = timezone.now()
        obj.save()
        # Notify subscribers (email and Twitter)
        notify_subscribers(obj, obj_type)
        messages.success(
            request,
            f"{obj_type.capitalize()} published successfully!"
        )
        # Redirect to pending approvals
        return redirect('pending_approvals')


# Helper to notify subscribers via email and Twitter
def notify_subscribers(obj, obj_type):
    """
    Notify subscribers via email and Twitter when an article or
    newsletter is published.
    """
    # Get all subscriptions to the author or publisher
    emails = set()
    # If the object is an article
    if obj_type == 'article':
        # Get subscriptions for the journalist (author)
        subs = Subscription.objects.filter(journalist=obj.author)
        # If the article has a publisher
        if obj.publisher:
            # Include subscriptions for the publisher
            subs |= Subscription.objects.filter(publisher=obj.publisher)
    # Else, if the object is a newsletter
    else:
        # Get subscriptions for the journalist (author)
        subs = Subscription.objects.filter(journalist=obj.author)
        # If the newsletter has a publisher
        if obj.publisher:
            # Include subscriptions for the publisher
            subs |= Subscription.objects.filter(publisher=obj.publisher)
    # Collect unique emails from subscriptions
    for sub in subs:
        emails.add(sub.subscriber.email)
    # If there are any emails to notify
    if emails:
        # Send email notification
        subject = f"New {obj_type.capitalize()} Published: {obj.title}"
        message = (
            f"A new {obj_type} has been published by "
            f"{obj.author.get_full_name() or obj.author.username}.\n\n"
            f"Title: {obj.title}\n\n"
            "Read it now on News Application!"
        )
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            list(emails),
            fail_silently=True
        )
    # Post to Twitter using TwitterService
    try:
        # If the object is an article
        if obj_type == 'article':
            # Post a new article tweet
            twitter_service.tweet_new_article(
                title=obj.title,
                description=getattr(obj, 'description', ''),
                author_name=obj.author.get_full_name() or obj.author.username
            )
        # Else, if the object is a newsletter
        elif obj_type == 'newsletter':
            # Post a new newsletter tweet
            image_path = getattr(obj, 'image', None)
            twitter_service.tweet_new_newsletter(
                title=obj.title,
                description=getattr(obj, 'description', ''),
                author_name=obj.author.get_full_name() or obj.author.username,
                image_path=image_path
            )
    # Handle any Twitter posting errors
    except Exception as e:
        print(f"Twitter notification error: {e}")


# Shared Staff Check Helper
def staff_editor_check(user, obj):
    """
    Return True if the user is an editor staff member for the object's
    publisher.
    """
    # If user is not authenticated or does not have a publisher
    if not hasattr(obj, 'publisher') or not obj.publisher:
        # Return False
        return False
    # Get all staff IDs for the user with editor role
    staff_ids = set(PublisherStaff.objects.filter(
        user=user,
        role='editor'
    ).values_list('publisher_id', flat=True))
    # Return True if the user's publisher ID is in the staff IDs
    return obj.publisher.id in staff_ids


# Shared Approval Helper
def approve_content(request, model, obj_id, obj_type):
    """
    Approve articles or newsletters (shared logic).
    """
    # If object type is article and user cannot approve articles
    if obj_type == 'article' and not request.user.can_approve_articles():
        # Deny access
        return HttpResponseForbidden("Only editors can approve articles.")
    # If object type is newsletter and user cannot manage content
    if obj_type == 'newsletter' and not request.user.can_manage_content():
        # Deny access
        return HttpResponseForbidden("Only editors can approve newsletters.")
    # Get the object to approve
    obj = get_object_or_404(model, id=obj_id)
    obj.is_approved = True
    obj.approved_by = request.user
    obj.approval_date = timezone.now()
    obj.save()
    # If the object is approved send notifications
    messages.success(
        request,
        f'{obj_type.capitalize()} "{obj.title}" has been approved!'
    )
    # Redirect to pending approvals
    return redirect('pending_approvals')


# Shared Deletion Helper
def delete_content(request, model, obj_id, obj_type, redirect_url):
    """
    Delete articles or newsletters (shared logic).
    """
    obj = get_object_or_404(model, id=obj_id)
    # Allow deletion by editors or the journalist who created the object
    # If user is not the author and not an editor
    if request.user != obj.author and request.user.role != 'editor':
        # Deny access
        return HttpResponseForbidden(
            f"Only the author (journalist) or editors can delete {obj_type}s."
        )
    # Else, delete the object
    obj.delete()
    messages.success(request, f"{obj_type.capitalize()} deleted successfully!")
    # Then redirect to the specified URL
    return redirect(redirect_url)


# ----- Shared Comment Permission Helper -----
def can_manage_comment(user, comment):
    """
    Return True if the user can manage (edit/delete) the comment.
    """
    # If user is the author of the comment
    if user == comment.author:
        # Allow management
        return True
    # If user can manage content
    if user.can_manage_content():
        # Allow management
        return True
    # Else, deny management
    return False


# --------- Subscription Views ---------
# Subscriptions management view for readers
@login_required
@role_required('reader')
def subscriptions_view(request):
    """
    Display the user's current subscriptions to publishers and
    journalists.
    """
    # Get current subscriptions
    subscribed_publishers = get_subscribed_publishers(request.user)
    subscribed_journalists = get_subscribed_journalists(request.user)
    # Get all publishers and journalists
    all_publishers = Publisher.objects.all()
    all_journalists = CustomUser.objects.filter(role='journalist')
    context = {
        'subscribed_publishers': subscribed_publishers,
        'subscribed_journalists': subscribed_journalists,
        'all_publishers': all_publishers,
        'all_journalists': all_journalists,
    }
    # Render the subscriptions page with context
    return render(request, 'news_app/subscriptions.html', context)


# Subscribe/unsubscribe to publisher
@login_required
@require_POST
@role_required('reader')
def unsubscribe_publisher_view(request, publisher_id):
    """
    Unsubscribe the current user from a publisher.
    """
    # Get the publisher object
    publisher = get_object_or_404(Publisher, id=publisher_id)
    # If the user is subscribed to this publisher
    if Subscription.objects.filter(
        subscriber=request.user,
        publisher=publisher
    ).exists():
        # Delete the subscription
        Subscription.objects.filter(
            subscriber=request.user,
            publisher=publisher
        ).delete()
        # Show success message
        messages.success(
            request,
            f'Unsubscribed from publisher {publisher.name}!'
        )
    # Else, user was not subscribed
    else:
        # Show info message (alternative action)
        messages.info(
            request,
            f'You were not subscribed to publisher {publisher.name}.'
        )
    # Redirect to subscriptions page
    return redirect('subscriptions')


# Subscribe/unsubscribe to journalist
@login_required
@require_POST
@role_required('reader')
def subscribe_journalist_view(request, journalist_id):
    """
    Subscribe the current user to a journalist.
    """
    # Get the journalist object
    journalist = get_object_or_404(
        CustomUser,
        id=journalist_id,
        role='journalist'
    )
    # If the user is not already subscribed to this journalist
    if not Subscription.objects.filter(
        subscriber=request.user,
        journalist=journalist
    ).exists():
        # Create the subscription
        Subscription.objects.create(
            subscriber=request.user, journalist=journalist
        )
        # Show success message
        messages.success(
            request,
            f'Subscribed to journalist '
            f'{journalist.get_full_name() or journalist.username}!'
        )
    # Else, user is already subscribed
    else:
        # Show info message (alternative action)
        messages.info(
            request,
            f'You are already subscribed to journalist '
            f'{journalist.get_full_name() or journalist.username}.'
        )
    # Redirect to subscriptions page
    return redirect('subscriptions')


@login_required
@require_POST
@role_required('reader')
def unsubscribe_journalist_view(request, journalist_id):
    """
    Unsubscribe the current user from a journalist.
    """
    # Get the journalist object
    journalist = get_object_or_404(
        CustomUser,
        id=journalist_id,
        role='journalist'
    )
    # If the user is subscribed to this journalist
    if Subscription.objects.filter(
        subscriber=request.user,
        journalist=journalist
    ).exists():
        # Delete the subscription
        Subscription.objects.filter(
            subscriber=request.user,
            journalist=journalist
        ).delete()
        # Show success message
        messages.success(
            request,
            f'Unsubscribed from journalist '
            f'{journalist.get_full_name() or journalist.username}!'
        )
    # Else, user was not subscribed
    else:
        # Show info message (alternative action)
        messages.info(
            request,
            f'You were not subscribed to journalist '
            f'{journalist.get_full_name() or journalist.username}.'
        )
    # Redirect to subscriptions page
    return redirect('subscriptions')


# --------- HTML Template Views ---------

@superuser_redirect
def home_view(request):
    """
    Render the home page with latest articles, categories, and stats.
    """

    # Get latest published and approved articles
    latest_articles = Article.objects.filter(
        is_published=True, is_approved=True
    ).select_related('author', 'category').order_by('-created_date')[:6]

    # Get categories
    categories = Category.objects.all()[:6]

    # Get stats
    stats = {
        'total_articles': Article.objects.filter(
            is_published=True, is_approved=True
        ).count(),
        'total_newsletters': Newsletter.objects.filter(
            is_published=True, is_approved=True
        ).count(),
        'total_categories': Category.objects.count(),
        'total_publishers': Publisher.objects.count(),
    }

    # Render the home page with context
    # Pass latest articles, categories, and stats to the template
    context = {
        'latest_articles': latest_articles,
        'categories': categories,
        'stats': stats,
    }
    # Return the rendered home page
    return render(request, 'news_app/home.html', context)


# Admin home view for superusers
@login_required
def admin_home(request):
    """
    Render the admin home page for superusers.
    """
    # If the user is not a superuser
    if not request.user.is_superuser:
        # Redirect to home page
        return redirect('home')
    # Else, render the admin home page
    return render(request, 'news_app/admin_home.html')


@superuser_redirect
def articles_view(request):
    """
    Render the articles list view with search and category filtering.
    """
    # Get published and approved articles
    articles = Article.objects.filter(is_published=True, is_approved=True)

    # Filter by search query
    search_query = request.GET.get('search')
    # If search query is provided
    if search_query:
        # Filter articles by search query
        articles = articles.filter(
            Q(title__icontains=search_query) |
            Q(content__icontains=search_query)
        )

    # Filter by category
    category_id = request.GET.get('category')
    # If category filter is provided
    if category_id:
        # Filter articles by category
        articles = articles.filter(category_id=category_id)

    # Order and select related fields
    articles = articles.select_related(
        'author', 'category', 'publisher'
    ).order_by('-created_date')

    # Use shared pagination helper
    page_obj = paginate_queryset(request, articles, per_page=12)

    # If category_id is provided
    if category_id:
        # Set selected_category_id to string value
        selected_category_id = str(category_id)
    # If category_id is not provided
    else:
        # Set selected_category_id to empty string
        selected_category_id = ""

    # Add 'selected' attribute for each category for template
    categories = Category.objects.all()
    # For each category, set the 'selected' attribute
    for category in categories:
        # Set selected to True if this category is selected
        category.selected = str(category.id) == selected_category_id

    # Prepare context for template
    context = {
        'articles': page_obj,
        'categories': categories,
        'is_paginated': page_obj.has_other_pages(),
        'page_obj': page_obj,
        'selected_category_id': selected_category_id,
    }
    # Render the articles page with context
    return render(request, 'news_app/articles.html', context)


@superuser_redirect
def article_detail_view(request, article_id):
    """
    Render the detail view for a single article, including comments and
    related articles.
    """
    # Get the article object
    article = get_object_or_404(Article, id=article_id)

    # Check if user can view this article
    # If article is not published or not approved
    if not article.is_published or not article.is_approved:
        # If user is not authenticated
        if not request.user.is_authenticated:
            # Deny access to unauthenticated users
            return HttpResponseForbidden("This article is not available.")
        # If user is not the author and not an editor
        if (
            request.user != article.author and
            request.user.role not in ['editor']
        ):
            # Deny access to unauthorized users
            return HttpResponseForbidden("This article is not available.")

    # Get comments
    comments = Comment.objects.filter(article=article).select_related(
        'author'
    ).order_by('-created_date')

    # Get related articles (same category, excluding current)
    related_articles = Article.objects.filter(
        category=article.category,
        is_published=True,
        is_approved=True
    ).exclude(id=article.id).select_related('author')[:5]

    # Get latest articles
    latest_articles = Article.objects.filter(
        is_published=True,
        is_approved=True
    ).exclude(id=article.id).select_related('author').order_by(
        '-created_date'
    )[:5]

    # Prepare context for template
    context = {
        'article': article,
        'comments': comments,
        'related_articles': related_articles,
        'latest_articles': latest_articles,
    }
    # Render the article detail page with context
    return render(request, 'news_app/article_detail.html', context)


@login_required
def add_comment_view(request, article_id):
    """
    Allow a user to add a comment to an article.
    """
    # If user is a superuser
    if request.user.is_superuser:
        # Redirect superusers to admin home
        return redirect('admin_home')

    # Get the article object
    article = get_object_or_404(Article, id=article_id)

    # If the request method is POST
    if request.method == 'POST':
        # Bind form with POST data
        form = CommentForm(request.POST)
        # If form is valid
        if form.is_valid():
            # Create comment but don't save yet
            comment = form.save(commit=False)
            # Set article and author
            comment.article = article
            comment.author = request.user
            # Save the comment
            comment.save()
            # Show success message
            messages.success(request, 'Comment added successfully!')
            # Redirect to article detail
            return redirect('article_detail', article_id=article_id)
        # If form is not valid
        else:
            # Show error message
            messages.error(request, 'Comment content is required.')
    # If the request method is not POST
    else:
        # Create a blank form
        form = CommentForm()

    # Render the add comment page with form and article
    return render(
        request, 'news_app/add_comment.html',
        {'form': form, 'article': article}
    )


@superuser_redirect
def newsletters_view(request):
    """
    Render the newsletters list view, including independent newsletters.
    """
    # Get all published and approved newsletters
    newsletters = Newsletter.objects.filter(
        is_published=True, is_approved=True
    ).select_related('author', 'publisher').order_by('-created_date')

    # Get independent newsletters for template logic
    independent_newsletters = Newsletter.objects.filter(
        is_published=True, is_approved=True, is_independent=True
    )

    # Use shared pagination helper
    page_obj = paginate_queryset(request, newsletters, per_page=10)

    # Prepare context for template
    context = {
        'newsletters': page_obj,
        'independent_newsletters': independent_newsletters,
        'is_paginated': page_obj.has_other_pages(),
        'page_obj': page_obj,
    }
    # Render the newsletters page with context
    return render(request, 'news_app/newsletters.html', context)


@superuser_redirect
def categories_view(request):
    """
    Render the categories list view, including article counts per
    category.
    """
    # Get all categories
    categories = Category.objects.all()

    # For each category
    for category in categories:
        # Get the count of published and approved articles
        article_count = Article.objects.filter(
            category=category,
            is_published=True,
            is_approved=True
        ).count()
        # Set the article_count attribute
        category.article_count = article_count

    # Prepare context for template
    context = {
        'categories': categories,
    }
    # Render the categories page with context
    return render(request, 'news_app/categories.html', context)


@login_required
def publishers_view(request):
    """
    Render the publishers list view, with edit permissions for editors.
    """
    # If user is authenticated and is a superuser
    if request.user.is_authenticated and request.user.is_superuser:
        # Redirect to admin home
        return redirect('admin_home')
    # If user is not authenticated or does not have a valid role
    if (
        not request.user.is_authenticated or
        request.user.role not in ['editor', 'journalist', 'reader']
    ):
        # Redirect to login page
        return redirect('login')
    # Get all publishers
    publishers = Publisher.objects.all()
    # Set can_edit to True if user is an editor
    can_edit = request.user.role == 'editor'
    context = {
        'publishers': publishers,
        'can_edit': can_edit,
    }
    # Render the publishers page with context
    return render(request, 'news_app/publishers.html', context)


@login_required
@require_POST
@role_required('reader')
def subscribe_publisher_view(request, publisher_id):
    """
    Subscribe the current reader to a publisher.
    """
    # Get the publisher object
    publisher = get_object_or_404(Publisher, id=publisher_id)
    # Create the subscription if it does not exist
    Subscription.objects.get_or_create(
        subscriber=request.user,
        publisher=publisher
    )
    # Show success message
    messages.success(request, f'Subscribed to publisher {publisher.name}!')
    # Redirect to subscriptions page
    return redirect('subscriptions')


@superuser_redirect
def category_articles_view(request, category_id):
    """
    Render the articles list view for a specific category.
    """
    # Get the category object
    category = get_object_or_404(Category, id=category_id)
    # Get all published and approved articles for this category
    articles = Article.objects.filter(
        category=category,
        is_published=True,
        is_approved=True
    ).select_related('author', 'publisher').order_by('-created_date')

    # Use shared pagination helper
    page_obj = paginate_queryset(request, articles, per_page=12)

    # Prepare context for template
    context = {
        'category': category,
        'articles': page_obj,
        'is_paginated': page_obj.has_other_pages(),
        'page_obj': page_obj,
    }
    # Render the category articles page
    return render(request, 'news_app/category_articles.html', context)


# --------------------------- API ViewSets ---------------------------

class UserViewSet(viewsets.ModelViewSet):
    """
    API ViewSet for managing User objects.
    """
    # Queryset for all User objects
    queryset = User.objects.all()
    # Default serializer for User
    serializer_class = UserSerializer
    # Require authentication for all actions
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        """
        Return the appropriate serializer class based on the action.
        """
        # If action is create
        if self.action == 'create':
            # Use UserCreateSerializer for creating new users
            return UserCreateSerializer
        # Otherwise use the default UserSerializer
        return UserSerializer

    @action(detail=False, methods=['get'])
    def me(self, request):
        """
        Get current user profile
        """
        # Serialize the current user
        serializer = self.get_serializer(request.user)
        # Return the serialized data
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def by_role(self, request):
        """
        Get users by role
        """
        # Get the role from query parameters
        role = request.query_params.get('role')
        # If role is provided
        if role:
            # Filter users by the given role
            users = User.objects.filter(role=role)
            serializer = self.get_serializer(users, many=True)
            # Return the serialized data
            return Response(serializer.data)
        # If no role provided, return error
        return Response(
            {'error': 'Role parameter is required'},
            status=status.HTTP_400_BAD_REQUEST
        )


class CategoryViewSet(viewsets.ModelViewSet):
    """
    API ViewSet for managing Category objects.
    """
    # Queryset for all Category objects
    queryset = Category.objects.all()
    # Serializer for Category
    serializer_class = CategorySerializer
    # Require authentication for all actions
    permission_classes = [IsAuthenticated]


class PublisherViewSet(viewsets.ModelViewSet):
    """
    API ViewSet for managing Publisher objects, including adding editors
    and journalists.
    """
    # Queryset for all Publisher objects
    queryset = Publisher.objects.all()
    # Serializer for Publisher
    serializer_class = PublisherSerializer
    # Require authentication for all actions
    permission_classes = [IsAuthenticated]

    @action(detail=True, methods=['post'])
    def add_editor(self, request, pk=None):
        """
        Add an editor to the publisher
        """
        # Get the publisher object for this request
        publisher = self.get_object()
        # Get the user ID from request data
        user_id = request.data.get('user_id')

        try:
            # Find the user with the given ID and role 'editor'
            user = User.objects.get(id=user_id, role='editor')
            # Create a PublisherStaff entry for this user and publisher
            PublisherStaff.objects.get_or_create(
                publisher=publisher,
                user=user,
                role='editor'
            )
            # If user is successfully added, return success message
            return Response({'message': 'Editor added successfully'})
        # If user not found
        except User.DoesNotExist:
            # return error
            return Response(
                {'error': 'Editor not found'},
                status=status.HTTP_404_NOT_FOUND
            )

    @action(detail=True, methods=['post'])
    def add_journalist(self, request, pk=None):
        """
        Add a journalist to the publisher
        """
        # Get the publisher object for this request
        publisher = self.get_object()
        # Get the user ID from request data
        user_id = request.data.get('user_id')

        try:
            # Find the user with the given ID and role 'journalist'
            user = User.objects.get(id=user_id, role='journalist')
            # Create a PublisherStaff entry for this user and publisher
            PublisherStaff.objects.get_or_create(
                publisher=publisher,
                user=user,
                role='journalist'
            )
            # If user is successfully added, return success message
            return Response({'message': 'Journalist added successfully'})
        # If user not found
        except User.DoesNotExist:
            # return error
            return Response(
                {'error': 'Journalist not found'},
                status=status.HTTP_404_NOT_FOUND
            )


class ArticleViewSet(viewsets.ModelViewSet):
    """
    API ViewSet for managing Article objects, with custom actions for
    approval and publishing.
    """
    # Serializer for Article objects
    serializer_class = ArticleSerializer
    # Require authentication for all actions
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Get all articles
        queryset = Article.objects.all()
        # Filter articles based on user role
        user = self.request.user
        # If user is is a reader
        if user.role == 'reader':
            # Can only see published and approved articles
            queryset = queryset.filter(is_published=True, is_approved=True)
        # If user is a journalist
        elif user.role == 'journalist':
            # Can see their own articles + published approved articles
            queryset = queryset.filter(
                Q(author=user) |
                Q(is_published=True, is_approved=True)
            )
        # Select related fields for efficiency
        return queryset.select_related('author', 'publisher', 'category')

    def get_serializer_class(self):
        """
        Return the appropriate serializer class based on the action.
        """
        # If action is create
        if self.action == 'create':
            # Use ArticleCreateSerializer
            return ArticleCreateSerializer
        # Otherwise use the default ArticleSerializer
        return ArticleSerializer

    @action(detail=True, methods=['post'],
            permission_classes=[IsAuthenticated])
    def approve(self, request, pk=None):
        """
        Approve an article (Editor only)
        """
        # If user cannot approve articles
        if not request.user.can_approve_articles():
            # Return error response
            return Response(
                {'error': 'Only editors can approve articles'},
                status=status.HTTP_403_FORBIDDEN
            )

        # Get the article object
        article = self.get_object()
        # Use the approval serializer to set is_approved=True
        serializer = ArticleApprovalSerializer(
            article, data={'is_approved': True},
            context={'request': request}
        )
        # If serializer is valid
        if serializer.is_valid():
            serializer.save()
            # Return success message
            return Response({'message': 'Article approved successfully'})
        # Otherwise, return error response
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'])
    def publish(self, request, pk=None):
        """
        Publish an article
        """
        # Get the article object
        article = self.get_object()
        # Check permissions: only the author or editors can publish
        if ((request.user.role == 'journalist' and
             article.author != request.user) or
           (request.user.role == 'reader')):
            return Response(
                {'error': 'Permission denied'},
                status=status.HTTP_403_FORBIDDEN
            )

        # Set article as published and update published_date
        article.is_published = True
        from django.utils import timezone
        article.published_date = timezone.now()
        article.save()

        # Return the updated article data
        serializer = self.get_serializer(article)
        # Return the serialized data
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def my_articles(self, request):
        """
        Get current user's articles
        """
        # Filter articles authored by the current user
        articles = Article.objects.filter(author=request.user)
        serializer = self.get_serializer(articles, many=True)
        # Return the serialized data
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def pending_approval(self, request):
        """
        Get articles pending approval (Editor only)
        """
        # If user cannot manage content
        if not request.user.can_manage_content():
            # Return error response
            return Response(
                {'error': 'Only editors can view pending articles'},
                status=status.HTTP_403_FORBIDDEN
            )

        # Get articles that are not approved
        articles = Article.objects.filter(is_approved=False)
        serializer = self.get_serializer(articles, many=True)
        # Return the serialized data
        return Response(serializer.data)


class NewsletterViewSet(viewsets.ModelViewSet):
    """
    API ViewSet for managing Newsletter objects, with custom actions for
    approval and publishing.
    """
    # Serializer for Newsletter objects
    serializer_class = NewsletterSerializer
    # Require authentication for all actions
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Get all newsletters
        queryset = Newsletter.objects.all()
        # Filter newsletters based on user role
        user = self.request.user
        if user.role == 'reader':
            # Readers can only see published and approved newsletters
            queryset = queryset.filter(is_published=True, is_approved=True)
        elif user.role == 'journalist':
            # Journalists can see their own newsletters + published approved
            # newsletters
            queryset = queryset.filter(
                Q(author=user) |
                Q(is_published=True, is_approved=True)
            )

        # Select related fields for efficiency
        return queryset.select_related('author', 'publisher')

    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        """
        Approve a newsletter (Editor only)
        """
        # If user cannot approve newsletters
        if not request.user.can_approve_articles():
            # Return error response
            return Response(
                {'error': 'Only editors can approve newsletters'},
                status=status.HTTP_403_FORBIDDEN
            )

        # Get the newsletter object
        newsletter = self.get_object()
        # Use the approval serializer to set is_approved=True
        serializer = NewsletterApprovalSerializer(
            newsletter, data={'is_approved': True},
            context={'request': request}
        )
        # If serializer is valid
        if serializer.is_valid():
            serializer.save()
            # Return success message
            return Response({'message': 'Newsletter approved successfully'})
        # If serializer is not valid, return errors
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'])
    def publish(self, request, pk=None):
        """
        Publish a newsletter
        """
        # Get the newsletter object
        newsletter = self.get_object()

        # If user cannot publish newsletters
        if ((request.user.role == 'journalist' and
             newsletter.author != request.user) or
           (request.user.role == 'reader')):
            # Return error response
            return Response(
                {'error': 'Permission denied'},
                status=status.HTTP_403_FORBIDDEN
            )

        # Set newsletter as published and update published_date
        newsletter.is_published = True
        from django.utils import timezone
        newsletter.published_date = timezone.now()
        newsletter.save()

        # Return the updated newsletter data
        serializer = self.get_serializer(newsletter)
        # Return the serialized data
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def my_newsletters(self, request):
        """
        Get current user's newsletters
        """
        # Filter newsletters authored by the current user
        newsletters = Newsletter.objects.filter(author=request.user)
        serializer = self.get_serializer(newsletters, many=True)
        # Return the serialized data
        return Response(serializer.data)


class CommentViewSet(viewsets.ModelViewSet):
    """
    API ViewSet for managing Comment objects.
    """
    # Serializer for Comment objects
    serializer_class = CommentSerializer
    # Require authentication for all actions
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Get all comments
        queryset = Comment.objects.all()

        # Optionally filter by article ID if provided in query params
        article_id = self.request.query_params.get('article')
        # If article_id is provided
        if article_id:
            queryset = queryset.filter(article_id=article_id)
        # Return queryset filtered by article ID
        return queryset.select_related('author', 'article')

    def perform_create(self, serializer):
        # Set the author to the current user when creating a comment
        serializer.save(author=self.request.user)

    def perform_update(self, serializer):
        # If the user is not the author of the comment
        if serializer.instance.author != self.request.user:
            # Return error response
            return Response(
                {'error': 'You can only edit your own comments'},
                status=status.HTTP_403_FORBIDDEN
            )
        serializer.save()

    def perform_destroy(self, instance):
        """
        Delete a comment instance.

        Only the author or an editor can delete a comment.
        """
        # If the user is not the author or an editor
        if (instance.author != self.request.user and
                self.request.user.role != 'editor'):
            # Return error response
            return Response(
                {'error': 'Permission denied'},
                status=status.HTTP_403_FORBIDDEN
            )
        # Otherwise, delete the comment instance
        instance.delete()


# --- API Registration View ---
class RegisterAPIView(APIView):
    """
    API endpoint for registering a new user.
    Accepts JSON data: username, password, email, first_name, last_name, role.
    """
    # Allow any user to register
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = UserCreateSerializer(data=request.data)
        # If serializer is valid
        if serializer.is_valid():
            user = serializer.save()
            # Return success response with user data
            return Response({
                "message": "User registered successfully.",
                "user": UserCreateSerializer(user).data
            }, status=status.HTTP_201_CREATED)
        # Otherwise, return error response
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PasswordChangeAPIView(APIView):
    permission_classes = [IsAuthenticated]
    """
    API endpoint for changing the user's password.
    Accepts JSON data: old_password, new_password.
    """

    # Override the post method to handle password change
    def post(self, request):
        # Get the user from the request
        user = request.user
        old_password = request.data.get('old_password')
        new_password = request.data.get('new_password')

        # Check if the old password matches the user's current password
        if not user.check_password(old_password):
            # If not, return error response
            return Response(
                {"error": "Old password is incorrect."},
                status=status.HTTP_400_BAD_REQUEST
            )
        # If correct, validate the new password
        try:
            validate_password(new_password, user)
        # If it fails
        except Exception as e:
            # Return error response with validation error message
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        # If validation passes, set the new password
        user.set_password(new_password)
        user.save()
        # Return success response
        return Response({"message": "Password changed successfully."})


@api_view(['POST'])
def password_reset_api_view(request):
    """
    API endpoint to request a password reset.
    Accepts JSON data: {"email": <user_email>}
    Sends a password reset link to the user's email.
    """
    # Request user's email
    email = request.data.get('email')
    # If email is not provided
    if not email:
        # Return error response
        return Response({"error": "Email is required."},
                        status=status.HTTP_400_BAD_REQUEST)
    # If email is provided
    try:
        # Get the user by email
        user = CustomUser.objects.get(email=email)
    # If user with this email does not exist
    except CustomUser.DoesNotExist:
        # Return error response
        return Response(
            {"error": "User with this email does not exist."},
            status=status.HTTP_404_NOT_FOUND
        )
    # Generate password reset token and uid
    token = default_token_generator.make_token(user)
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    # Build password reset link (assuming frontend at /reset-password/)
    reset_link = (
        f"https://your-frontend-domain/reset-password/"
        f"{uid}/{token}/"
    )
    # Build the email content
    subject = "Password Reset Requested"
    message = (
        f"Hi {user.get_full_name() or user.username},\n\n"
        "You requested a password reset. Click the link below to reset your "
        "password:\n"
        f"{reset_link}\n\n"
        "If you did not request this, please ignore this email."
    )
    # Send the email using Django's send_mail function
    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        [email],
        fail_silently=True
    )
    # Return success response
    return Response({"message": "Password reset link sent to your email."})


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def api_subscribe(request):
    """
    API endpoint to subscribe the current user to a publisher or journalist.
    Accepts JSON: {"publisher": <publisher_id>} or
    {"journalist": <journalist_id>}
    """
    # Get publisher or journalist ID from request data
    publisher_id = request.data.get('publisher')
    journalist_id = request.data.get('journalist')
    # If publisher_id is provided
    if publisher_id:
        # Try to get the publisher object
        try:
            publisher = Publisher.objects.get(id=publisher_id)
        # If publisher with this ID does not exist
        except Publisher.DoesNotExist:
            # Return error response
            return Response(
                {"error": "Publisher not found."},
                status=status.HTTP_404_NOT_FOUND
            )
        # Otherwise, create the subscription
        sub, created = Subscription.objects.get_or_create(
            subscriber=request.user,
            publisher=publisher
        )
        # If subscription was created
        if created:
            # Return success response
            return Response({
                "message": (
                    f"Subscribed to publisher {publisher.name}."
                )
            })
        # If subscription already exists
        else:
            # Return message indicating already subscribed
            return Response({
                "message": (
                    f"Already subscribed to publisher {publisher.name}."
                )
            })
    # If journalist_id is provided
    elif journalist_id:
        # Try to get the journalist object
        try:
            journalist = CustomUser.objects.get(
                id=journalist_id,
                role='journalist'
            )
        # If journalist with this ID does not exist
        except CustomUser.DoesNotExist:
            # Return error response
            return Response(
                {"error": "Journalist not found."},
                status=status.HTTP_404_NOT_FOUND
            )
        # Otherwise, create the subscription
        sub, created = Subscription.objects.get_or_create(
            subscriber=request.user,
            journalist=journalist
        )
        # If subscription was created
        if created:
            # Return success response
            return Response({
                "message": (
                    f"Subscribed to journalist "
                    f"{journalist.get_full_name() or journalist.username}."
                )
            })
        # If subscription already exists
        else:
            # Return message indicating already subscribed
            return Response({
                "message": (
                    f"Already subscribed to journalist "
                    f"{journalist.get_full_name() or journalist.username}."
                )
            })
    # If neither publisher_id nor journalist_id is provided
    else:
        # Return error response
        return Response(
            {"error": "Publisher or Journalist ID is required."},
            status=status.HTTP_400_BAD_REQUEST
        )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def api_add_comment(request, article_id):
    """
    API endpoint to add a comment to an article.

    Accepts JSON: {"content": <comment_content>}
    """
    # Get the article ID from the URL
    content = request.data.get('content')
    # If content is not provided
    if not content:
        # Return error response
        return Response(
            {"error": "Comment content is required."},
            status=status.HTTP_400_BAD_REQUEST
        )
    # Try to get the article object
    try:
        article = Article.objects.get(id=article_id)
    # If article with this ID does not exist
    except Article.DoesNotExist:
        # Return error response
        return Response(
            {"error": "Article not found."},
            status=status.HTTP_404_NOT_FOUND
        )
    # Otherwise, create the comment
    comment = Comment.objects.create(
        article=article,
        author=request.user,
        content=content
    )
    # Return success response with comment ID
    return Response({
        "message": f"Comment added to article {article.title}.",
        "comment_id": comment.id
    }, status=status.HTTP_201_CREATED)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def api_list_subscriptions(request):
    """
    API endpoint to list all publishers and journalists the current user is
    subscribed to.

    Returns a list of publishers and journalists.
    """
    # Get subscriptions for publishers
    publisher_subs = Subscription.objects.filter(
        subscriber=request.user,
        publisher__isnull=False
    ).select_related('publisher')
    # Get subscriptions for journalists
    journalist_subs = Subscription.objects.filter(
        subscriber=request.user,
        journalist__isnull=False
    ).select_related('journalist')
    # Prepare the response data for publishers
    publishers = [
        {
            'id': sub.publisher.id,
            'name': sub.publisher.name,
            'description': sub.publisher.description
        }
        for sub in publisher_subs
    ]
    # Prepare the response data for journalists
    journalists = [
        {
            'id': sub.journalist.id,
            'username': sub.journalist.username,
            'full_name': sub.journalist.get_full_name(),
            'email': sub.journalist.email
        }
        for sub in journalist_subs
    ]
    # Return the response data list
    return Response({
        'publishers': publishers,
        'journalists': journalists
    })


# --------- Subscribable Users API ---------
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def api_subscribable_users(request):
    """
    API endpoint to get all publishers and journalists available to
    subscribe to.

    Returns: {
        'publishers': [...],
        'journalists': [...]
    }
    """
    # Get all publishers and journalists
    publishers = Publisher.objects.all()
    journalists = CustomUser.objects.filter(role='journalist')
    # Serialize the publishers data
    publisher_data = [
        {
            'id': pub.id,
            'name': pub.name,
            'description': pub.description
        }
        for pub in publishers
    ]
    # Serialize the journalists data
    journalist_data = [
        {
            'id': user.id,
            'username': user.username,
            'full_name': user.get_full_name(),
            'email': user.email
        }
        for user in journalists
    ]
    # Return the serialized data
    return Response({
        'publishers': publisher_data,
        'journalists': journalist_data
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def api_unsubscribe(request):
    """
    API endpoint to unsubscribe the current user from a publisher or
    journalist.

    Accepts JSON: {"publisher": <publisher_id>} or
    {"journalist": <journalist_id>}
    """
    # Get publisher or journalist ID from request data
    publisher_id = request.data.get('publisher')
    journalist_id = request.data.get('journalist')
    # If publisher_id is provided
    if publisher_id:
        # Try to get the publisher object
        try:
            publisher = Publisher.objects.get(id=publisher_id)
        # If publisher with this ID does not exist
        except Publisher.DoesNotExist:
            # Return error response
            return Response(
                {"error": "Publisher not found."},
                status=status.HTTP_404_NOT_FOUND
            )
        # Otherwise, delete the subscription
        deleted, _ = Subscription.objects.filter(
            subscriber=request.user,
            publisher=publisher
        ).delete()
        # If subscription was deleted
        if deleted:
            # Return success response
            return Response({
                "message": (
                    f"Unsubscribed from publisher {publisher.name}."
                )
            })
        # If subscription was not found
        else:
            # Return message indicating not subscribed
            return Response({
                "message": (
                    f"You were not subscribed to publisher {publisher.name}."
                )
            })
    # If journalist_id is provided
    elif journalist_id:
        # Try to get the journalist object
        try:
            journalist = CustomUser.objects.get(
                id=journalist_id,
                role='journalist'
            )
        # If journalist with this ID does not exist
        except CustomUser.DoesNotExist:
            # Return error response
            return Response(
                {"error": "Journalist not found."},
                status=status.HTTP_404_NOT_FOUND
            )
        # Otherwise, delete the subscription
        deleted, _ = Subscription.objects.filter(
            subscriber=request.user,
            journalist=journalist
        ).delete()
        # If subscription was deleted
        if deleted:
            # Return success response
            return Response({
                "message": (
                    f"Unsubscribed from journalist "
                    f"{journalist.get_full_name() or journalist.username}."
                )
            })
        # If subscription was not found
        else:
            # Return message indicating not subscribed
            return Response({
                "message": (
                    f"You were not subscribed to journalist "
                    f"{journalist.get_full_name() or journalist.username}."
                )
            })
    # If neither publisher_id nor journalist_id is provided
    else:
        # Return error response
        return Response(
            {"error": "Publisher or Journalist ID is required."},
            status=status.HTTP_400_BAD_REQUEST
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def api_subscribed_content(request):
    """
    API endpoint to list all newsletters and articles from authors and
    publishers that the current user is subscribed to.
    Returns: {
        'articles': [...],
        'newsletters': [...]
    }
    """
    # Get publisher and journalist subscriptions
    publishers = get_subscribed_publishers(request.user)
    journalists = get_subscribed_journalists(request.user)

    # Get articles from subscribed publishers and journalists
    articles = Article.objects.filter(
        Q(publisher__in=publishers) |
        Q(author__in=journalists)
    ).filter(
        is_published=True,
        is_approved=True
    ).select_related(
        'author', 'publisher', 'category'
    )

    # Get newsletters from subscribed publishers and journalists
    newsletters = Newsletter.objects.filter(
        Q(publisher__in=publishers) |
        Q(author__in=journalists)
    ).filter(
        is_published=True,
        is_approved=True
    ).select_related('author', 'publisher')

    # Serialize articles and newsletters
    article_data = ArticleSerializer(articles, many=True).data
    newsletter_data = NewsletterSerializer(newsletters, many=True).data

    # Return the serialized data
    return Response({
        'articles': article_data,
        'newsletters': newsletter_data
    })


# --------- Profile & Content Management Views ---------


@login_required
def profile_view(request):
    """
    Render the user profile page, including subscriptions and authored
    content.
    """
    subscribed_publishers = get_subscribed_publishers(request.user)
    subscribed_journalists = get_subscribed_journalists(request.user)
    articles = []
    newsletters = []
    display_role = get_display_role(request.user)
    # If user is a journalist, get their articles and newsletters
    if request.user.role == 'journalist':
        articles = (
            Article.objects.filter(author=request.user)
            .order_by('-created_date')
        )
        newsletters = (
            Newsletter.objects.filter(author=request.user)
            .order_by('-created_date')
        )
    pending_articles = []
    pending_newsletters = []
    # If user can manage content, filter pending articles/newsletters
    if (
        hasattr(request.user, 'can_manage_content')
        and request.user.can_manage_content
    ):
        from News_app.models import PublisherStaff
        user = request.user
        staff_publisher_ids = set(
            PublisherStaff.objects.filter(
                user=user,
                role='editor'
            ).values_list('publisher_id', flat=True)
        )
        # Filter articles the editor can approve
        articles_qs = (
            Article.objects.filter(is_published=False)
            .order_by('-created_date')
        )
        filtered_articles = []
        for article in articles_qs:
            # If article is independent and user can approve articles
            if article.is_independent and user.can_approve_articles():
                # Add to filtered_articles
                filtered_articles.append(article)
            # If article is for a publisher the user can approve
            elif (
                article.publisher_id
                and user.can_approve_articles()
                and article.publisher_id in staff_publisher_ids
            ):
                # Add to filtered_articles
                filtered_articles.append(article)
        pending_articles = filtered_articles
        # Filter newsletters the editor can approve
        newsletters_qs = (
            Newsletter.objects.filter(is_published=False)
            .order_by('-created_date')
        )
        filtered_newsletters = []
        for newsletter in newsletters_qs:
            # If newsletter is independent and user can approve articles
            if newsletter.is_independent and user.can_approve_articles():
                # Add to filtered_newsletters
                filtered_newsletters.append(newsletter)
            # If newsletter is for a publisher the user can approve
            elif (
                newsletter.publisher_id
                and user.can_approve_articles()
                and newsletter.publisher_id in staff_publisher_ids
            ):
                # Add to filtered_newsletters
                filtered_newsletters.append(newsletter)
        pending_newsletters = filtered_newsletters
    # Render the profile page with all context
    return render(
        request, 'news_app/profile.html', {
            'subscribed_publishers': subscribed_publishers,
            'subscribed_journalists': subscribed_journalists,
            'articles': articles,
            'newsletters': newsletters,
            'display_role': display_role,
            'pending_articles': pending_articles,
            'pending_newsletters': pending_newsletters,
        }
    )


def newsletter_detail_view(request, newsletter_id):
    """
    Render the detail view for a single newsletter.
    """
    # If user is authenticated and is a superuser
    if request.user.is_authenticated and request.user.is_superuser:
        # Redirect to admin home
        return redirect('admin_home')
    newsletter = get_object_or_404(Newsletter, id=newsletter_id)
    context = {
        'newsletter': newsletter,
    }
    # Render the newsletter detail page with context
    return render(request, 'news_app/newsletter_detail.html', context)


@login_required
def edit_newsletter_view(request, newsletter_id):
    """
    Allow a journalist to edit their own newsletter.
    """
    # If user is a superuser
    if request.user.is_superuser:
        # Redirect to admin home
        return redirect('admin_home')
    # Get the newsletter object
    newsletter = get_object_or_404(Newsletter, id=newsletter_id)
    # If the user is not the author of the newsletter
    if request.user != newsletter.author:
        # Deny access to editing newsletter
        return HttpResponseForbidden(
            "You do not have permission to edit this newsletter."
        )
    # If the request method is POST
    if request.method == 'POST':
        # Bind form with POST data and newsletter instance
        form = NewsletterForm(request.POST, instance=newsletter)
        # If form is valid
        if form.is_valid():
            # Save the changes
            form.save()
            # Redirect to my_newsletters
            return redirect('my_newsletters')
    # If the request method is not POST
    else:
        # Create a form with the newsletter instance
        form = NewsletterForm(instance=newsletter)
    # Render the edit newsletter page with form and newsletter
    return render(
        request,
        'news_app/create_newsletter.html',
        {
            'form': form,
            'newsletter': newsletter,
            'page_title': 'Edit Newsletter',
            'button_text': 'Save Changes',
        }
    )


def register_view(request):
    """
    Render the user registration page and handle registration logic.
    """
    # If the user is authenticated and an admin
    if request.user.is_authenticated and request.user.is_superuser:
        # Redirect to admin home
        return redirect('admin_home')
    # If the request method is POST
    if request.method == 'POST':
        # Bind form with POST data
        form = CustomUserCreationForm(request.POST)
        # If form is valid
        if form.is_valid():
            # Save the new user and log them in
            user = form.save()
            login(request, user)
            # Redirect to profile page after successful registration
            return redirect('profile')
    # If the request method is not POST
    else:
        # Create a blank registration form
        form = CustomUserCreationForm()
    # Render the registration page with the form
    return render(request, 'news_app/register.html', {'form': form})


@login_required
def my_articles_view(request):
    """
    Render the list of articles authored by the current user.
    """
    # If the user is an admin
    if request.user.is_superuser:
        # Redirect to admin home
        return redirect('admin_home')
    # Get all articles authored by the current user
    articles = Article.objects.filter(
        author=request.user
    ).order_by('-created_date')
    # Get independent articles authored by the current user
    independent_articles = articles.filter(is_independent=True)
    # Render the my articles page with articles and independent articles
    return render(
        request, 'news_app/my_articles.html', {
            'articles': articles,
            'independent_articles': independent_articles
        }
    )


@login_required
def my_newsletters_view(request):
    """
    Render the list of newsletters authored by the current user.
    """
    # If the user is an admin
    if request.user.is_superuser:
        # Redirect to admin home
        return redirect('admin_home')
    # Get all newsletters authored by the current user (not independent)
    newsletters = Newsletter.objects.filter(
        author=request.user, is_independent=False
    ).order_by('-created_date')
    # Get independent newsletters authored by the current user
    independent_newsletters = Newsletter.objects.filter(
        author=request.user, is_independent=True
    ).order_by('-created_date')
    # Render the page with newsletters and independent newsletters
    return render(
        request, 'news_app/my_newsletters.html', {
            'newsletters': newsletters,
            'independent_newsletters': independent_newsletters
        }
    )


@login_required
@editor_required
def pending_approvals_view(request):
    """
    Render the list of articles and newsletters pending approval (for
    editors).
    """
    # If the user is an admin
    if request.user.is_superuser:
        # Redirect to admin home
        return redirect('admin_home')
    # Get all unpublished articles
    articles = (
        Article.objects.filter(is_published=False)
        .order_by('-created_date')
    )
    # Get all unpublished newsletters
    newsletters = (
        Newsletter.objects.filter(is_published=False)
        .order_by('-created_date')
    )

    # Get publisher staff editor ids for current user
    user = request.user
    staff_publisher_ids = set(
        PublisherStaff.objects.filter(
            user=user,
            role='editor'
        ).values_list('publisher_id', flat=True)
    )

    # Filter articles the editor can approve
    filtered_articles = []
    for article in articles:
        # If article is independent and user can approve
        if article.is_independent and user.can_approve_articles():
            filtered_articles.append(article)
        # If article is for a publisher the user can approve
        elif (
            article.publisher_id
            and user.can_approve_articles()
            and article.publisher_id in staff_publisher_ids
        ):
            filtered_articles.append(article)

    # Filter newsletters the editor can approve
    filtered_newsletters = []
    for newsletter in newsletters:
        # If newsletter is independent and user can approve
        if newsletter.is_independent and user.can_approve_articles():
            filtered_newsletters.append(newsletter)
        # If newsletter is for a publisher the user can approve
        elif (
            newsletter.publisher_id
            and user.can_approve_articles()
            and newsletter.publisher_id in staff_publisher_ids
        ):
            filtered_newsletters.append(newsletter)

    # Render the page with filtered articles and newsletters
    return render(
        request, 'news_app/pending_approvals.html', {
            'articles': filtered_articles,
            'newsletters': filtered_newsletters
        }
    )


@login_required
def create_article_view(request):
    """
    Allow a journalist to create a new article.
    """
    # If user is Admin
    if request.user.is_superuser:
        # Redirect to admin home
        return redirect('admin_home')
    # If user is not a journalist
    if request.user.role != 'journalist':
        # Deny access to non-journalists
        return HttpResponseForbidden(
            "Only journalists can create articles."
        )
    # If request method is POST
    if request.method == 'POST':
        form = ArticleForm(request.POST, request.FILES)
        # If form is valid
        if form.is_valid():
            article = form.save(commit=False)
            article.author = request.user
            article.save()
            messages.success(request, 'Article created successfully!')
            # Redirect to my_articles after successful creation
            return redirect('my_articles')
    # If request method is not POST
    else:
        form = ArticleForm()
    # Render the create article page
    return render(request, 'news_app/create_article.html', {'form': form})


@login_required
def edit_article_view(request, article_id):
    """
    Allow a journalist to edit their own article.
    """
    # If user is Admin
    if request.user.is_superuser:
        # Redirect to admin home
        return redirect('admin_home')
    article = get_object_or_404(Article, id=article_id)
    # Only the journalist who created the article can edit
    # If user is not the author
    if request.user != article.author:
        # Deny access to editing article
        return HttpResponseForbidden(
            "You do not have permission to edit this article."
        )
    # If request method is POST
    if request.method == 'POST':
        form = ArticleForm(request.POST, request.FILES, instance=article)
        # If form is valid
        if form.is_valid():
            form.save()
            messages.success(request, 'Article updated successfully!')
            # Redirect to my_articles after successful update
            return redirect('my_articles')
    # If request method is not POST
    else:
        form = ArticleForm(instance=article)
    # Render the edit article page
    return render(
        request, 'news_app/create_article.html',
        {'form': form, 'article': article}
    )


@login_required
def create_publisher_view(request):
    """
    Allow an admin to create a new publisher.
    """
    # If user is not an Admin
    if not request.user.is_superuser:
        # Deny access to creating publishers
        return HttpResponseForbidden("Only admins can create publishers.")
    # If request method is POST
    if request.method == 'POST':
        form = PublisherForm(request.POST)
        # If form is valid
        if form.is_valid():
            form.save()
            messages.success(request, 'Publisher created successfully!')
            # Redirect to admin_publishers after successful creation
            return redirect('admin_publishers')
    # If request method is not POST
    else:
        form = PublisherForm()
    # Render the create publisher page
    return render(request, 'news_app/create_publisher.html', {'form': form})


@login_required
def edit_publisher_view(request, publisher_id):
    """
    Allow an admin to edit an existing publisher.
    """
    # If user is not an Admin
    if not request.user.is_superuser:
        # Deny access to editing publishers
        return HttpResponseForbidden("Only admins can edit publishers.")
    # Get the publisher object
    publisher = get_object_or_404(Publisher, id=publisher_id)
    # If request method is POST
    if request.method == 'POST':
        form = PublisherForm(request.POST, instance=publisher)
        # If form is valid
        if form.is_valid():
            form.save()
            messages.success(request, 'Publisher updated successfully!')
            # Redirect to admin_publishers after successful update
            return redirect('admin_publishers')
    # If request method is not POST
    else:
        form = PublisherForm(instance=publisher)
    # Render the edit publisher page
    return render(
        request, 'news_app/edit_publisher.html',
        {'form': form, 'publisher': publisher}
    )


@login_required
@editor_required
def create_category_view(request):
    """
    Allow an editor to create a new category.
    """
    # If user is an Admin
    if request.user.is_superuser:
        # Redirect to admin home
        return redirect('admin_home')
    # If request method is POST
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        # If form is valid
        if form.is_valid():
            form.save()
            messages.success(request, 'Category created successfully!')
            # Redirect to categories after successful creation
            return redirect('categories')
    # If request method is not POST
    else:
        form = CategoryForm()
    # Render the create category page
    return render(request, 'news_app/create_category.html', {'form': form})


@login_required
@editor_required
def edit_category_view(request, category_id):
    """
    Allow an editor to edit an existing category.
    """
    # If user is an Admin
    if request.user.is_superuser:
        # Redirect to admin home
        return redirect('admin_home')
    # Get the category object
    category = get_object_or_404(Category, id=category_id)
    # If request method is POST
    if request.method == 'POST':
        form = CategoryForm(request.POST, instance=category)
        # If form is valid
        if form.is_valid():
            form.save()
            messages.success(request, 'Category updated successfully!')
            # Redirect to categories after successful update
            return redirect('categories')
    # If request method is not POST
    else:
        form = CategoryForm(instance=category)
    # Render the edit category page
    return render(
        request, 'news_app/edit_category.html',
        {'form': form, 'category': category}
    )


@login_required
def edit_profile_view(request):
    """
    Allow a user to edit their profile information.
    """
    # If user is an Admin
    if request.user.is_superuser:
        # Redirect to admin home
        return redirect('admin_home')
    # If request method is POST
    if request.method == 'POST':
        form = CustomUserChangeForm(request.POST, instance=request.user)
        # If form is valid
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully!')
            # Redirect to profile after successful update
            return redirect('profile')
    # If request method is not POST
    else:
        form = CustomUserChangeForm(instance=request.user)
    # Render the edit profile page
    return render(request, 'news_app/edit_profile.html', {'form': form})


@login_required
def create_newsletter_view(request):
    """
    Allow a journalist to create a new newsletter.
    """
    # If user is Admin
    if request.user.is_superuser:
        # Redirect to admin home
        return redirect('admin_home')
    # If user is not a journalist
    if request.user.role != 'journalist':
        # Deny access to creating newsletters
        return HttpResponseForbidden(
            "Only journalists can create newsletters."
        )
    # If request method is POST
    if request.method == 'POST':
        form = NewsletterForm(request.POST)
        # If form is valid
        if form.is_valid():
            newsletter = form.save(commit=False)
            newsletter.author = request.user
            newsletter.save()
            messages.success(request, 'Newsletter created successfully!')
            # Redirect to newsletters after successful creation
            return redirect('newsletters')
    # If request method is not POST
    else:
        form = NewsletterForm()
    # Render the create newsletter page
    return render(request, 'news_app/create_newsletter.html', {'form': form})


@login_required
@editor_required
def approve_article_view(request, article_id):
    """
    Allow an editor to approve an article.
    """
    # If user is Admin
    if request.user.is_superuser:
        # Redirect to admin home
        return redirect('admin_home')
    # Approve the article
    return approve_content(request, Article, article_id, 'article')


@login_required
@editor_required
@require_POST
def approve_newsletter_view(request, newsletter_id):
    """
    Allow an editor to approve a newsletter.
    """
    # If user is Admin
    if request.user.is_superuser:
        # Redirect to admin home
        return redirect('admin_home')
    # Approve the newsletter
    return approve_content(request, Newsletter, newsletter_id, 'newsletter')


@login_required
def delete_article_view(request, article_id):
    """
    Allow an author or editor to delete an article.
    """
    # If user is Admin
    if request.user.is_superuser:
        # Redirect to admin home
        return redirect('admin_home')
    # Delete the article
    return delete_content(
        request,
        Article,
        article_id,
        'article',
        'my_articles'
    )


@login_required
def delete_newsletter_view(request, newsletter_id):
    """
    Allow an author or editor to delete a newsletter.
    """
    # If user is Admin
    if request.user.is_superuser:
        # Redirect to admin home
        return redirect('admin_home')
    # Delete the newsletter
    return delete_content(
        request,
        Newsletter,
        newsletter_id,
        'newsletter',
        'newsletters'
    )


# --------- Admin Publisher Management Views ---------

@login_required
def admin_publishers_view(request):
    """
    Render the admin view for managing all publishers.
    """
    # If user is not an Admin
    if not request.user.is_superuser:
        # Deny access.
        return HttpResponseForbidden("Admins only.")
    publishers = Publisher.objects.all()
    # For each publisher, get editor and journalist staff
    for publisher in publishers:
        publisher.editor_staff = PublisherStaff.objects.filter(
            publisher=publisher,
            role='editor'
        )
        publisher.journalist_staff = PublisherStaff.objects.filter(
            publisher=publisher,
            role='journalist'
        )
    # Render the admin publishers page
    return render(
        request,
        'news_app/admin_publishers.html',
        {'publishers': publishers}
    )


@login_required
def add_publisher_staff_view(request, publisher_id, role):
    """
    Allow an admin to add staff (editor/journalist) to a publisher.
    """
    # If user is not an Admin
    if not request.user.is_superuser:
        # Deny access
        return HttpResponseForbidden("Admins only.")
    publisher = get_object_or_404(Publisher, id=publisher_id)
    # If request method is POST
    if request.method == 'POST':
        user_id = request.POST.get('user_id')
        user = get_object_or_404(CustomUser, id=user_id, role=role)
        PublisherStaff.objects.create(
            publisher=publisher,
            user=user,
            role=role
        )
        messages.success(request, f"{role.title()} added.")
        # Redirect to admin publishers after adding staff
        return redirect('admin_publishers')
    # Get all users with the specified role
    users = CustomUser.objects.filter(role=role)
    existing_staff_ids = PublisherStaff.objects.filter(
        publisher=publisher,
        role=role
    ).values_list('user_id', flat=True)
    # Render the add publisher staff page
    return render(
        request,
        'news_app/add_publisher_staff.html',
        {
            'publisher': publisher,
            'role': role,
            'users': users,
            'existing_staff_ids': list(existing_staff_ids)
        }
    )


@login_required
def edit_publisher_staff_view(request, staff_id):
    """
    Allow an admin to edit publisher staff assignments.
    """
    # If user is not an Admin
    if not request.user.is_superuser:
        # Deny access
        return HttpResponseForbidden("Admins only.")
    staff = get_object_or_404(PublisherStaff, id=staff_id)
    # If request method is POST
    if request.method == 'POST':
        user_id = request.POST.get('user_id')
        role = request.POST.get('role')
        user = get_object_or_404(CustomUser, id=user_id, role=role)
        staff.user = user
        staff.role = role
        staff.save()
        messages.success(request, "Staff updated.")
        # Redirect to admin publishers after updating staff
        return redirect('admin_publishers')
    # Get all users with editor or journalist role
    users = CustomUser.objects.filter(role__in=['editor', 'journalist'])
    # Render the edit publisher staff page
    return render(
        request,
        'news_app/edit_publisher_staff.html',
        {
            'staff': staff,
            'users': users
        }
    )


@login_required
def delete_publisher_staff_view(request, staff_id):
    """
    Allow an admin to delete a publisher staff assignment.
    """
    # If user is not an Admin
    if not request.user.is_superuser:
        # Deny access
        return HttpResponseForbidden("Admins only.")
    staff = get_object_or_404(PublisherStaff, id=staff_id)
    # Delete staff assignment
    staff.delete()
    messages.success(request, "Staff deleted.")
    # Redirect to admin publishers
    return redirect('admin_publishers')


@login_required
@user_passes_test(is_admin)
@require_POST
def delete_publisher_view(request, publisher_id):
    """
    Allow an admin to delete a publisher.
    """
    # Get the publisher object
    publisher = get_object_or_404(Publisher, id=publisher_id)
    # Delete publisher
    publisher.delete()
    # Redirect to admin publishers
    return redirect('admin_publishers')


# View publisher staff details (admin only)
@login_required
@require_GET
def view_publisher_staff_view(request, staff_id):
    """
    Render the detail view for a publisher staff assignment (admin only).
    """
    # If user is not an Admin
    if not request.user.is_superuser:
        # Deny access
        return HttpResponseForbidden("Admins only.")
    staff = get_object_or_404(PublisherStaff, id=staff_id)
    # Render the staff detail page
    return render(
        request,
        'news_app/view_publisher_staff.html',
        {'staff': staff}
    )


# Admin: Manage Users view (basic, for navigation)
@login_required
def admin_users_view(request):
    """
    Render the admin view for managing all users.
    """
    # If user is not an Admin
    if not request.user.is_superuser:
        # Deny access
        return HttpResponseForbidden("Admins only.")
    users = CustomUser.objects.all()
    # Set display role for each user
    for user in users:
        user.display_role = get_display_role(user)
    # Render the admin users page
    return render(request, 'news_app/admin_users.html', {'users': users})


# --------- Admin User Management Views ---------
@login_required
def view_user(request, user_id):
    """
    Render the detail view for a user (admin only).
    """
    # If user is not an Admin
    if not request.user.is_superuser:
        # Deny access
        return HttpResponseForbidden("Admins only.")
    user = get_object_or_404(get_user_model(), id=user_id)
    # Set display role for user
    user.display_role = get_display_role(user)
    # Render the user detail page
    return render(request, 'news_app/view_user.html', {'user': user})


@login_required
def edit_user(request, user_id):
    """
    Allow an admin to edit a user's information.
    """
    # If user is not an Admin
    if not request.user.is_superuser:
        # Deny access
        return HttpResponseForbidden("Admins only.")
    user = get_object_or_404(get_user_model(), id=user_id)
    # If request method is POST
    if request.method == 'POST':
        form = CustomUserChangeForm(request.POST, instance=user)
        # If form is valid
        if form.is_valid():
            form.save()
            messages.success(request, 'User updated successfully!')
            # Redirect to admin_users after successful update
            return redirect('admin_users')
    # If request method is not POST
    else:
        form = CustomUserChangeForm(instance=user)
    # Render the edit user page
    return render(
        request,
        'news_app/edit_user.html',
        {'form': form, 'user': user}
    )


@login_required
def delete_user(request, user_id):
    """
    Allow an admin to delete a user.
    """
    # If user is not an Admin
    if not request.user.is_superuser:
        # Deny access
        return HttpResponseForbidden("Admins only.")
    user = get_object_or_404(get_user_model(), id=user_id)
    # If request method is POST
    if request.method == 'POST':
        user.delete()
        messages.success(request, 'User deleted successfully!')
        # Redirect to admin_users after successful deletion
        return redirect('admin_users')
    # If request method is not POST
    return render(request, 'news_app/delete_user.html', {'user': user})


# --------- Publish Newsletter View ---------
@login_required
def publish_newsletter_view(request, newsletter_id):
    """
    Allow an editor to publish a newsletter.
    """
    # If user is Admin
    if request.user.is_superuser:
        # Redirect to admin home
        return redirect('admin_home')
    # Get the newsletter object
    newsletter = get_object_or_404(Newsletter, id=newsletter_id)
    # Publish the newsletter
    return publish_content(
        request,
        newsletter,
        'newsletter',
        staff_check=staff_editor_check
    )


# --------- Publish Article View ---------
@login_required
def publish_article_view(request, article_id):
    """
    Allow an editor to publish an article.
    """
    # If user is Admin
    if request.user.is_superuser:
        # Redirect to admin home
        return redirect('admin_home')
    # Get the article object
    article = get_object_or_404(Article, id=article_id)
    # Publish the article
    return publish_content(
        request,
        article,
        'article',
        staff_check=staff_editor_check
    )


# --------- Edit Comment View ---------
@login_required
@superuser_redirect
def edit_comment_view(request, comment_id):
    """
    Allow a user or editor to edit a comment.
    """
    # Get the comment object
    comment = get_object_or_404(Comment, id=comment_id)
    # If user cannot manage the comment
    if not can_manage_comment(request.user, comment):
        # Deny access
        return HttpResponseForbidden(
            "You do not have permission to edit this comment."
        )
    # If request method is POST
    if request.method == 'POST':
        content = request.POST.get('content', '').strip()
        # If content is empty
        if not content:
            messages.error(request, 'Comment content is required.')
        # If content is provided
        else:
            comment.content = content
            comment.save()
            messages.success(request, 'Comment updated successfully!')
            # Redirect to article detail after successful update
            return redirect('article_detail', article_id=comment.article.id)
    # Render the edit comment page
    return render(request, 'news_app/edit_comment.html', {'comment': comment})


# --------- Delete Comment View ---------
@login_required
@superuser_redirect
def delete_comment_view(request, comment_id):
    """
    Allow a user or editor to delete a comment.
    """
    # Get the comment object
    comment = get_object_or_404(Comment, id=comment_id)
    # If user cannot manage the comment
    if not can_manage_comment(request.user, comment):
        # Deny access
        return HttpResponseForbidden(
            "You do not have permission to delete this comment."
        )
    # If request method is POST
    if request.method == 'POST':
        article_id = comment.article.id
        comment.delete()
        messages.success(request, 'Comment deleted successfully!')
        # Redirect to article detail after successful deletion
        return redirect('article_detail', article_id=article_id)
    # Render the delete comment page
    return render(
        request,
        'news_app/delete_comment.html',
        {'comment': comment}
    )

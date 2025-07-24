# News_app/models.py
from django.db import models
from django.contrib.auth.models import AbstractUser


# CustomUser model to represent different user roles in the news application
class CustomUser(AbstractUser):
    """
    Model to represent a custom user with different roles

    This model extends the default Django user model to include roles
    such as Reader, Editor, and Journalist. Each role has specific fields
    and relationships to other models like Publisher, Article, and Newsletter.

    Fields:
    - role: The role of the user (reader, editor, journalist).

    Relationships:
    - Readers can subscribe to multiple Publishers and Journalists
      via Subscription.
    - Journalists can create independent Articles and Newsletters
      (is_independent=True).
    - Editors can manage Articles and Newsletters, approving or rejecting them.

    Methods:
    - can_approve_articles: Returns True if user is editor or in
      the Editors group.
    - can_manage_content: Returns True if user is editor or in
      the Editors group.
    - save: Custom save method to handle role-specific logic.
    """
    ROLE_CHOICES = [
        ('reader', 'Reader'),
        ('editor', 'Editor'),
        ('journalist', 'Journalist'),
    ]

    role = models.CharField(
        max_length=20, choices=ROLE_CHOICES, default='reader'
    )

    def can_approve_articles(self):
        """
        Check if user can approve articles

        Returns True if user has Editor role or is in the Editors group
        """
        return (self.role == 'editor' or
                self.groups.filter(name='Editors').exists())

    def can_manage_content(self):
        """
        Check if user can manage content (view unapproved articles)

        Returns True if user has Editor role or is in the Editors group
        """
        return (self.role == 'editor' or
                self.groups.filter(name='Editors').exists())

    def save(self, *args, **kwargs):
        """
        Custom save method to handle role-specific logic

        This method ensures that when a user is created or updated,
        appropriate relationships and cleanup are performed based on the role.
        """
        is_new = self.pk is None
        super().save(*args, **kwargs)
        # Now it's safe to access related fields
        if self.role == 'journalist':
            if is_new:
                # Remove all subscriptions to publishers/journalists
                self.subscriptions.all().delete()
        elif self.role == 'reader':
            if is_new:
                # Remove all authored articles/newsletters
                # and staff memberships
                self.authored_articles.all().delete()
                self.authored_newsletters.all().delete()
                PublisherStaff.objects.filter(user=self).delete()


# Publisher model to represent a news publisher organization
class Publisher(models.Model):
    """
    Model to represent a news publisher organization

    Publishers are organizations that can have multiple editors and journalists
    working for them. They can publish articles and newsletters through their
    associated staff members.

    Fields:
    - name: The name of the publisher organization.
    - description: A detailed description of the publisher.
    - created_date: The date when the publisher was created.

    Relationships:
    - Publishers can have multiple Editors and Journalists via PublisherStaff.
    - Publishers can have multiple Articles and Newsletters published
      under them.

    Methods:
    - ordering: Publishers are ordered by name.
    - __str__: Returns the name of the publisher for easy identification.
    """
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    created_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


# Category model to represent article categories
class Category(models.Model):
    """
    Model to represent article categories

    Categories are used to organize and classify articles into different
    topics or subjects. This helps readers find articles of interest and
    enables better content organization.

    Fields:
    - name: The name of the category.
    - description: A detailed description of what the category covers.

    Relationships:
    - Categories can have multiple Articles associated with them.

    Methods:
    - verbose_name_plural: Set to "Categories" for proper admin display.
    - ordering: Categories are ordered by name.
    - __str__: Returns the name of the category for easy identification.
    """
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)

    class Meta:
        verbose_name_plural = "Categories"
        ordering = ['name']

    def __str__(self):
        return self.name


# Article model to represent news articles
class Article(models.Model):
    """
    Model to represent news articles

    Articles are the main content pieces in the news application. They are
    created by journalists, can be associated with publishers, and require
    approval from editors before publication.

    Fields:
    - title: The headline/title of the article.
    - content: The main body content of the article.
    - author: Foreign key to the journalist who wrote the article.
    - publisher: Optional foreign key to the publisher organization.
    - category: Optional foreign key to categorize the article.
    - created_date: Timestamp when the article was created.
    - published_date: Timestamp when the article was published.
    - updated_date: Timestamp when the article was last updated.
    - is_approved: Boolean indicating if the article is approved.
    - approved_by: Foreign key to the editor who approved the article.
    - approval_date: Timestamp when the article was approved.
    - is_published: Boolean indicating if the article is published.
    - image: Optional featured image for the article.
    - is_independent: Boolean indicating if the article is independent.

    Relationships:
    - Articles are authored by Journalists (CustomUser).
    - Articles can be published by Publishers.
    - Articles can be categorized under Categories.
    - Articles can be approved by Editors (CustomUser).
    - Articles can have multiple Comments from readers.

    Methods:
    - __str__: Returns the title of the article for easy identification.
    - ordering: Articles are ordered by creation date (newest first).
    """
    title = models.CharField(max_length=200)
    content = models.TextField()
    author = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='authored_articles'
    )
    publisher = models.ForeignKey(
        Publisher,
        on_delete=models.CASCADE,
        related_name='articles',
        null=True,
        blank=True
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    created_date = models.DateTimeField(auto_now_add=True)
    published_date = models.DateTimeField(null=True, blank=True)
    updated_date = models.DateTimeField(auto_now=True)

    # Article approval status
    is_approved = models.BooleanField(default=False)
    approved_by = models.ForeignKey(
        CustomUser,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        limit_choices_to={'role': 'editor'},
        related_name='approved_articles'
    )
    approval_date = models.DateTimeField(null=True, blank=True)

    is_published = models.BooleanField(default=False)
    image = models.ImageField(
        upload_to='article_images/', blank=True, null=True
    )
    # replaces independent_articles
    is_independent = models.BooleanField(default=False)

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['-created_date']


# Newsletter model to represent newsletters
class Newsletter(models.Model):
    """
    Model to represent newsletters

    Newsletters are periodic publications that can be created by journalists
    and published by publisher organizations. Like articles, they require
    editorial approval before publication.

    Fields:
    - title: The title/subject of the newsletter.
    - content: The main content of the newsletter.
    - author: Foreign key to the journalist who created the newsletter.
    - publisher: Optional foreign key to the publisher organization.
    - created_date: Timestamp when the newsletter was created.
    - published_date: Timestamp when the newsletter was published.
    - updated_date: Timestamp when the newsletter was last updated.
    - is_approved: Boolean indicating if the newsletter is approved.
    - approved_by: Foreign key to the editor who approved the newsletter.
    - approval_date: Timestamp when the newsletter was approved.
    - is_published: Boolean indicating if the newsletter is published.
    - is_independent: Boolean indicating if the newsletter is independent.

    Relationships:
    - Newsletters are authored by Journalists (CustomUser).
    - Newsletters can be published by Publishers.
    - Newsletters can be approved by Editors (CustomUser).
    - Readers can subscribe to newsletters from specific publishers.

    Methods:
    - __str__: Returns the title of the newsletter for easy identification.
    - ordering: Newsletters are ordered by creation date (newest first).
    """
    title = models.CharField(max_length=200)
    content = models.TextField()
    author = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='authored_newsletters'
    )
    publisher = models.ForeignKey(
        Publisher,
        on_delete=models.CASCADE,
        related_name='newsletters',
        null=True,
        blank=True
    )
    created_date = models.DateTimeField(auto_now_add=True)
    published_date = models.DateTimeField(null=True, blank=True)
    updated_date = models.DateTimeField(auto_now=True)

    # Newsletter approval status
    is_approved = models.BooleanField(default=False)
    approved_by = models.ForeignKey(
        CustomUser,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        limit_choices_to={'role': 'editor'},
        related_name='approved_newsletters'
    )
    approval_date = models.DateTimeField(null=True, blank=True)

    is_published = models.BooleanField(default=False)
    # replaces independent_newsletters
    is_independent = models.BooleanField(default=False)

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['-created_date']


# Comment model to represent comments on articles
class Comment(models.Model):
    """
    Model to represent comments on articles

    Comments allow readers to engage with articles by sharing their thoughts,
    opinions, or feedback. This creates an interactive community around
    news content.

    Fields:
    - article: Foreign key to the article being commented on.
    - author: Foreign key to the user who wrote the comment.
    - content: The text content of the comment.
    - created_date: Timestamp when the comment was created.
    - updated_date: Timestamp when the comment was last updated.

    Relationships:
    - Comments belong to a specific Article.
    - Comments are authored by any authenticated user (CustomUser).

    Methods:
    - __str__: Returns a descriptive string showing the commenter and article.
    - ordering: Comments are ordered by creation date (newest first).
    """
    article = models.ForeignKey(
        Article,
        on_delete=models.CASCADE,
        related_name='comments'
    )
    author = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='comments'
    )
    content = models.TextField()
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    def __str__(self):
        return (f'Comment by {self.author.username} on '
                f'{self.article.title}')

    class Meta:
        ordering = ['-created_date']


# PublisherStaff model to represent staff members of a publisher
class PublisherStaff(models.Model):
    """
    Model to represent staff members of a publisher

    This is a join table for publisher staff (editors/journalists).

    Fields:
    - publisher: Foreign key to Publisher.
    - user: Foreign key to CustomUser (staff member).
    - role: Staff role (editor/journalist).
    - date_joined: Date joined.

    Relationships:
    - Connects publishers to their staff (editors/journalists).

    Methods:
    - __str__: Returns staff member and role for easy identification.
    """
    publisher = models.ForeignKey('Publisher', on_delete=models.CASCADE)
    user = models.ForeignKey('CustomUser', on_delete=models.CASCADE)
    role = models.CharField(
        max_length=20,
        choices=[
            ('editor', 'Editor'),
            ('journalist', 'Journalist')
        ]
    )
    date_joined = models.DateField(auto_now_add=True)

    def __str__(self):
        return f'{self.user.username} as {self.role}'


# Subscription model to represent user subscriptions
# to publishers or journalists
class Subscription(models.Model):
    """
    Model to represent user subscriptions to publishers or journalists

    This is a join table for user subscriptions to publishers or journalists.

    Fields:
    - subscriber: Foreign key to CustomUser (user subscribing).
    - publisher: Foreign key to Publisher (optional).
    - journalist: Foreign key to CustomUser (journalist, optional).
    # Only one of publisher or journalist should be set

    Relationships:
    - Connects users to publishers or journalists they subscribe to.

    Methods:
    - __str__: Returns a description of the subscription.
    """
    subscriber = models.ForeignKey(
        'CustomUser',
        on_delete=models.CASCADE,
        related_name='subscriptions'
    )
    publisher = models.ForeignKey(
        'Publisher',
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )
    journalist = models.ForeignKey(
        'CustomUser',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='journalist_subscriptions'
    )
    # Only one of publisher or journalist should be set

    def __str__(self):
        if self.publisher:
            return (
                f"{self.subscriber.username} subscribes to publisher "
                f"{self.publisher.name}"
            )
        elif self.journalist:
            return (
                f"{self.subscriber.username} subscribes to journalist "
                f"{self.journalist.username}"
            )
        return f"{self.subscriber.username} subscription"

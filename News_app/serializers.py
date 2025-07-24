# News_app/serializers.py
from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import (
    Article, Newsletter, Publisher, Category, Comment,
    PublisherStaff, Subscription
)

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    '''
    Serializer for User model.
    Converts User model instances to JSON format and vice versa.
    Includes fields like username, email, first_name, last_name, and role.

    :param username: Username of the user
    :param email: Email address of the user
    :param first_name: First name of the user
    :param last_name: Last name of the user
    :param role: Role of the user (e.g., journalist, publisher)

    :return: Serialized data for User model
    '''
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'role']
        read_only_fields = ['id']


class UserCreateSerializer(serializers.ModelSerializer):
    '''
    Serializer for creating User model instances.
    Handles password hashing and user creation logic.

    :param username: Username of the user
    :param email: Email address of the user
    :param first_name: First name of the user
    :param last_name: Last name of the user
    :param role: Role of the user (e.g., journalist, publisher)
    :param password: Password for the user (write-only)

    :return: Serialized data for new User instance
    '''
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = [
            'username', 'email', 'first_name', 'last_name', 'role', 'password'
        ]

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user


class CategorySerializer(serializers.ModelSerializer):
    '''
    Serializer for Category model.
    Converts Category instances to and from JSON format.

    :param id: ID of the category
    :param name: Name of the category
    :param description: Description of the category

    :return: Serialized data for Category model
    '''
    class Meta:
        model = Category
        fields = ['id', 'name', 'description']


class PublisherSerializer(serializers.ModelSerializer):
    '''
    Serializer for Publisher model.
    Converts Publisher instances to and from JSON format.

    :param id: ID of the publisher
    :param name: Name of the publisher
    :param description: Description of the publisher
    :param created_date: Date the publisher was created (read-only)

    :return: Serialized data for Publisher model
    '''
    class Meta:
        model = Publisher
        fields = [
            'id', 'name', 'description', 'created_date'
        ]
        read_only_fields = ['id', 'created_date']


class ArticleSerializer(serializers.ModelSerializer):
    '''
    Serializer for Article model.
    Handles nested serialization for related fields and
    write-only IDs for creation.

    :param id: ID of the article
    :param title: Title of the article
    :param content: Content of the article
    :param author: Author of the article (UserSerializer, read-only)
    :param publisher: Publisher of the article (PublisherSerializer, read-only)
    :param category: Category of the article (CategorySerializer, read-only)
    :param created_date: Date the article was created (read-only)
    :param published_date: Date the article was published
    :param updated_date: Date the article was last updated (read-only)
    :param is_approved: Approval status of the article
    :param approved_by: User who approved the article
        (UserSerializer, read-only)
    :param approval_date: Date the article was approved (read-only)
    :param is_published: Publication status of the article
    :param image: Image associated with the article
    :param is_independent: Whether the article is independent
    :param publisher_id: Publisher ID for write operations (write-only)
    :param category_id: Category ID for write operations (write-only)

    :return: Serialized data for Article model
    '''
    author = UserSerializer(read_only=True)
    publisher = PublisherSerializer(read_only=True)
    category = CategorySerializer(read_only=True)
    approved_by = UserSerializer(read_only=True)

    # For write operations
    publisher_id = serializers.IntegerField(write_only=True, required=False)
    category_id = serializers.IntegerField(write_only=True, required=False)

    class Meta:
        model = Article
        fields = [
            'id', 'title', 'content', 'author', 'publisher', 'category',
            'created_date', 'published_date', 'updated_date', 'is_approved',
            'approved_by', 'approval_date', 'is_published', 'image',
            'is_independent', 'publisher_id', 'category_id'
        ]
        read_only_fields = [
            'id', 'author', 'created_date', 'updated_date',
            'approved_by', 'approval_date'
        ]

    def create(self, validated_data):
        # Remove write-only fields and set the author
        publisher_id = validated_data.pop('publisher_id', None)
        category_id = validated_data.pop('category_id', None)

        article = Article(**validated_data)
        article.author = self.context['request'].user

        if publisher_id:
            article.publisher_id = publisher_id
        if category_id:
            article.category_id = category_id

        article.save()
        return article


class ArticleCreateSerializer(serializers.ModelSerializer):
    '''
    Serializer for creating Article model instances.
    Used for simplified article creation with required fields.

    :param title: Title of the article
    :param content: Content of the article
    :param publisher: Publisher of the article
    :param category: Category of the article
    :param image: Image associated with the article
    :param is_independent: Whether the article is independent

    :return: Serialized data for new Article instance
    '''
    class Meta:
        model = Article
        fields = [
            'title', 'content', 'publisher', 'category',
            'image', 'is_independent'
        ]

    def create(self, validated_data):
        validated_data['author'] = self.context['request'].user
        return super().create(validated_data)


class NewsletterSerializer(serializers.ModelSerializer):
    '''
    Serializer for Newsletter model.
    Handles nested serialization for related fields and
    write-only IDs for creation.

    :param id: ID of the newsletter
    :param title: Title of the newsletter
    :param content: Content of the newsletter
    :param author: Author of the newsletter (UserSerializer, read-only)
    :param publisher: Publisher of the newsletter
        (PublisherSerializer, read-only)
    :param created_date: Date the newsletter was created (read-only)
    :param published_date: Date the newsletter was published
    :param updated_date: Date the newsletter was last updated (read-only)
    :param is_approved: Approval status of the newsletter
    :param approved_by: User who approved the newsletter
        (UserSerializer, read-only)
    :param approval_date: Date the newsletter was approved (read-only)
    :param is_published: Publication status of the newsletter
    :param is_independent: Whether the newsletter is independent
    :param publisher_id: Publisher ID for write operations (write-only)

    :return: Serialized data for Newsletter model
    '''
    author = UserSerializer(read_only=True)
    publisher = PublisherSerializer(read_only=True)
    approved_by = UserSerializer(read_only=True)

    # For write operations
    publisher_id = serializers.IntegerField(write_only=True, required=False)

    class Meta:
        model = Newsletter
        fields = [
            'id', 'title', 'content', 'author', 'publisher', 'created_date',
            'published_date', 'updated_date', 'is_approved', 'approved_by',
            'approval_date', 'is_published', 'is_independent', 'publisher_id'
        ]
        read_only_fields = [
            'id', 'author', 'created_date', 'updated_date',
            'approved_by', 'approval_date'
        ]

    def create(self, validated_data):
        publisher_id = validated_data.pop('publisher_id', None)

        newsletter = Newsletter(**validated_data)
        newsletter.author = self.context['request'].user

        if publisher_id:
            newsletter.publisher_id = publisher_id

        newsletter.save()
        return newsletter


class CommentSerializer(serializers.ModelSerializer):
    '''
    Serializer for Comment model.
    Handles serialization of comment data and automatic author assignment.

    :param id: ID of the comment
    :param article: Article the comment belongs to
    :param author: Author of the comment (UserSerializer, read-only)
    :param content: Content of the comment
    :param created_date: Date the comment was created (read-only)
    :param updated_date: Date the comment was last updated (read-only)

    :return: Serialized data for Comment model
    '''
    author = UserSerializer(read_only=True)

    class Meta:
        model = Comment
        fields = [
            'id', 'article', 'author', 'content',
            'created_date', 'updated_date'
        ]
        read_only_fields = ['id', 'author', 'created_date', 'updated_date']

    def create(self, validated_data):
        validated_data['author'] = self.context['request'].user
        return super().create(validated_data)


class ArticleApprovalSerializer(serializers.ModelSerializer):
    '''
    Serializer for approving Article instances.
    Used to update approval status and approval date.

    :param is_approved: Approval status of the article
    :param approval_date: Date the article was approved (read-only)

    :return: Serialized data for Article approval
    '''
    class Meta:
        model = Article
        fields = ['is_approved', 'approval_date']
        read_only_fields = ['approval_date']

    def update(self, instance, validated_data):
        if validated_data.get('is_approved'):
            validated_data['approved_by'] = self.context['request'].user
            from django.utils import timezone
            validated_data['approval_date'] = timezone.now()
        return super().update(instance, validated_data)


class NewsletterApprovalSerializer(serializers.ModelSerializer):
    '''
    Serializer for approving Newsletter instances.
    Used to update approval status and approval date.

    :param is_approved: Approval status of the newsletter
    :param approval_date: Date the newsletter was approved (read-only)

    :return: Serialized data for Newsletter approval
    '''
    class Meta:
        model = Newsletter
        fields = ['is_approved', 'approval_date']
        read_only_fields = ['approval_date']

    def update(self, instance, validated_data):
        if validated_data.get('is_approved'):
            validated_data['approved_by'] = self.context['request'].user
            from django.utils import timezone
            validated_data['approval_date'] = timezone.now()
        return super().update(instance, validated_data)


class PublisherStaffSerializer(serializers.ModelSerializer):
    '''
    Serializer for PublisherStaff model.
    Handles serialization of publisher staff assignments.

    :param id: ID of the publisher staff record
    :param publisher: Publisher assigned
    :param user: User assigned as staff
    :param role: Role of the staff member
    :param date_joined: Date the staff member joined (read-only)

    :return: Serialized data for PublisherStaff model
    '''
    class Meta:
        model = PublisherStaff
        fields = ['id', 'publisher', 'user', 'role', 'date_joined']
        read_only_fields = ['id', 'date_joined']


class SubscriptionSerializer(serializers.ModelSerializer):
    '''
    Serializer for Subscription model.
    Handles serialization of subscription data.

    :param id: ID of the subscription
    :param subscriber: User subscribing
    :param publisher: Publisher being subscribed to
    :param journalist: Journalist being followed

    :return: Serialized data for Subscription model
    '''
    class Meta:
        model = Subscription
        fields = ['id', 'subscriber', 'publisher', 'journalist']
        read_only_fields = ['id']

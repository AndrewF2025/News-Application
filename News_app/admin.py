# News_app/admin.py
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import (
    CustomUser, Publisher, Category, Article, Newsletter, Comment,
    PublisherStaff, Subscription
)


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ['username', 'email', 'role', 'is_active', 'is_staff']
    list_filter = ['role', 'is_active', 'is_staff']
    fieldsets = UserAdmin.fieldsets + (
        ('Custom Fields', {
            'fields': ('role',)
        }),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Custom Fields', {
            'fields': ('role',)
        }),
    )


@admin.register(Publisher)
class PublisherAdmin(admin.ModelAdmin):
    list_display = ['name', 'created_date']
    search_fields = ['name', 'description']


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'description']
    search_fields = ['name']


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = [
        'title', 'author', 'publisher', 'category',
        'is_approved', 'is_published', 'created_date'
    ]
    list_filter = [
        'is_approved', 'is_published', 'category',
        'publisher', 'created_date'
    ]
    search_fields = ['title', 'content', 'author__username']
    readonly_fields = ['created_date', 'updated_date']
    date_hierarchy = 'created_date'


@admin.register(Newsletter)
class NewsletterAdmin(admin.ModelAdmin):
    list_display = [
        'title', 'author', 'publisher',
        'is_approved', 'is_published', 'created_date'
    ]
    list_filter = ['is_approved', 'is_published', 'publisher', 'created_date']
    search_fields = ['title', 'content', 'author__username']
    readonly_fields = ['created_date', 'updated_date']
    date_hierarchy = 'created_date'


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ['author', 'article', 'created_date']
    list_filter = ['created_date']
    search_fields = ['content', 'author__username', 'article__title']
    readonly_fields = ['created_date', 'updated_date']


@admin.register(PublisherStaff)
class PublisherStaffAdmin(admin.ModelAdmin):
    list_display = ['publisher', 'user', 'role', 'date_joined']
    list_filter = ['role', 'publisher']
    search_fields = ['user__username', 'publisher__name']


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ['subscriber', 'publisher', 'journalist']
    list_filter = ['publisher', 'journalist']
    search_fields = [
        'subscriber__username',
        'publisher__name',
        'journalist__username'
    ]

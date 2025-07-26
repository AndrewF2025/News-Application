from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from News_app.models import Article, Category, Publisher, Newsletter, Comment

User = get_user_model()


class APITestSetup(APITestCase):
    """
    Base setup class for API test cases.
    Initializes a test user, category, publisher, article, newsletter, and
    comment for use in all derived API test classes. Handles authentication
    and test data creation.
    """
    def setUp(self):
        # Print setup start message
        print("\n[Setup] Creating test user, category, publisher, article, "
              "newsletter, and comment...")
        # Create a test user
        self.user = User.objects.create_user(
            username='testuser', password='testpass', role='journalist'
        )
        # Log in the test user
        self.client.login(username='testuser', password='testpass')
        # Create a test category
        self.category = Category.objects.create(name='Tech')
        # Create a test publisher
        self.publisher = Publisher.objects.create(name='Test Publisher')
        # Create a test article
        self.article = Article.objects.create(
            title='Test Article', content='Test Content',
            author=self.user, category=self.category
        )
        # Create a test newsletter
        self.newsletter = Newsletter.objects.create(
            title='Test Newsletter',
            content='Newsletter Content',
            author=self.user
        )
        # Create a test comment
        self.comment = Comment.objects.create(
            article=self.article, author=self.user, content='Test Comment'
        )
        # Print setup complete message
        print("[Setup] Test data created.")


class ArticleAPITests(APITestSetup):
    """
    API tests for the Article model.
    Covers listing, creation, retrieval, update, deletion, unauthorized access,
    and invalid data scenarios for articles.
    """
    # Test listing articles via the API
    def test_list_articles(self):
        """
        Test listing articles via the API.
        Asserts that the response is successful and returns the article list.
        """
        print("\n[Tests for listing articles via the API]")
        # Build the URL for listing articles
        url = reverse('article-list')
        print(f"[Request] GET {url}")
        # Send GET request to the API
        response = self.client.get(url)
        print(f"[Response] Status code: {response.status_code}")
        # Assert that the response is successful
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        print("[Assert] Article list returned successfully.")

    # Test creating a new article via the API
    def test_create_article(self):
        """
        Test creating a new article via the API.
        Asserts that the article is created successfully.
        """
        print("\n[Tests for creating a new article via the API]")
        # Build the URL for creating an article
        url = reverse('article-list')
        # Prepare the data for the new article
        data = {
            'title': 'New Article',
            'content': 'Some content',
            'category': self.category.id,
            'author': self.user.id
        }
        print(f"[Request] POST {url} with data: {data}")
        # Send POST request to create the article
        response = self.client.post(url, data)
        print(f"[Response] Status code: {response.status_code}")
        # Assert that the article was created successfully
        self.assertIn(
            response.status_code,
            [status.HTTP_201_CREATED, status.HTTP_200_OK]
        )
        print("[Assert] Article created successfully.")

    # Test retrieving a single article via the API
    def test_retrieve_article(self):
        """
        Test retrieving a single article via the API.
        Asserts that the response is successful and returns the article detail.
        """
        print("\n[Tests for retrieving a single article via the API]")
        # Build the URL for retrieving the article
        url = reverse('article-detail', args=[self.article.id])
        print(f"[Request] GET {url}")
        # Send GET request to retrieve the article
        response = self.client.get(url)
        print(f"[Response] Status code: {response.status_code}")
        # Assert that the response is successful
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        print("[Assert] Article detail returned successfully.")

    # Test updating an article via the API
    def test_update_article(self):
        """
        Test updating an article via the API.
        Asserts that the article is updated successfully.
        """
        print("\n[Tests for updating an article via the API]")
        # Build the URL for updating the article
        url = reverse('article-detail', args=[self.article.id])
        # Prepare the updated data
        data = {
            'title': 'Updated Title',
            'content': 'Updated content',
            'category': self.category.id,
            'author': self.user.id
        }
        print(f"[Request] PUT {url} with data: {data}")
        # Send PUT request to update the article
        response = self.client.put(url, data)
        print(f"[Response] Status code: {response.status_code}")
        # Assert that the article was updated successfully
        self.assertIn(
            response.status_code,
            [status.HTTP_200_OK, status.HTTP_202_ACCEPTED]
        )
        print("[Assert] Article updated successfully.")

    # Test deleting an article via the API
    def test_delete_article(self):
        """
        Test deleting an article via the API.
        Asserts that the article is deleted successfully.
        """
        print("\n[Tests for deleting an article via the API]")
        # Build the URL for deleting the article
        url = reverse('article-detail', args=[self.article.id])
        print(f"[Request] DELETE {url}")
        # Send DELETE request to delete the article
        response = self.client.delete(url)
        print(f"[Response] Status code: {response.status_code}")
        # Assert that the article was deleted successfully
        self.assertIn(
            response.status_code,
            [status.HTTP_204_NO_CONTENT, status.HTTP_200_OK]
        )
        print("[Assert] Article deleted successfully.")

    # Test unauthorized article creation is blocked
    def test_unauthorized_create_article(self):
        """
        Test that unauthorized article creation is blocked by the API.
        """
        print("\n[Tests for unauthorized article creation]")
        # Log out to simulate unauthorized user
        self.client.logout()
        # Build the URL for creating an article
        url = reverse('article-list')
        # Prepare the data for the new article
        data = {
            'title': 'Unauthorized Article',
            'content': 'Should not work',
            'category': self.category.id,
            'author': self.user.id
        }
        print(f"[Request] POST {url} with data: {data} (unauthenticated)")
        # Send POST request as unauthorized user
        response = self.client.post(url, data)
        print(f"[Response] Status code: {response.status_code}")
        # Assert that unauthorized creation is blocked
        self.assertIn(
            response.status_code,
            [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN]
        )
        print("[Assert] Unauthorized article creation blocked.")

    # Test creating an article with invalid data is blocked
    def test_create_article_invalid_data(self):
        """
        Test creating an article with invalid data.
        Asserts that invalid creation is blocked by the API.
        """
        print("\n[Tests for creating an article with invalid data]")
        # Build the URL for creating an article
        url = reverse('article-list')
        # Prepare invalid data (missing required fields)
        data = {
            'title': '',  # Invalid: title required
            'content': '',  # Invalid: content required
        }
        print(f"[Request] POST {url} with data: {data}")
        # Send POST request with invalid data
        response = self.client.post(url, data)
        print(f"[Response] Status code: {response.status_code}")
        # Assert that invalid creation is blocked
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        print("[Assert] Invalid article creation blocked.")


class CategoryAPITests(APITestSetup):
    """
    API tests for the Category model.
    Covers listing, creation, retrieval, update, deletion, unauthorized access,
    and invalid data scenarios for categories.
    """
    # Test listing categories via the API
    def test_list_categories(self):
        """
        Test listing categories via the API.
        Asserts that the response is successful and returns the category list.
        """
        print("\n[Tests for listing categories via the API]")
        # Build the URL for listing categories
        url = reverse('category-list')
        print(f"[Request] GET {url}")
        # Send GET request to the API
        response = self.client.get(url)
        print(f"[Response] Status code: {response.status_code}")
        # Assert that the response is successful
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        print("[Assert] Category list returned successfully.")

    # Test retrieving a single category via the API
    def test_retrieve_category(self):
        """
        Test retrieving a single category via the API.
        Asserts that the response is successful and returns the
        category detail.
        """
        print("\n[Tests for retrieving a single category via the API]")
        # Build the URL for retrieving the category
        url = reverse('category-detail', args=[self.category.id])
        print(f"[Request] GET {url}")
        # Send GET request to retrieve the category
        response = self.client.get(url)
        print(f"[Response] Status code: {response.status_code}")
        # Assert that the response is successful
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        print("[Assert] Category detail returned successfully.")

    # Test updating a category via the API
    def test_update_category(self):
        """
        Test updating a category via the API.
        Asserts that the category is updated successfully.
        """
        print("\n[Tests for updating a category via the API]")
        # Build the URL for updating the category
        url = reverse('category-detail', args=[self.category.id])
        # Prepare the updated data
        data = {'name': 'Updated Category'}
        print(f"[Request] PUT {url} with data: {data}")
        # Send PUT request to update the category
        response = self.client.put(url, data)
        print(f"[Response] Status code: {response.status_code}")
        # Assert that the category was updated successfully
        self.assertIn(
            response.status_code,
            [status.HTTP_200_OK, status.HTTP_202_ACCEPTED]
        )
        print("[Assert] Category updated successfully.")

    # Test deleting a category via the API
    def test_delete_category(self):
        """
        Test deleting a category via the API.
        Asserts that the category is deleted successfully.
        """
        print("\n[Tests for deleting a category via the API]")
        # Build the URL for deleting the category
        url = reverse('category-detail', args=[self.category.id])
        print(f"[Request] DELETE {url}")
        # Send DELETE request to delete the category
        response = self.client.delete(url)
        print(f"[Response] Status code: {response.status_code}")
        # Assert that the category was deleted successfully
        self.assertIn(
            response.status_code,
            [status.HTTP_204_NO_CONTENT, status.HTTP_200_OK]
        )
        print("[Assert] Category deleted successfully.")

    # Test unauthorized category creation is blocked
    def test_unauthorized_create_category(self):
        """
        Test that unauthorized category creation is blocked by the API.
        """
        print("\n[Tests for unauthorized category creation]")
        # Log out to simulate unauthorized user
        self.client.logout()
        # Build the URL for creating a category
        url = reverse('category-list')
        # Prepare the data for the new category
        data = {'name': 'Unauthorized Category'}
        print(f"[Request] POST {url} with data: {data} (unauthenticated)")
        # Send POST request as unauthorized user
        response = self.client.post(url, data)
        print(f"[Response] Status code: {response.status_code}")
        # Assert that unauthorized creation is blocked
        self.assertIn(
            response.status_code,
            [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN]
        )
        print("[Assert] Unauthorized category creation blocked.")

    # Test creating a category with invalid data is blocked
    def test_create_category_invalid_data(self):
        """
        Test creating a category with invalid data.
        Asserts that invalid creation is blocked by the API.
        """
        print("\n[Tests for creating a category with invalid data]")
        # Build the URL for creating a category
        url = reverse('category-list')
        # Prepare invalid data (missing required fields)
        data = {'name': ''}  # Invalid: name required
        print(f"[Request] POST {url} with data: {data}")
        # Send POST request with invalid data
        response = self.client.post(url, data)
        print(f"[Response] Status code: {response.status_code}")
        # Assert that invalid creation is blocked
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        print("[Assert] Invalid category creation blocked.")


class PublisherAPITests(APITestSetup):
    """
    API tests for the Publisher model.
    Covers listing, creation, retrieval, update, deletion, unauthorized access,
    and invalid data scenarios for publishers.
    """
    # Test listing publishers via the API
    def test_list_publishers(self):
        """
        Test listing publishers via the API.
        Asserts that the response is successful and returns the publisher list.
        """
        print("\n[Tests for listing publishers via the API]")
        # Build the URL for listing publishers
        url = reverse('publisher-list')
        print(f"[Request] GET {url}")
        # Send GET request to the API
        response = self.client.get(url)
        print(f"[Response] Status code: {response.status_code}")
        # Assert that the response is successful
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        print("[Assert] Publisher list returned successfully.")

    # Test retrieving a single publisher via the API
    def test_retrieve_publisher(self):
        """
        Test retrieving a single publisher via the API.
        Asserts that the response is successful and returns the
        publisher detail.
        """
        print("\n[Tests for retrieving a single publisher via the API]")
        # Build the URL for retrieving the publisher
        url = reverse('publisher-detail', args=[self.publisher.id])
        print(f"[Request] GET {url}")
        # Send GET request to retrieve the publisher
        response = self.client.get(url)
        print(f"[Response] Status code: {response.status_code}")
        # Assert that the response is successful
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        print("[Assert] Publisher detail returned successfully.")

    # Test updating a publisher via the API
    def test_update_publisher(self):
        """
        Test updating a publisher via the API.
        Asserts that the publisher is updated successfully.
        """
        print("\n[Tests for updating a publisher via the API]")
        # Build the URL for updating the publisher
        url = reverse('publisher-detail', args=[self.publisher.id])
        # Prepare the updated data
        data = {'name': 'Updated Publisher'}
        print(f"[Request] PUT {url} with data: {data}")
        # Send PUT request to update the publisher
        response = self.client.put(url, data)
        print(f"[Response] Status code: {response.status_code}")
        # Assert that the publisher was updated successfully
        self.assertIn(
            response.status_code,
            [status.HTTP_200_OK, status.HTTP_202_ACCEPTED]
        )
        print("[Assert] Publisher updated successfully.")

    # Test deleting a publisher via the API
    def test_delete_publisher(self):
        """
        Test deleting a publisher via the API.
        Asserts that the publisher is deleted successfully.
        """
        print("\n[Tests for deleting a publisher via the API]")
        # Build the URL for deleting the publisher
        url = reverse('publisher-detail', args=[self.publisher.id])
        print(f"[Request] DELETE {url}")
        # Send DELETE request to delete the publisher
        response = self.client.delete(url)
        print(f"[Response] Status code: {response.status_code}")
        # Assert that the publisher was deleted successfully
        self.assertIn(
            response.status_code,
            [status.HTTP_204_NO_CONTENT, status.HTTP_200_OK]
        )
        print("[Assert] Publisher deleted successfully.")

    # Test unauthorized publisher creation is blocked
    def test_unauthorized_create_publisher(self):
        """
        Test that unauthorized publisher creation is blocked by the API.
        """
        print("\n[Tests for unauthorized publisher creation]")
        # Log out to simulate unauthorized user
        self.client.logout()
        # Build the URL for creating a publisher
        url = reverse('publisher-list')
        # Prepare the data for the new publisher
        data = {'name': 'Unauthorized Publisher'}
        print(f"[Request] POST {url} with data: {data} (unauthenticated)")
        # Send POST request as unauthorized user
        response = self.client.post(url, data)
        print(f"[Response] Status code: {response.status_code}")
        # Assert that unauthorized creation is blocked
        self.assertIn(
            response.status_code,
            [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN]
        )
        print("[Assert] Unauthorized publisher creation blocked.")

    # Test creating a publisher with invalid data is blocked
    def test_create_publisher_invalid_data(self):
        """
        Test creating a publisher with invalid data.
        Asserts that invalid creation is blocked by the API.
        """
        print("\n[Tests for creating a publisher with invalid data]")
        # Build the URL for creating a publisher
        url = reverse('publisher-list')
        # Prepare invalid data (missing required fields)
        data = {'name': ''}  # Invalid: name required
        print(f"[Request] POST {url} with data: {data}")
        # Send POST request with invalid data
        response = self.client.post(url, data)
        print(f"[Response] Status code: {response.status_code}")
        # Assert that invalid creation is blocked
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        print("[Assert] Invalid publisher creation blocked.")


class NewsletterAPITests(APITestSetup):
    """
    API tests for the Newsletter model.
    Covers listing, creation, retrieval, update, deletion, unauthorized access,
    and invalid data scenarios for newsletters.
    """
    # Test listing newsletters via the API
    def test_list_newsletters(self):
        """
        Test listing newsletters via the API.
        Asserts that the response is successful and returns the
        newsletter list.
        """
        print("\n[Tests for listing newsletters via the API]")
        # Build the URL for listing newsletters
        url = reverse('newsletter-list')
        print(f"[Request] GET {url}")
        # Send GET request to the API
        response = self.client.get(url)
        print(f"[Response] Status code: {response.status_code}")
        # Assert that the response is successful
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        print("[Assert] Newsletter list returned successfully.")

    # Test retrieving a single newsletter via the API
    def test_retrieve_newsletter(self):
        """
        Test retrieving a single newsletter via the API.
        Asserts that the response is successful and returns the
        newsletter detail.
        """
        print("\n[Tests for retrieving a single newsletter via the API]")
        # Build the URL for retrieving the newsletter
        url = reverse('newsletter-detail', args=[self.newsletter.id])
        print(f"[Request] GET {url}")
        # Send GET request to retrieve the newsletter
        response = self.client.get(url)
        print(f"[Response] Status code: {response.status_code}")
        # Assert that the response is successful
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        print("[Assert] Newsletter detail returned successfully.")

    # Test updating a newsletter via the API
    def test_update_newsletter(self):
        """
        Test updating a newsletter via the API.
        Asserts that the newsletter is updated successfully.
        """
        print("\n[Tests for updating a newsletter via the API]")
        # Build the URL for updating the newsletter
        url = reverse('newsletter-detail', args=[self.newsletter.id])
        # Prepare the updated data
        data = {
            'title': 'Updated Newsletter',
            'content': 'Updated content',
            'author': self.user.id
        }
        print(f"[Request] PUT {url} with data: {data}")
        # Send PUT request to update the newsletter
        response = self.client.put(url, data)
        print(f"[Response] Status code: {response.status_code}")
        # Assert that the newsletter was updated successfully
        self.assertIn(
            response.status_code,
            [status.HTTP_200_OK, status.HTTP_202_ACCEPTED]
        )
        print("[Assert] Newsletter updated successfully.")

    # Test deleting a newsletter via the API
    def test_delete_newsletter(self):
        """
        Test deleting a newsletter via the API.
        Asserts that the newsletter is deleted successfully.
        """
        print("\n[Tests for deleting a newsletter via the API]")
        # Build the URL for deleting the newsletter
        url = reverse('newsletter-detail', args=[self.newsletter.id])
        print(f"[Request] DELETE {url}")
        # Send DELETE request to delete the newsletter
        response = self.client.delete(url)
        print(f"[Response] Status code: {response.status_code}")
        # Assert that the newsletter was deleted successfully
        self.assertIn(
            response.status_code,
            [status.HTTP_204_NO_CONTENT, status.HTTP_200_OK]
        )
        print("[Assert] Newsletter deleted successfully.")

    # Test unauthorized newsletter creation is blocked
    def test_unauthorized_create_newsletter(self):
        """
        Test that unauthorized newsletter creation is blocked by the API.
        """
        print("\n[Tests for unauthorized newsletter creation]")
        # Log out to simulate unauthorized user
        self.client.logout()
        # Build the URL for creating a newsletter
        url = reverse('newsletter-list')
        # Prepare the data for the new newsletter
        data = {
            'title': 'Unauthorized Newsletter',
            'content': 'Should not work',
            'author': self.user.id
        }
        print(f"[Request] POST {url} with data: {data} (unauthenticated)")
        # Send POST request as unauthorized user
        response = self.client.post(url, data)
        print(f"[Response] Status code: {response.status_code}")
        # Assert that unauthorized creation is blocked
        self.assertIn(
            response.status_code,
            [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN]
        )
        print("[Assert] Unauthorized newsletter creation blocked.")

    # Test creating a newsletter with invalid data is blocked
    def test_create_newsletter_invalid_data(self):
        """
        Test creating a newsletter with invalid data.
        Asserts that invalid creation is blocked by the API.
        """
        print("\n[Tests for creating a newsletter with invalid data]")
        # Build the URL for creating a newsletter
        url = reverse('newsletter-list')
        # Prepare invalid data (missing required fields)
        data = {
            'title': '',
            'content': '',
            'author': self.user.id  # Invalid: title/content required
        }
        print(f"[Request] POST {url} with data: {data}")
        # Send POST request with invalid data
        response = self.client.post(url, data)
        print(f"[Response] Status code: {response.status_code}")
        # Assert that invalid creation is blocked
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        print("[Assert] Invalid newsletter creation blocked.")


class CommentAPITests(APITestSetup):
    """
    API tests for the Comment model.
    Covers listing, creation, retrieval, update, deletion, unauthorized access,
    and invalid data scenarios for comments.
    """
    # Test listing comments via the API
    def test_list_comments(self):
        """
        Test listing comments via the API.
        Asserts that the response is successful and returns the comment list.
        """
        print("\n[Tests for listing comments via the API]")
        # Build the URL for listing comments
        url = reverse('comment-list')
        print(f"[Request] GET {url}")
        # Send GET request to the API
        response = self.client.get(url)
        print(f"[Response] Status code: {response.status_code}")
        # Assert that the response is successful
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        print("[Assert] Comment list returned successfully.")

    # Test retrieving a single comment via the API
    def test_retrieve_comment(self):
        """
        Test retrieving a single comment via the API.
        Asserts that the response is successful and returns the comment detail.
        """
        print("\n[Tests for retrieving a single comment via the API]")
        # Build the URL for retrieving the comment
        url = reverse('comment-detail', args=[self.comment.id])
        print(f"[Request] GET {url}")
        # Send GET request to retrieve the comment
        response = self.client.get(url)
        print(f"[Response] Status code: {response.status_code}")
        # Assert that the response is successful
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        print("[Assert] Comment detail returned successfully.")

    # Test updating a comment via the API
    def test_update_comment(self):
        """
        Test updating a comment via the API.
        Asserts that the comment is updated successfully.
        """
        print("\n[Tests for updating a comment via the API]")
        # Build the URL for updating the comment
        url = reverse('comment-detail', args=[self.comment.id])
        # Prepare the updated data
        data = {
            'content': 'Updated comment',
            'author': self.user.id,
            'article': self.article.id
        }
        print(f"[Request] PUT {url} with data: {data}")
        # Send PUT request to update the comment
        response = self.client.put(url, data)
        print(f"[Response] Status code: {response.status_code}")
        # Assert that the comment was updated successfully
        self.assertIn(
            response.status_code,
            [status.HTTP_200_OK, status.HTTP_202_ACCEPTED]
        )
        print("[Assert] Comment updated successfully.")

    # Test deleting a comment via the API
    def test_delete_comment(self):
        """
        Test deleting a comment via the API.
        Asserts that the comment is deleted successfully.
        """
        print("\n[Tests for deleting a comment via the API]")
        # Build the URL for deleting the comment
        url = reverse('comment-detail', args=[self.comment.id])
        print(f"[Request] DELETE {url}")
        # Send DELETE request to delete the comment
        response = self.client.delete(url)
        print(f"[Response] Status code: {response.status_code}")
        # Assert that the comment was deleted successfully
        self.assertIn(
            response.status_code,
            [status.HTTP_204_NO_CONTENT, status.HTTP_200_OK]
        )
        print("[Assert] Comment deleted successfully.")

    # Test unauthorized comment creation is blocked
    def test_unauthorized_create_comment(self):
        """
        Test that unauthorized comment creation is blocked by the API.
        """
        print("\n[Tests for unauthorized comment creation]")
        # Log out to simulate unauthorized user
        self.client.logout()
        # Build the URL for creating a comment
        url = reverse('comment-list')
        # Prepare the data for the new comment
        data = {
            'content': 'Should not work',
            'author': self.user.id,
            'article': self.article.id
        }
        print(f"[Request] POST {url} with data: {data} (unauthenticated)")
        # Send POST request as unauthorized user
        response = self.client.post(url, data)
        print(f"[Response] Status code: {response.status_code}")
        # Assert that unauthorized creation is blocked
        self.assertIn(
            response.status_code,
            [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN]
        )
        print("[Assert] Unauthorized comment creation blocked.")

    # Test creating a comment with invalid data is blocked
    def test_create_comment_invalid_data(self):
        """
        Test creating a comment with invalid data.
        Asserts that invalid creation is blocked by the API.
        """
        print("\n[Tests for creating a comment with invalid data]")
        # Build the URL for creating a comment
        url = reverse('comment-list')
        # Prepare invalid data (missing required fields)
        data = {
            'content': '',
            'author': self.user.id,
            'article': self.article.id  # Invalid: content required
        }
        print(f"[Request] POST {url} with data: {data}")
        # Send POST request with invalid data
        response = self.client.post(url, data)
        print(f"[Response] Status code: {response.status_code}")
        # Assert that invalid creation is blocked
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        print("[Assert] Invalid comment creation blocked.")

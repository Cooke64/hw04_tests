from http import HTTPStatus

from django.test import Client, TestCase
from django.urls import reverse

from ..models import Group, Post, User


STATUS_OK = HTTPStatus.OK
STATUS_NO = HTTPStatus.NOT_FOUND
STATUS_FOUND = HTTPStatus.FOUND


class URLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create_user(username='test_user')
        cls.no_author = User.objects.create_user(username='no_author')
        cls.group = Group.objects.create(
            title='Тестовый заголовок',
            slug='test-slug',
            description='Тестовый текст',
        )
        cls.post = Post.objects.create(
            author=cls.author,
            group=cls.group,
            text='Тестовый заголовок',
            pub_date='22.02.2022',
        )
        cls.guest_client = Client()
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.author)
        cls.authorized_client_1 = Client()
        cls.authorized_client_1.force_login(cls.no_author)

    def test_pages_exists_at_desired_location(self):
        """Страница доступна любому пользователю"""
        pages_url = {
            '/': STATUS_OK,
            '/group/test-slug/': STATUS_OK,
            '/profile/test_user/': STATUS_OK,
            '/posts/1/': STATUS_OK,
            '/about/author/': STATUS_OK,
            '/about/tech/': STATUS_OK,
        }

        for adress, http_status in pages_url.items():
            with self.subTest(adress=adress):
                response = self.guest_client.get(adress)
                self.assertEqual(response.status_code, http_status)

    def test_post_create_url_redirect_anonymous(self):
        """Страница create/ перенаправляет анонимного пользователя."""
        response = self.guest_client.post(
            reverse('post:create'),
        )
        self.assertRedirects(response, ('/auth/login/?next=/create/'))
        self.assertEqual(response.status_code, STATUS_FOUND)

    def test_post_edit_url_redirect_anonymous(self):
        """Страница post_edit/ перенаправляет анонимного пользователя."""
        response = self.guest_client.post(
            reverse('post:post_edit', kwargs={'post_id': '1'},)
        )
        self.assertRedirects(response, ('/auth/login/?next=/posts/1/edit/'))
        self.assertEqual(response.status_code, STATUS_FOUND)

    def test_urls_uses_correct_template(self):
        templates_url_names = {
            'posts/index.html': '',
            'posts/create_post.html': '/create/',
            'posts/post_detail.html': '/posts/1/',
            'posts/group_list.html': '/group/test-slug/',
            'posts/profile.html': '/profile/test_user/',
        }
        for template, url in templates_url_names.items():
            with self.subTest(url=url):
                response = self.authorized_client.get(url)
                self.assertTemplateUsed(response, template)

    def test_unknown_page_url_unexists_at_desired_location(self):
        """Страница не существует"""
        response = self.guest_client.get('/postss/')
        self.assertEqual(response.status_code, STATUS_NO)

    def test_post_edit_url_exists_at_desired_location(self):
        """Страница posts/<post_id>/edit/ доступна автору поста."""
        response = self.authorized_client.get('/posts/1/edit/')
        self.assertEqual(response.status_code, STATUS_OK)

    def test_no_author_of_post_cant_edit_post(self):
        """Страница posts/<post_id>/edit/ не доступна
         авторизованному пользователю, но не автору поста"""
        response = self.authorized_client_1.get('/posts/1/edit/')
        self.assertRedirects(response, '/posts/1/')
        self.assertEqual(response.status_code, STATUS_FOUND)

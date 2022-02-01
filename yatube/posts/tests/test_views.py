from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from django import forms

from ..models import Group, Post


User = get_user_model()


class ViewsTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create_user(username='test_user')
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

    def test_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_pages_names = {
            'posts/index.html': reverse('post:main'),
            'posts/group_list.html': (
                reverse('post:group', kwargs={'slug': 'test-slug'})
            ),
            'posts/profile.html': (
                reverse('post:profile', kwargs={'username': 'test_user'})
            ),
            'posts/post_detail.html': (
                reverse('post:post_detail', kwargs={'post_id': '1'})
            ),
            'posts/create_post.html': (
                reverse('post:post_edit', kwargs={'post_id': '1'})
            ),
        }
        for template, reverse_name in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_post_edit_show_correct_context(self):
        """Шаблон post_edit сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse('post:post_edit', kwargs={'post_id': '1'})
        )
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_post_index_page_show_correct_context(self):
        """Проверяем Context страницы index"""
        response = self.authorized_client.get(reverse('post:main'))
        first_object = response.context['page_obj'][0]
        context_objects = {
            self.author: first_object.author,
            self.post.text: first_object.text,
            self.group: first_object.group,
            self.post.id: first_object.id,
        }
        for reverse_name, response_name in context_objects.items():
            with self.subTest(reverse_name=reverse_name):
                self.assertEqual(response_name, reverse_name)

    def test_post_posts_groups_page_show_correct_context(self):
        """Проверяем Context страницы posts_groups"""
        response = self.authorized_client.get(
            reverse('post:group', kwargs={'slug': self.group.slug}))
        for post in response.context['page_obj']:
            self.assertEqual(post.group, self.group)

    def test_post_profile_page_show_correct_context(self):
        """Проверяем Context страницы profile"""
        response = self.authorized_client.get(
            reverse('post:profile', kwargs={'username': self.author.username}))
        for post in response.context['page_obj']:
            self.assertEqual(post.author, self.author)

    def test_create_page_show_correct_context(self):
        """Шаблон post_create сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse('post:create'))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

        def test_profile_page_list_is_1(self):
            """В шаблон profile передается верное количество постов"""
            response = self.authorized_client.get(
                reverse('post:profile',
                        kwargs={'username': ViewsTests.post.author}))
            object_all = response.context['page_obj']
            self.assertEqual(len(object_all), 1)

    def test_post_new_create(self):
        """При создании поста он должен появиться там,где следует"""
        exp_pages = [
            reverse('post:main'),
            reverse(
                'post:group', kwargs={'slug': self.group.slug}),
            reverse(
                'post:profile', kwargs={'username': self.author.username})
        ]
        for revers in exp_pages:
            with self.subTest(revers=revers):
                response = self.authorized_client.get(revers)
                self.assertIn(self.post, response.context['page_obj'])


class PaginatorViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create_user(username='test_user')
        cls.group = Group.objects.create(
            title='Тестовый заголовок',
            slug='test-slug',
            description='Тестовый текст',
        )
        for cls.post in range(1, 14):
            cls.post = Post.objects.create(
                author=cls.author,
                group=cls.group,
                text='Тестовый заголовок',
                pub_date='22.02.2022',
            )

    def test_first_page_contains_ten_records(self):
        # Проверка: на первой странице должно быть 10 постов.
        response = self.client.get(reverse('post:main'))
        self.assertEqual(len(response.context['page_obj']), 10)

    def test_second_page_contains_three_records(self):
        # Проверка: на второй странице должно быть три поста.
        response = self.client.get(reverse('post:main') + '?page=2')
        self.assertEqual(len(response.context['page_obj']), 3)

    def test_group_list_contains_ten_pages(self):
        # Проверка: на  странице group_list должно быть 10 постов.
        response = self.client.get(
            reverse('post:group', kwargs={'slug': 'test-slug'})
        )
        self.assertEqual(len(response.context['page_obj']), 10)

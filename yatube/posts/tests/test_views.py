from django import forms
from django.test import Client, TestCase
from django.urls import reverse

from ..forms import PostForm
from ..models import Group, Post, User


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
        cls.new_group = Group.objects.create(
            title='Тестовый заголовок 1',
            slug='test_slug_1',
            description='Тестовый текст 1',
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
        self.assertIsInstance(response.context.get('form'), PostForm)
        self.assertTrue('is_edit' in response.context)

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

    def test_post_profile_page_show_correct_context(self):
        """Проверяем Context страницы profile"""
        response = self.authorized_client.get(
            reverse('post:profile', kwargs={'username': self.author.username}))
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
        self.assertIsInstance(response.context.get('form'), PostForm)

    def test_profile_page_list_is_1(self):
        """В шаблон profile передается верное количество постов"""
        response = self.authorized_client.get(
            reverse('post:profile',
                    kwargs={'username': ViewsTests.post.author}))
        object_all = response.context['page_obj']
        self.assertEqual(len(object_all), 1)

    def test_post_new_create_appears_on_correct_pages(self):
        """При создании поста он должен появляется на главной странице,
        на странице выбранной группы и в профиле пользователя"""
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

    def test_posts_not_contain_in_wrong_group(self):
        """При создании поста он не появляется в другой группе"""
        post = Post.objects.get(pk=1)
        response = self.authorized_client.get(
            reverse('post:group', kwargs={'slug': self.new_group.slug})
        )
        self.assertNotIn(post, response.context['page_obj'].object_list)


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
        # bulk_create для создания
        # 13 объектов модели Post
        objs = [
            Post(
                author=cls.author,
                group=cls.group,
                text='Тестовый заголовок',
                pub_date='22.02.2022',
            )
            for bulk in range(1, 14)
        ]
        cls.post = Post.objects.bulk_create(objs)

    def test_first_page_contains_ten_records(self):
        """Проверка: на первой странице должно быть 10 постов."""
        response = self.client.get(reverse('post:main'))
        self.assertEqual(len(response.context['page_obj']), 10)

    def test_second_page_contains_three_records(self):
        """Проверка: на второй странице должно быть три поста."""
        response = self.client.get(reverse('post:main') + '?page=2')
        self.assertEqual(len(response.context['page_obj']), 3)

    def test_group_list_contains_ten_pages(self):
        """Проверка: на  странице group_list должно быть 10 постов."""
        response = self.client.get(
            reverse('post:group', kwargs={'slug': 'test-slug'})
        )
        self.assertEqual(len(response.context['page_obj']), 10)

    def test_profile_contains_ten_records(self):
        """Проверка: на  странице рофиля должно быть 10 постов."""
        response = self.client.get(reverse(
            'post:profile', kwargs={'username': self.author.username}))
        self.assertEqual(len(response.context['page_obj']), 10)

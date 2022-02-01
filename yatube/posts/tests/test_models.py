from django.test import TestCase

from ..models import Group, Post, User


class PostModelTest(TestCase):
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
            text='Очень длинный текст',
            pub_date='22.02.2022',
        )

    def test_post_model_have_correct_object_names(self):
        """Проверяем, что у модели Post
        and Group корректно работает __str__."""
        text = PostModelTest.post.text[:15]
        title = PostModelTest.group.title
        self.assertEqual(text, self.post.text)
        self.assertEqual(title, self.group.title)

    def test_group_model_have_correct_object_names(self):
        """Проверяем, что у модели Grouup корректно работает __str__."""
        group_title = PostModelTest.group
        title = group_title.title
        self.assertEqual(title, self.group.title)

    def test_verbose_name_post_model(self):
        """verbose_name в полях совпадает с ожидаемым."""
        post_text = PostModelTest.post
        field_verboses = {
            'text': 'Текст публикации',
            'pub_date': 'Дата публикации',
            'author': 'Автор',
            'group': 'Группа',

        }
        for field, expected_value in field_verboses.items():
            with self.subTest(field=field):
                self.assertEqual(
                    post_text._meta.get_field(field).verbose_name,
                    expected_value)

    def test_verbose_name_group_model(self):
        """verbose_name в полях совпадает с ожидаемым."""
        group = PostModelTest.group
        field_verboses = {
            'title': 'Название группы',
            'slug': 'URL',
            'description': 'Описание',
        }
        for field, expected_value in field_verboses.items():
            with self.subTest(field=field):
                self.assertEqual(
                    group._meta.get_field(field).verbose_name, expected_value)

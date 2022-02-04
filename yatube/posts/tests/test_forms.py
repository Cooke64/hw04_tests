import shutil
import tempfile

from django.conf import settings
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from posts.forms import PostForm
from posts.models import Post, Group, User

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostFormTest(TestCase):
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
        cls.form = PostForm()
        cls.guest_client = Client()
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.author)

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def test_form_create(self):
        """Валидная форма создает пост."""
        post_count = Post.objects.count()
        form_data = {
            'text': PostFormTest.post.text,
            'group': PostFormTest.group.id,
            'id': PostFormTest.post.id,
        }
        response_1 = self.guest_client.post(
            reverse('post:create'),
            data=form_data,
            follow=True
        )
        self.assertRedirects(response_1, ('/auth/login/?next=/create/'))
        response = self.authorized_client.post(
            reverse('post:create'),
            data=form_data,
            follow=True
        )
        self.assertRedirects(response, reverse(
            'post:profile', kwargs={'username': self.author.username}))

        self.assertEqual(Post.objects.count(), post_count + 1)
        self.assertTrue(
            Post.objects.filter(
                id=PostFormTest.post.id,
                text=PostFormTest.post.text,
                group=PostFormTest.group.id,
            ).exists()
        )

    def test_post_edit(self):
        """При отправке валидной формы пост редактируется."""
        text_edit = 'Отредактированный текст'
        posts_count = Post.objects.count()
        form_data = {
            'text': text_edit,
            'group': PostFormTest.group.id
        }
        response = self.guest_client.post(
            reverse('post:post_edit', kwargs={'post_id': '1'}),
            data=form_data,
            follow=True
        )
        self.assertRedirects(response, ('/auth/login/?next=/posts/1/edit/'))

        response_1 = self.authorized_client.post(
            reverse('post:post_edit',
                    kwargs={'post_id': PostFormTest.post.id}),
            data=form_data,
            follow=True
        )
        self.assertRedirects(response_1, reverse(
            'post:post_detail', kwargs={'post_id': PostFormTest.post.id}), )

        self.assertTrue(Post.objects.filter(
            group=PostFormTest.group.id,
            id=PostFormTest.post.id,
            text=text_edit,
        ).exists())
        self.assertEqual(Post.objects.count(), posts_count)

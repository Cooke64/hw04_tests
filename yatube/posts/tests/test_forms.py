import shutil
import tempfile

from django.contrib.auth import get_user_model
from posts.forms import PostForm
from posts.models import Post, Group
from django.conf import settings
from django.test import Client, TestCase, override_settings
from django.urls import reverse

User = get_user_model()
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

    def test_create_task(self):
        tasks_count = Post.objects.count()
        form_data = {
            'text': PostFormTest.post.text,
            'group': PostFormTest.group.id,
            'id': PostFormTest.post.id,
        }
        self.authorized_client.post(
            reverse('post:post_detail', kwargs={'post_id': '1'}),
            data=form_data,
        )

        self.assertEqual(Post.objects.count(), tasks_count)
        self.assertTrue(
            Post.objects.filter(
                id=PostFormTest.post.id,
                text=PostFormTest.post.text,
                group=PostFormTest.group.id,
            ).exists()
        )

    def test_post_edit(self):
        posts_count = Post.objects.count()
        form_data = {
            'text': 'а',
            'group': PostFormTest.group.id
        }
        self.authorized_client.post(
            reverse('post:post_detail', kwargs={'post_id': '1'}),
            data=form_data,
        )
        self.assertTrue(Post.objects.filter(
            group=PostFormTest.group.id,
            id=PostFormTest.post.id,
            text=PostFormTest.post.text,
        ).exists())
        self.assertEqual(Post.objects.count(), posts_count)

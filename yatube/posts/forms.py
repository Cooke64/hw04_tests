from django import forms

from .models import Post


class PostForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['group'].empty_label = 'Категория не выбрана'

    class Meta:
        model = Post
        fields = ['text', 'group']
        label = {
            'text': 'Содержание',
            'group': 'Группа',
        }
        help_text = {
            'text': 'Текст поста',
            'group': 'Группа,к которой будет относиться пост',
        }

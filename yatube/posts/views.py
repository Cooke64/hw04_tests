from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import render, get_object_or_404, redirect

from .forms import PostForm
from .models import Post, User, Group

AMOUNT_POST = 10


def index(request):
    template = 'posts/index.html'
    title = 'Последние обновления на сайте'
    post_list = Post.objects.all().order_by('-pub_date')
    paginator = Paginator(post_list, AMOUNT_POST)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'page_obj': page_obj,
        'title': title,
    }
    return render(request, template, context)


def profile(request, username):
    author = get_object_or_404(User, username=username)
    post_list = author.posts.all()
    paginator = Paginator(post_list, AMOUNT_POST)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    counter_posts = author.posts.count()
    context = {
        'author': author,
        'page_obj': page_obj,
        'counter_posts': counter_posts,

    }
    template = 'posts/profile.html'
    return render(request, template, context)


def group_posts(request, slug):
    template = 'posts/group_list.html'
    title = 'Записи сообщества'
    group = get_object_or_404(Group, slug=slug)
    get_posts = Post.objects.filter(group=group)
    posts = get_posts.order_by('-pub_date')[:AMOUNT_POST]
    paginator = Paginator(posts, AMOUNT_POST)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'page_obj': page_obj,
        'title': title,
        'group': group,
        'posts': posts,
    }
    return render(request, template, context)


# Исправлено в шаблоне post_detail
def post_detail(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    username_obj = User.objects.get(username=post.author)
    posts_counter = username_obj.posts.count()
    template = 'posts/post_detail.html'
    title = 'Подробная информация'
    context = {
        'title': title,
        'post': post,
        'posts_counter': posts_counter
    }
    return render(request, template, context)


@login_required
def post_create(request):
    form = PostForm(request.POST)
    if form.is_valid():
        post = form.save(commit=False)
        post.author = request.user
        post.save()
        return redirect('post:profile', request.user)
    return render(request, 'posts/create_post.html', {'form': form})


@login_required
def post_edit(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    form = PostForm(request.POST, instance=post)
    if post.author != request.user:
        return redirect('post:post_detail', post_id=post_id)
    if form.is_valid():
        post.save()
        return redirect('post:post_detail', post.pk,)
    is_edit = True
    context = {'form': form, 'is_edit': is_edit}
    return render(request, 'posts/create_post.html', context)

# Второй вариант реализации подробнее и мне понятнее,чем первый.
# @login_required
# def post_edit(request, post_id):
#     post = get_object_or_404(Post, pk=post_id)
#     if post.author != request.user:
#         return redirect('post:post_detail', post_id=post_id)
#     elif request.method == 'POST':
#         form = PostForm(request.POST, instance=post)
#         form.save()
#         return redirect('post:post_detail', post_id=post_id)
#     else:
#         form = PostForm(initial={'group': post.group, 'text': post.text})
#     is_edit = True
#     context = {'form': form, 'is_edit': is_edit, 'post': post}
#     return render(request, 'posts/create_post.html', context)

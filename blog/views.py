# views.py

from django.shortcuts import render, get_object_or_404
from .models import Post
from django.http import HttpResponseRedirect
from .forms import PostForm, CategoryForm
from django.urls import reverse
from django.shortcuts import redirect

def post_list(request):
    posts = Post.objects.all().order_by('-created_at')
    return render(request, 'blog/post_list.html', {'posts': posts})

def post_detail(request, slug):
    post = get_object_or_404(Post, slug=slug)
    return render(request, 'blog/post_detail.html', {'post': post})

def create_post(request):
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)  # Pastikan menggunakan request.FILES
        if form.is_valid():
            post = form.save()
            return HttpResponseRedirect(post.get_absolute_url())
        else:
            print("Form is not valid")
            print(form.errors)
    else:
        form = PostForm()
    return render(request, 'blog/post_form.html', {'form': form})

def delete_post(request, slug):
    post = get_object_or_404(Post, slug=slug)
    if request.method == 'POST':
        post.delete()
        return redirect('blog:post_list')
    return render(request, 'blog/post_confirm_delete.html', {'post': post})

def edit_post(request, slug):
    post = get_object_or_404(Post, slug=slug)
    if request.method == 'POST':
        form = PostForm(request.POST, instance=post)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(post.get_absolute_url())
    else:
        form = PostForm(instance=post)
    return render(request, 'blog/post_form.html', {'form': form})

def dashboard(request):
    return render(request, 'blog/dashboard.html')

def add_category(request):
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('blog:dashboard')
        else:
            return render(request, 'blog/add_category.html', {'form': form})
    else:
        form = CategoryForm()
        return render(request, 'blog/add_category.html', {'form': form})

def post_table(request):
    posts = Post.objects.all().order_by('-created_at')
    return render(request, 'blog/post_table.html', {'posts': posts})

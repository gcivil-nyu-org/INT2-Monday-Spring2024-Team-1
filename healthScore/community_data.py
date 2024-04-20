from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse

from .models import (
    Post,
    Comment,
)

from .forms import PostForm, CommentForm


@login_required(login_url="/")
def community_home(request):
    return redirect("all_posts")


@login_required(login_url="/")
def view_all_posts(request):
    posts = Post.objects.all().order_by("-createdAt")
    posts_with_status_info = [
        {
            "id": post.id,
            "title": post.title,
            "description": post.description,
            "createdAt": post.createdAt,
            "is_healthcare_worker": post.user.is_healthcare_worker,
        }
        for post in posts
    ]
    return render(
        request,
        "community_home.html",
        {"posts": posts_with_status_info, "headerTitle": "All the posts"},
    )


@login_required(login_url="/")
def view_my_posts(request):
    posts = Post.objects.filter(user=request.user).order_by("-createdAt")
    return render(
        request, "community_home.html", {"posts": posts, "headerTitle": "My posts"}
    )


@login_required(login_url="/")
def view_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    comments = post.comments.all()
    return render(request, "post_details.html", {"post": post, "comments": comments})


@login_required(login_url="/")
def create_post(request):
    if request.method == "POST":
        form = PostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.user = request.user
            post.save()
            return redirect("community")
    else:
        form = PostForm()
    return render(request, "post_create.html", {"form": form})


@login_required(login_url="/")
def edit_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    if request.method == "POST":
        form = PostForm(request.POST, instance=post)
        if form.is_valid():
            form.save()
            return redirect("view_post", post_id=post.id)
    else:
        form = PostForm(instance=post)
    return render(request, "post_edit.html", {"form": form})


@login_required(login_url="/")
def delete_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    if request.method == "GET":
        post.delete()
        return redirect("community")
    return redirect("view_post", post_id=post_id)


@login_required(login_url="/")
def create_comments(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    if request.method == "POST":
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = post
            comment.commenter = request.user
            comment.save()

    return redirect("view_post", post_id=post.id)


@login_required(login_url="/")
def delete_comment(request, comment_id):
    userID = request.user.id
    comment = get_object_or_404(Comment, id=comment_id)

    if comment.post.user.id != userID and comment.commenter.id != userID:
        return JsonResponse({"error": "Unauthorized"}, status=401)

    if request.method == "GET":
        comment.delete()

    return redirect("view_post", post_id=comment.post.id)

from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify
from flask_login import login_required, current_user
from .models import Post, User, Comment, Like, Message
from . import db

views = Blueprint("views", __name__)


@views.route("/")
@views.route("/home")
def home():
    posts = Post.query.all()
    return render_template("home.html", user=current_user, posts=posts)


@views.route("/create-post", methods=['GET', 'POST'])
@login_required
def create_post():
    if request.method == "POST":
        title = request.form.get('title')
        content = request.form.get('content')

        if not title:
            flash('Post cannot be empty', category='error')
        else:
           post = Post(title=title, content=content, author=current_user.id)
           try:
            db.session.add(post)
            db.session.commit()
           except:
            db.session.rollback()
            flash('Post can not be added, try again.', category='error')

        return redirect(url_for('views.home'))

    return render_template('create_post.html', user=current_user)


@views.route("/delete-post/<id>")
@login_required
def delete_post(id):
    post = Post.query.filter_by(id=id).first()

    if not post:
        flash("Post does not exist.", category='error')
    elif current_user.id != post.id:
        flash('You do not have permission to delete this post.', category='error')
    else:
        db.session.delete(post)
        db.session.commit()
        flash('Post deleted.', category='success')

    return redirect(url_for('views.home'))


@views.route("/posts/<username>")
@login_required
def posts(username):
    user = User.query.filter_by(username=username).first()

    if not user:
        flash('No user with that username exists.', category='error')
        return redirect(url_for('views.home'))

    posts = user.posts
    return render_template("posts.html", user=current_user, posts=posts, username=username)


@views.route("/create-comment/<int:post_id>", methods=['POST'])
@login_required
def create_comment(post_id):
    content = request.form.get('text')

    if not content:
        flash('Comment cannot be empty.', category='error')
    else:
        post = Post.query.filter_by(id=post_id).first()
        if post:
            comment = Comment(
                content=content, author=current_user.id, post_id=post_id)
            try:
                db.session.add(comment)
                db.session.commit()
            except:
                db.session.rollback()
        else:
            flash('Post can not be added, try again.', category='error')

        return redirect(url_for('views.home'))

    return redirect(url_for('views.home'))


@views.route("/delete-comment/<comment_id>")
@login_required
def delete_comment(comment_id):
    comment = Comment.query.filter_by(id=comment_id).first()

    if not comment:
        flash('Comment does not exist', category='error')
    elif current_user.id != comment.author and current_user.id != comment.post.author:
        flash('You do not have permission to delete this comment', category='error')
    else:
        db.session.delete(comment)
        db.session.commit()

    return redirect(url_for('views.home'))


@views.route("/like-post/<post_id>", methods=['POST'])
def like(post_id):
    post = Post.query.filter_by(id=post_id).first()
    like = Like.query.filter_by(author=current_user.id, post_id=post_id).first()

    if not post:
        return jsonify({'error': 'Post does not exist'}, 400)
    elif like:
        db.session.delete(like)
        db.session.commit()
    else:
        like = Like(author=current_user.id, post_id=post_id)
        db.session.add(like)
        db.session.commit()

    return jsonify({"likes": len(post.likes), "liked": current_user.id in map(lambda x: x.author, post.likes)})


@views.route("/about")
def about():
    return render_template('about.html', user=current_user)


@views.route('/edit/<int:id>/', methods=['GET', 'POST'])
@login_required
def edit(id):
    post_to_edit = Post.query.get_or_404(id)

    if current_user.username != post_to_edit.author:
        if request.method == 'POST':
            post_to_edit.title = request.form.get('title')
            post_to_edit.content = request.form.get('content')

            db.session.commit()

            flash("Your changes have been saved.")
            return redirect(url_for('views.home', id=post_to_edit.id))

        return render_template('edit.html', user=current_user, post=post_to_edit)

    flash("You cannot edit another user's article.")
    return redirect(url_for('views.home'))


@views.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        sender = request.form.get('name')
        email = request.form.get('email')
        title = request.form.get('title')
        phone = request.form.get('tel')
        message = request.form.get('message')

        new_message = Message(sender=sender, email=email,
                              title=title, message=message, phone=phone)
        db.session.add(new_message)
        db.session.commit()

        flash("Message sent. Thanks for reaching out!")
        return redirect(url_for('views.home'))

    return render_template('contact.html', user=current_user)

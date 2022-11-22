from app import app, db
from app.models import User, Post
from app.forms import LoginForm, RegistrationForm, EditProfileForm, PostForm
from app.forms import ResetPasswordRequestForm, ResetPasswordForm
from flask import render_template, flash, redirect, url_for, request
from flask_login import current_user, login_user, logout_user, login_required
from werkzeug.urls import url_parse
from datetime import datetime

realtime = str(datetime.today())
menu = [{"title": "Main", "url": "/"},
        {"title": "Чат", "url": "/explore"},
        {"title": "Про сайт", "url": "/about"},
        {"title": realtime[0:-10], "url": "/"},]


@app.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()


@app.route('/', methods=['GET', 'POST'])  # ГОЛОВНА
@app.route('/index', methods=['GET', 'POST'])
@login_required
def index():
    form = PostForm()
    if form.validate_on_submit():
        post = Post(body=form.post.data, author=current_user)
        db.session.add(post)
        db.session.commit()
        flash("Повідомлення опубліковано")
        return redirect(url_for('index'))

    page = request.args.get('page', 1, type=int)  # Розбивка на сторінки з постами
    posts = current_user.followed_posts().paginate(page=page, per_page=app.config['POSTS_PER_PAGE'], error_out=False)
    next_url = url_for('index', page=posts.next_num) \
        if posts.has_next else None
    prev_url = url_for('index', page=posts.prev_num) \
        if posts.has_prev else None

    return render_template('index.html', title='Головна', form=form, menu=menu, posts=posts.items,
                           next_url=next_url, prev_url=prev_url)


@app.route('/explore')  # Усі пости
@login_required
def explore():
    page = request.args.get('page', 1, type=int)
    posts = Post.query.order_by(Post.timestamp.desc()).paginate(page=page, per_page=app.config['POSTS_PER_PAGE'], error_out=False)
    next_url = url_for('explore', page=posts.next_num) \
        if posts.has_next else None
    prev_url = url_for('explore', page=posts.prev_num) \
        if posts.has_prev else None

    return render_template('index.html', title='Чат', menu=menu, posts=posts.items,
                           next_url=next_url, prev_url=prev_url)


@app.route('/register', methods=['GET', 'POST'])  # Register
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()

    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data, nickname=form.nickname.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash("Ви успішно зареєствувались!")
        return redirect(url_for('login'))
    return render_template('register.html', title='Реєстрація', form=form, menu=menu)


@app.route('/login', methods=['GET', 'POST'])  # Login
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()

        if user is None or not user.check_password(form.password.data):
            flash("Неправильне ім'я або пароль")
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')

        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('index')
        return redirect(next_page)
    return render_template('login.html', title='Увійти', form=form, menu=menu)


@app.route('/logout')  # Exit
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/user/<username>')  # Profile
@login_required
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    page = request.args.get('page', 1, type=int)
    posts = user.posts.order_by(Post.timestamp.desc()).paginate(page=page, per_page=app.config['POSTS_PER_PAGE'], error_out=False)

    next_url = url_for('user', username=user.username, page=posts.next_num) \
        if posts.has_next else None
    prev_url = url_for('user', username=user.username, page=posts.prev_num) \
        if posts.has_prev else None
    return render_template('profile/user.html', title='Профіль', user=user, menu=menu, posts=posts.items,
                           next_url=next_url, prev_url=prev_url)


@app.route('/edit_profile', methods=['GET', 'POST'])  # Edit profile
@login_required
def edit_profile():
    form = EditProfileForm(current_user.username)
    if form.validate_on_submit():
        current_user.nickname = form.nickname.data
        current_user.username = form.username.data
        current_user.about_me = form.about_me.data
        db.session.commit()
        flash("Зміни збережено")
        return redirect(url_for('user', username=current_user.username))
    elif request.method == 'GET':
        form.nickname.data = current_user.nickname
        form.username.data = current_user.username
        form.about_me.data = current_user.about_me
    return render_template('profile/edit_profile.html', title='Редагувати Профіль', form=form, menu=menu)


@app.route('/about')
def about():
    return render_template('about.html', title='Це мій мікроблог на Flask', menu=menu)


@app.route('/follow/<username>')  # ПІДПИСКА
@login_required
def follow(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash(f"Користувача {username} не знайдено")
        return redirect(url_for('index'))
    if user == current_user:
        flash("Ви не можете підписатися на себе")
        return redirect(url_for('user', username=username))
    current_user.follow(user)
    db.session.commit()
    flash(f"Ви підписалися на {username}!")
    return redirect(url_for('user', username=username))


@app.route('/unfollow/<username>')  # ВІДПИСКА
@login_required
def unfollow(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash(f"Користувача {username} не знайдено")
        return redirect(url_for('index'))
    if user == current_user:
        flash("Ви не можете відписатися від себе")
        return redirect(url_for('user', username=username))
    current_user.unfollow(user)
    db.session.commit()
    flash(f"Ви відписалися від {username}")
    return redirect(url_for('user', username=current_user.username))

@app.route('/reset')
def reset_password_request():
    pass


@app.errorhandler(404)  # Error 404
def pageNotFount(error):
    return render_template('error/404.html', title="Сторінку не знайдено", menu=menu), 404


@app.errorhandler(500)  # Error 500
def internal_error(error):
    db.session.rollback()
    return render_template('error/500.html'), 500

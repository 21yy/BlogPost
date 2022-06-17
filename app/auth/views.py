from flask import render_template, redirect, request, url_for, flash
from flask_login import login_user, login_required, logout_user
from . import auth
from ..models import User
from .forms import LoginForm


@auth.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        email = form.data['email']
        user = User.query.filter_by(email=email).first()
        if user is not None and user.verify_password(form.password.data):
            login_user(user)
            flash(u'welcome back，%s!' % user.username, 'success')
            return redirect(request.args.get('next') or url_for('main.index'))
        else:
            flash(u'sign in failed! username or password incorrect', 'danger')
    if form.errors:
        flash(u'sign in failed, please sign in again.', 'danger')

    return render_template('auth/login.html', form=form)


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash(u'log out!。', 'success')
    return redirect(url_for('main.index'))
from datetime import datetime
import json
from flask import render_template, redirect, flash, \
    url_for, request, current_app, jsonify
from flask_login import login_required, current_user
from . import admin
from ..models import ArticleType, Source, Article, \
    Comment, User, Follow, Menu, ArticleTypeSetting, BlogInfo
from .forms import SubmitArticlesForm, ManageArticlesForm, DeleteArticleForm, \
    DeleteArticlesForm, AdminCommentForm, DeleteCommentsForm, AddArticleTypeForm, \
    EditArticleTypeForm, AddArticleTypeNavForm, EditArticleNavTypeForm, SortArticleNavTypeForm, \
    CustomBlogInfoForm, ChangePasswordForm, EditUserInfoForm
from .. import db


@admin.route('/')
@login_required
def manager():
    return redirect(url_for('admin.custom_blog_info'))


@admin.route('/submit-articles', methods=['GET', 'POST'])
@login_required
def submitArticles():
    form = SubmitArticlesForm()

    sources = [(s.id, s.name) for s in Source.query.all()]
    form.source.choices = sources
    types = [(t.id, t.name) for t in ArticleType.query.all()]
    form.types.choices = types

    if form.validate_on_submit():
        title = form.title.data
        source_id = form.source.data
        content = form.content.data
        type_id = form.types.data
        summary = form.summary.data

        source = Source.query.get(source_id)
        articleType = ArticleType.query.get(type_id)

        if source and articleType:
            article = Article(title=title, content=content, summary=summary,
                              source=source, articleType=articleType)
            db.session.add(article)
            db.session.commit()
            flash(u'post succeed！', 'success')
            article_id = Article.query.filter_by(title=title).first().id
            return redirect(url_for('main.articleDetails', id=article_id))
    if form.errors:
        flash(u'post failed', 'danger')

    return render_template('admin/submit_articles.html', form=form)


@admin.route('/edit-articles/<int:id>', methods=['GET', 'POST'])
@login_required
def editArticles(id):
    article = Article.query.get_or_404(id)
    form = SubmitArticlesForm()

    sources = [(s.id, s.name) for s in Source.query.all()]
    form.source.choices = sources
    types = [(t.id, t.name) for t in ArticleType.query.all()]
    form.types.choices = types

    if form.validate_on_submit():
        articleType = ArticleType.query.get_or_404(int(form.types.data))
        article.articleType = articleType
        source = Source.query.get_or_404(int(form.source.data))
        article.source = source

        article.title = form.title.data
        article.content = form.content.data
        article.summary = form.summary.data
        article.update_time = datetime.utcnow()
        db.session.add(article)
        db.session.commit()
        flash(u'post updated！', 'success')
        return redirect(url_for('main.articleDetails', id=article.id))
    form.source.data = article.source_id
    form.title.data = article.title
    form.content.data = article.content
    form.types.data = article.articleType_id
    form.summary.data = article.summary
    return render_template('admin/submit_articles.html', form=form)


@admin.route('/manage-articles', methods=['GET', 'POST'])
@login_required
def manage_articles():
    types_id = request.args.get('types_id', -1, type=int)
    source_id = request.args.get('source_id', -1, type=int)
    form = ManageArticlesForm(request.form, types=types_id, source=source_id)
    form2 = DeleteArticleForm()  # for delete an article
    from3 = DeleteArticlesForm()  # for delete articles

    types = [(t.id, t.name) for t in ArticleType.query.all()]
    types.append((-1, u'all categories'))
    form.types.choices = types
    sources = [(s.id, s.name) for s in Source.query.all()]
    sources.append((-1, u'all source'))
    form.source.choices = sources

    pagination_search = 0

    if form.validate_on_submit() or \
            (request.args.get('types_id') is not None and request.args.get('source_id') is not None):
        if form.validate_on_submit():
            types_id = form.types.data
            source_id = form.source.data
            page = 1
        else:
            types_id = request.args.get('types_id', type=int)
            source_id = request.args.get('source_id', type=int)
            form.types.data = types_id
            form.source.data = source_id
            page = request.args.get('page', 1, type=int)

        result = Article.query.order_by(Article.create_time.desc())
        if types_id != -1:
            articleType = ArticleType.query.get_or_404(types_id)
            result = result.filter_by(articleType=articleType)
        if source_id != -1:
            source = Source.query.get_or_404(source_id)
            result = result.filter_by(source=source)
        pagination_search = result.paginate(
                page, per_page=current_app.config['ARTICLES_PER_PAGE'], error_out=False)

    if pagination_search != 0:
        pagination = pagination_search
        articles = pagination_search.items
    else:
        page = request.args.get('page', 1, type=int)
        pagination = Article.query.order_by(Article.create_time.desc()).paginate(
                page, per_page=current_app.config['ARTICLES_PER_PAGE'],
                error_out=False)
        articles = pagination.items

    return render_template('admin/manage_articles.html', Article=Article,
                           articles=articles, pagination=pagination,
                           endpoint='admin.manage_articles',
                           form=form, form2=form2, form3=from3,
                           types_id=types_id, source_id=source_id, page=page)


@admin.route('/manage-articles/delete-article', methods=['GET', 'POST'])
@login_required
def delete_article():
    types_id = request.args.get('types_id', -1, type=int)
    source_id = request.args.get('source_id', -1, type=int)
    form = DeleteArticleForm()

    if form.validate_on_submit():
        articleId = int(form.articleId.data)
        article = Article.query.get_or_404(articleId)
        count = article.comments.count()
        for comment in article.comments:
            db.session.delete(comment)
        db.session.delete(article)
        try:
            db.session.commit()
        except:
            db.session.rollback()
            flash(u'delete failed！', 'danger')
        else:
            flash(u'delete post and %s comments！' % count, 'success')
    if form.errors:
        flash(u'delete failed！', 'danger')

    return redirect(url_for('admin.manage_articles', types_id=types_id, source_id=source_id,
                            page=request.args.get('page', 1, type=int)))


@admin.route('/manage-articles/delete-articles', methods=['GET', 'POST'])
@login_required
def delete_articles():
    types_id = request.args.get('types_id', -1, type=int)
    source_id = request.args.get('source_id', -1, type=int)
    form = DeleteArticlesForm()

    if form.validate_on_submit():
        articleIds = json.loads(form.articleIds.data)
        count = 0
        for articleId in articleIds:
            article = Article.query.get_or_404(int(articleId))
            count += article.comments.count()
            for comment in article.comments:
                db.session.delete(comment)
            db.session.delete(article)
        try:
            db.session.commit()
        except:
            db.session.rollback()
            flash(u'delete failed！', 'danger')
        else:
            flash(u'delete %s posts and %s comments！' % (len(articleIds), count), 'success')
    if form.errors:
        flash(u'delete failed！', 'danger')

    return redirect(url_for('admin.manage_articles', types_id=types_id, source_id=source_id,
                            page=request.args.get('page', 1, type=int)))


@admin.route('/manage-comments/disable/<int:id>')
@login_required
def disable_comment(id):
    comment = Comment.query.get_or_404(id)
    comment.disabled = True
    db.session.add(comment)
    db.session.commit()
    flash(u'block comments！', 'success')
    if request.args.get('disable_type') == 'admin':
        page = request.args.get('page', 1, type=int)
        return redirect(url_for('admin.manage_comments',
                                page=page))

    return redirect(url_for('main.articleDetails',
                            id=comment.article_id,
                            page=request.args.get('page', 1, type=int)))


@admin.route('/manage-comments/enable/<int:id>')
@login_required
def enable_comment(id):
    comment = Comment.query.get_or_404(id)
    comment.disabled = False
    db.session.add(comment)
    db.session.commit()
    flash(u'unblock comments！', 'success')
    if request.args.get('enable_type') == 'admin':
        page = request.args.get('page', 1, type=int)
        return redirect(url_for('admin.manage_comments',
                                page=page))

    return redirect(url_for('main.articleDetails',
                            id=comment.article_id,
                            page=request.args.get('page', 1, type=int)))


@admin.route('/manage-comments/delete-comment/<int:id>')
@login_required
def delete_comment(id):
    comment = Comment.query.get_or_404(id)
    article_id = comment.article_id
    db.session.delete(comment)
    try:
        db.session.commit()
    except:
        db.session.rollback()
        flash(u'delete comment failed！', 'danger')
    else:
        flash(u'delete comment succeed！', 'success')
    if request.args.get('delete_type') == 'admin':
        page = request.args.get('page', 1, type=int)
        return redirect(url_for('admin.manage_comments',
                                page=page))

    return redirect(url_for('main.articleDetails',
                            id=article_id,
                            page=request.args.get('page', 1, type=int)))


@admin.route('/manage-comments', methods=['GET', 'POST'])
@login_required
def manage_comments():
    form = AdminCommentForm(follow=-1, article=-1)
    form2 = DeleteCommentsForm(commentIds=-1)

    if form.validate_on_submit():
        article = Article.query.get_or_404(int(form.article.data))
        comment = Comment(article=article,
                          content=form.content.data,
                          author_name=form.name.data,
                          author_email=form.email.data)
        db.session.add(comment)
        db.session.commit()

        followed = Comment.query.get_or_404(int(form.follow.data))
        f = Follow(follower=comment, followed=followed)
        comment.comment_type = 'reply'
        comment.reply_to = followed.author_name
        db.session.add(f)
        db.session.add(comment)
        db.session.commit()
        flash(u'comment post！', 'success')
        return redirect(url_for('.manage_comments'))
    if form.errors:
        flash(u'comment post failed！', 'danger')
        return redirect(url_for('.manage_comments'))

    page = request.args.get('page', 1, type=int)
    pagination = Comment.query.order_by(Comment.timestamp.desc()).paginate(
        page, per_page=current_app.config['COMMENTS_PER_PAGE'],
        error_out=False)
    comments = pagination.items
    return render_template('admin/manage_comments.html', User=User,
                           Comment=Comment, comments=comments,
                           pagination=pagination, page=page,
                           endpoint='.manage_comments', form=form, form2=form2)


@admin.route('/manage-comments/delete-comments', methods=['GET', 'POST'])
@login_required
def delete_comments():
    form2 = DeleteCommentsForm(commentIds=-1)

    if form2.validate_on_submit():
        commentIds = json.loads(form2.commentIds.data)
        count = 0
        for commentId in commentIds:
            comment = Comment.query.get_or_404(int(commentId))
            count += 1
            db.session.delete(comment)
        try:
            db.session.commit()
        except:
            db.session.rollback()
            flash(u'delete failed!', 'danger')
        else:
            flash(u'delete %s comments!' % count , 'success')
    if form2.errors:
        flash(u'delete failed!', 'danger')

    page = request.args.get('page', 1, type=int)
    return redirect(url_for('.manage_comments', page=page))


@admin.route('/manage-articleTypes', methods=['GET', 'POST'])
@login_required
def manage_articleTypes():
    form = AddArticleTypeForm(menus=-1)
    form2= EditArticleTypeForm()

    menus = Menu.return_menus()
    return_setting_hide = ArticleTypeSetting.return_setting_hide()
    form.menus.choices = menus
    form.setting_hide.choices = return_setting_hide
    form2.menus.choices = menus
    form2.setting_hide.choices = return_setting_hide

    page = request.args.get('page', 1, type=int)
    # sub_type = request.args.get('type')

    if form.validate_on_submit():
        name = form.name.data
        articleType = ArticleType.query.filter_by(name=name).first()
        if articleType:
            flash(u'add category failed！current name exist。', 'danger')
        else:
            introduction = form.introduction.data
            setting_hide = form.setting_hide.data
            menu = Menu.query.get(form.menus.data)
            if not menu:
               menu = None
            articleType = ArticleType(name=name, introduction=introduction, menu=menu,
                                      setting=ArticleTypeSetting(name=name))
            if setting_hide == 1:
                articleType.setting.hide = True
            if setting_hide == 2:
                articleType.setting.hide = False
            # Note: to check whether introduction or menu is existing or not,
            # just use if `articleType.introduction` or `if articleType.menu`.
            db.session.add(articleType)
            db.session.commit()
            flash(u'add category succeed！', 'success')
        return redirect(url_for('.manage_articleTypes'))
    if form.errors:
        flash(u'add category failed!。', 'danger')
        return redirect(url_for('.manage_articleTypes'))

    pagination = ArticleType.query.order_by(ArticleType.id.desc()).paginate(
        page, per_page=current_app.config['COMMENTS_PER_PAGE'],
        error_out=False)
    articleTypes = pagination.items
    return render_template('admin/manage_articleTypes.html', articleTypes=articleTypes,
                           pagination=pagination, endpoint='.manage_articleTypes',
                           form=form, form2=form2, page=page)



@admin.route('/manage-articletypes/edit-articleType', methods=['POST'])
def edit_articleType():
    form2= EditArticleTypeForm()

    menus = Menu.return_menus()
    setting_hide = ArticleTypeSetting.return_setting_hide()
    form2.menus.choices = menus
    form2.setting_hide.choices = setting_hide

    page = request.args.get('page', 1, type=int)

    if form2.validate_on_submit():
        name = form2.name.data
        articleType_id = int(form2.articleType_id.data)
        articleType = ArticleType.query.get_or_404(articleType_id)
        setting_hide = form2.setting_hide.data

        if articleType.is_protected:
            if form2.name.data != articleType.name or \
                            form2.introduction.data != articleType.introduction:
                flash(u'This operation is not allowed!', 'danger')
            else:
                menu = Menu.query.get(form2.menus.data)
                if not menu:
                    menu = None
                articleType.menu = menu
                if setting_hide == 1:
                    articleType.setting.hide = True
                if setting_hide == 2:
                    articleType.setting.hide = False
                db.session.add(articleType)
                db.session.commit()
                flash(u'edit default category succeed！', 'success')
        elif ArticleType.query.filter_by(name=form2.name.data).first() \
            and ArticleType.query.filter_by(name=form2.name.data).first().id != articleType_id:
                flash(u'edit failed! current name exist.', 'danger')
        else:
            introduction = form2.introduction.data
            menu = Menu.query.get(form2.menus.data)
            if not menu:
               menu = None
            articleType = ArticleType.query.get_or_404(articleType_id)
            articleType.name = name
            articleType.introduction = introduction
            articleType.menu = menu
            if not articleType.setting:
                articleType.setting = ArticleTypeSetting(name=articleType.name)
            if setting_hide == 1:
                    articleType.setting.hide = True
            if setting_hide == 2:
                articleType.setting.hide = False

            db.session.add(articleType)
            db.session.commit()
            flash(u'edit succeed！', 'success')
        return redirect(url_for('.manage_articleTypes', page=page))
    if form2.errors:
        flash(u'edit failed!', 'danger')
        return redirect(url_for('.manage_articleTypes', page=page))


@admin.route('/manage-articleTypes/delete-articleType/<int:id>')
@login_required
def delete_articleType(id):
    page = request.args.get('page', 1, type=int)

    articleType = ArticleType.query.get_or_404(id)
    if articleType.is_protected:
        flash(u'warning：you are not allowed to delete it！', 'danger')
        return redirect(url_for('admin.manage_articleTypes', page=page))
    count = 0
    systemType = ArticleTypeSetting.query.filter_by(protected=True).first().types.first()
    articleTypeSetting = ArticleTypeSetting.query.get(articleType.setting_id)
    for article in articleType.articles.all():
        count += 1
        article.articleType_id = systemType.id
        db.session.add(article)
        db.session.commit()
    if articleTypeSetting:
        db.session.delete(articleTypeSetting)
    db.session.delete(articleType)
    try:
        db.session.commit()
    except:
        db.session.rollback()
        flash(u'delete category failed！', 'danger')
    else:
        flash(u'delete category succeed！Total %s posts in this category move to non-category.' % count, 'success')
    return redirect(url_for('admin.manage_articleTypes', page=page))


@admin.route('/manage-articleTypes/get-articleType-info/<int:id>')
@login_required
def get_articleType_info(id):
    if request.blueprint:
        articletype = ArticleType.query.get_or_404(id)
        if articletype.is_hide:
            setting_hide = 1
        else:
            setting_hide = 2
        return jsonify({
            'name': articletype.name,
            'setting_hide': setting_hide,
            'introduction': articletype.introduction,
            'menu': articletype.menu_id or -1
        })


@admin.route('/manage-articleTypes/nav', methods=['GET', 'POST'])
@login_required
def manage_articleTypes_nav():
    form = AddArticleTypeNavForm()
    form2 = EditArticleNavTypeForm()
    form3 = SortArticleNavTypeForm()

    page = request.args.get('page', 1, type=int)
    if form.validate_on_submit():
        name = form.name.data
        menu = Menu.query.filter_by(name=name).first()
        if menu:
            page = page
            flash(u'add failed！current name exist。', 'danger')
        else:
            menu_count = Menu.query.count()
            menu = Menu(name=name, order=menu_count+1)
            db.session.add(menu)
            db.session.commit()
            page = -1
            flash(u'add succeed！', 'success')
        return redirect(url_for('admin.manage_articleTypes_nav', page=page))
    if page == -1:
        page = (Menu.query.count() - 1) // \
               current_app.config['COMMENTS_PER_PAGE'] + 1
    pagination = Menu.query.order_by(Menu.order.asc()).paginate(
            page, per_page=current_app.config['COMMENTS_PER_PAGE'],
            error_out=False)
    menus = pagination.items
    return render_template('admin/manage_articleTypes_nav.html', menus=menus,
                           pagination=pagination, endpoint='.manage_articleTypes_nav',
                           page=page, form=form, form2=form2, form3=form3)


@admin.route('/manage-articleTypes/nav/edit-nav', methods=['GET', 'POST'])
@login_required
def edit_nav():
    form2 = EditArticleNavTypeForm()

    page = request.args.get('page', 1, type=int)

    if form2.validate_on_submit():
        name = form2.name.data
        nav_id = int(form2.nav_id.data)
        if Menu.query.filter_by(name=name).first() \
            and Menu.query.filter_by(name=name).first().id != nav_id:
                flash(u'edit failed！current name exist。', 'danger')
        else:
            nav = Menu.query.get_or_404(nav_id)
            nav.name = name
            db.session.add(nav)
            db.session.commit()
            flash(u'edit success！', 'success')
        return redirect(url_for('admin.manage_articleTypes_nav', page=page))
    if form2.errors:
        flash(u'edit failed！', 'danger')
        return redirect(url_for('admin.manage_articleTypes_nav', page=page))


@admin.route('/manage-articleTypes/nav/delete-nav/<int:id>')
@login_required
def delete_nav(id):
    page = request.args.get('page', 1, type=int)

    nav = Menu.query.get_or_404(id)
    count = 0
    for articleType in nav.types.all():
        count += 1
        articleType.menu = None
        db.session.add(articleType)
    nav.sort_delete()
    db.session.delete(nav)
    try:
        db.session.commit()
    except:
        db.session.rollback()
        flash(u'delete failed！', 'danger')
    else:
        flash(u'delete succeed！total %s categories below the tag change to no navigation tag' % count, 'success')
    return redirect(url_for('admin.manage_articleTypes_nav', page=page))


@admin.route('/manage-articleTypes/nav/sort-up/<int:id>')
@login_required
def nav_sort_up(id):
    page = request.args.get('page', 1, type=int)

    menu = Menu.query.get_or_404(id)
    pre_menu = Menu.query.filter_by(order=menu.order-1).first()
    if pre_menu:
        (menu.order, pre_menu.order) = (pre_menu.order, menu.order)
        db.session.add(menu)
        db.session.add(pre_menu)
        db.session.commit()
        flash(u'up succeed！', 'success')
    else:
        flash(u'this tag is the first already！', 'danger')
    return redirect(url_for('admin.manage_articleTypes_nav', page=page))


@admin.route('/manage-articleTypes/nav/sort-down/<int:id>')
@login_required
def nav_sort_down(id):
    page = request.args.get('page', 1, type=int)

    menu = Menu.query.get_or_404(id)
    latter_menu = Menu.query.filter_by(order=menu.order+1).first()
    if latter_menu:
        (latter_menu.order, menu.order) = (menu.order, latter_menu.order)
        db.session.add(menu)
        db.session.add(latter_menu)
        db.session.commit()
        flash(u'down succeed！', 'success')
    else:
        flash(u'this tag is the last already！', 'danger')
    return redirect(url_for('admin.manage_articleTypes_nav', page=page))


@admin.route('/manage-articleTypes/get-articleTypeNav-info/<int:id>')
@login_required
def get_articleTypeNav_info(id):
    if request.blueprint:
        menu = Menu.query.get_or_404(id)
        return jsonify({
            'name': menu.name,
            'nav_id': menu.id,
        })


@admin.route('/custom/blog-info', methods=['GET', 'POST'])
@login_required
def custom_blog_info():
    form = CustomBlogInfoForm()

    navbars = [(1, u'black'), (2, u'white')]
    form.navbar.choices = navbars

    if form.validate_on_submit():
        blog = BlogInfo.query.first()
        blog.title = form.title.data
        blog.signature = form.signature.data
        if form.navbar.data == 1:
            blog.navbar = 'inverse'
        if form.navbar.data == 2:
            blog.navbar = 'default'
        db.session.add(blog)
        db.session.commit()

        flash(u'edit blog infomation succeed！', 'success')
        return redirect(url_for('admin.custom_blog_info'))

    return render_template('admin/custom_blog_info.html', form=form)


@admin.route('/custom/blog-info/get')
@login_required
def get_blog_info():
    if request.blueprints:
        blog = BlogInfo.query.first()
        if blog.navbar == 'inverse':
            navbar = 1
        if blog.navbar == 'default':
            navbar = 2
        return jsonify({
            'title': blog.title,
            'signature': blog.signature,
            'navbar': navbar,
        })


@admin.route('/account/')
@login_required
def account():
    form = ChangePasswordForm()
    form2 = EditUserInfoForm()

    return render_template('admin/admin_account.html',
                           form=form, form2=form2)


@admin.route('/account/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
    form = ChangePasswordForm()

    if form.validate_on_submit():
        if current_user.verify_password(form.old_password.data):
            current_user.password = form.password.data
            db.session.add(current_user)
            db.session.commit()
            flash(u'edit password succeed！', 'success')
            return redirect(url_for('admin.account'))
        else:
            flash(u'failed, wrong password！', 'danger')
            return redirect(url_for('admin.account'))


@admin.route('/account/edit-user-info', methods=['GET', 'POST'])
@login_required
def edit_user_info():
    form2 = EditUserInfoForm()

    if form2.validate_on_submit():
        if current_user.verify_password(form2.password.data):
            current_user.username = form2.username.data
            current_user.email = form2.email.data
            db.session.add(current_user)
            db.session.commit()
            flash(u'edit user information succeed！', 'success')
            return redirect(url_for('admin.account'))
        else:
            flash(u'edit user information failed！wrong password！', 'danger')
            return redirect(url_for('admin.account'))


@admin.route('/help')
@login_required
def help():

    return render_template('admin/help_page.html')
from flask import Blueprint, redirect, render_template, url_for, request, flash, send_from_directory, current_app
from flask_login import login_user, logout_user, login_required, current_user

from . import db
from .forms import LoginForm, UnitForm, CategoryForm, ServiceForm, SettingForm
from .models import User, UnitOfMeasurement, Category, Service, Setting

import os

admin_bp = Blueprint('admin', __name__)


@admin_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('admin.units'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and user.check_password(form.password.data):
            login_user(user)
            return redirect(url_for('admin.units'))
        flash('Invalid credentials')
    return render_template('login.html', form=form)


@admin_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('admin.login'))


@admin_bp.route('/')
def index():
    return redirect(url_for('admin.units'))


@admin_bp.route('/calculator/')
def calculator_widget_page():
    widget_dir = os.path.join(current_app.root_path, '..', 'calculator_widget')
    return send_from_directory(widget_dir, 'index.html')


@admin_bp.route('/calculator/<path:filename>')
def calculator_widget_static(filename):
    widget_dir = os.path.join(current_app.root_path, '..', 'calculator_widget')
    return send_from_directory(widget_dir, filename)


@admin_bp.route('/units', methods=['GET', 'POST'])
@login_required
def units():
    form = UnitForm()
    if form.validate_on_submit():
        unit = UnitOfMeasurement(name=form.name.data, abbreviation=form.abbreviation.data)
        db.session.add(unit)
        db.session.commit()
        return redirect(url_for('admin.units'))
    units = UnitOfMeasurement.query.all()
    return render_template('units.html', form=form, units=units)


@admin_bp.route('/units/edit/<int:unit_id>', methods=['GET', 'POST'])
@login_required
def edit_unit(unit_id):
    unit = UnitOfMeasurement.query.get_or_404(unit_id)
    form = UnitForm(obj=unit)
    if form.validate_on_submit():
        form.populate_obj(unit)
        db.session.commit()
        return redirect(url_for('admin.units'))
    return render_template('units.html', form=form, units=UnitOfMeasurement.query.all())


@admin_bp.route('/units/delete/<int:unit_id>')
@login_required
def delete_unit(unit_id):
    unit = UnitOfMeasurement.query.get_or_404(unit_id)
    db.session.delete(unit)
    db.session.commit()
    return redirect(url_for('admin.units'))


@admin_bp.route('/categories', methods=['GET', 'POST'])
@login_required
def categories():
    form = CategoryForm()
    if form.validate_on_submit():
        category = Category(name=form.name.data)
        db.session.add(category)
        db.session.commit()
        return redirect(url_for('admin.categories'))
    categories = Category.query.all()
    return render_template('categories.html', form=form, categories=categories)


@admin_bp.route('/categories/edit/<int:category_id>', methods=['GET', 'POST'])
@login_required
def edit_category(category_id):
    category = Category.query.get_or_404(category_id)
    form = CategoryForm(obj=category)
    if form.validate_on_submit():
        form.populate_obj(category)
        db.session.commit()
        return redirect(url_for('admin.categories'))
    return render_template('categories.html', form=form, categories=Category.query.all())


@admin_bp.route('/categories/delete/<int:category_id>')
@login_required
def delete_category(category_id):
    category = Category.query.get_or_404(category_id)
    db.session.delete(category)
    db.session.commit()
    return redirect(url_for('admin.categories'))


@admin_bp.route('/services', methods=['GET', 'POST'])
@login_required
def services():
    form = ServiceForm()
    form.category.choices = [(c.id, c.name) for c in Category.query.all()]
    form.unit.choices = [(u.id, u.abbreviation) for u in UnitOfMeasurement.query.all()]
    if form.validate_on_submit():
        service = Service(name=form.name.data, price=form.price.data,
                          category_id=form.category.data or None,
                          unit_id=form.unit.data or None)
        db.session.add(service)
        db.session.commit()
        return redirect(url_for('admin.services'))
    services = Service.query.all()
    return render_template('services.html', form=form, services=services)


@admin_bp.route('/services/edit/<int:service_id>', methods=['GET', 'POST'])
@login_required
def edit_service(service_id):
    service = Service.query.get_or_404(service_id)
    form = ServiceForm(obj=service)
    form.category.choices = [(c.id, c.name) for c in Category.query.all()]
    form.unit.choices = [(u.id, u.abbreviation) for u in UnitOfMeasurement.query.all()]
    if form.validate_on_submit():
        service.name = form.name.data
        service.price = form.price.data
        service.category_id = form.category.data or None
        service.unit_id = form.unit.data or None
        db.session.commit()
        return redirect(url_for('admin.services'))
    return render_template('services.html', form=form, services=Service.query.all())


@admin_bp.route('/services/delete/<int:service_id>')
@login_required
def delete_service(service_id):
    service = Service.query.get_or_404(service_id)
    db.session.delete(service)
    db.session.commit()
    return redirect(url_for('admin.services'))


@admin_bp.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    form = SettingForm()
    if form.validate_on_submit():
        setting = Setting(key=form.key.data, value=form.value.data)
        db.session.add(setting)
        db.session.commit()
        return redirect(url_for('admin.settings'))
    settings = Setting.query.all()
    return render_template('settings.html', form=form, settings=settings)


@admin_bp.route('/settings/edit/<int:setting_id>', methods=['GET', 'POST'])
@login_required
def edit_setting(setting_id):
    setting = Setting.query.get_or_404(setting_id)
    form = SettingForm(obj=setting)
    if form.validate_on_submit():
        form.populate_obj(setting)
        db.session.commit()
        return redirect(url_for('admin.settings'))
    return render_template('settings.html', form=form, settings=Setting.query.all())


@admin_bp.route('/settings/delete/<int:setting_id>')
@login_required
def delete_setting(setting_id):
    setting = Setting.query.get_or_404(setting_id)
    db.session.delete(setting)
    db.session.commit()
    return redirect(url_for('admin.settings'))


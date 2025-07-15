from flask import (
    Blueprint,
    redirect,
    render_template,
    url_for,
    request,
    flash,
    send_from_directory,
    current_app,
    Response,
    abort,
)
from flask_login import login_user, logout_user, login_required, current_user

from . import db
from sqlalchemy import func
import csv
import io
from .forms import (
    LoginForm,
    UnitForm,
    CategoryForm,
    ServiceForm,
    DefaultSettingsForm,
)
from .models import (
    User,
    UnitOfMeasurement,
    Category,
    Service,
    Setting,
)

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
    widget_dir = os.path.join(
        current_app.root_path,
        '..',
        'calculator_widget',
    )
    return send_from_directory(widget_dir, 'index.html')


@admin_bp.route('/calculator/<path:filename>')
def calculator_widget_static(filename):
    widget_dir = os.path.join(
        current_app.root_path,
        '..',
        'calculator_widget',
    )
    return send_from_directory(widget_dir, filename)


@admin_bp.route('/units', methods=['GET', 'POST'])
@login_required
def units():
    form = UnitForm()
    if form.validate_on_submit():
        unit = UnitOfMeasurement(
            name=form.name.data,
            abbreviation=form.abbreviation.data,
        )
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
    return render_template(
        'units.html',
        form=form,
        units=UnitOfMeasurement.query.all(),
    )


@admin_bp.route('/units/delete/<int:unit_id>')
@login_required
def delete_unit(unit_id):
    unit = UnitOfMeasurement.query.get_or_404(unit_id)
    db.session.delete(unit)
    db.session.commit()
    return redirect(url_for('admin.units'))


@admin_bp.route('/units/delete-selected', methods=['POST'])
@login_required
def delete_selected_units():
    ids = request.form.getlist('unit_ids')
    for uid in ids:
        unit = UnitOfMeasurement.query.get(uid)
        if unit:
            db.session.delete(unit)
    if ids:
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
    return render_template(
        'categories.html',
        form=form,
        categories=Category.query.all(),
    )


@admin_bp.route('/categories/delete/<int:category_id>')
@login_required
def delete_category(category_id):
    category = Category.query.get_or_404(category_id)
    db.session.delete(category)
    db.session.commit()
    return redirect(url_for('admin.categories'))


@admin_bp.route('/categories/delete-selected', methods=['POST'])
@login_required
def delete_selected_categories():
    ids = request.form.getlist('category_ids')
    for cid in ids:
        category = Category.query.get(cid)
        if category:
            db.session.delete(category)
    if ids:
        db.session.commit()
    return redirect(url_for('admin.categories'))


@admin_bp.route('/services', methods=['GET', 'POST'])
@login_required
def services():
    form = ServiceForm()
    form.category.choices = [
        (c.id, c.name) for c in Category.query.all()
    ]
    form.unit.choices = [
        (u.id, u.abbreviation) for u in UnitOfMeasurement.query.all()
    ]
    if form.validate_on_submit():
        service = Service(
            name=form.name.data,
            price=form.price.data,
            category_id=form.category.data or None,
            unit_id=form.unit.data or None,
        )
        db.session.add(service)
        db.session.commit()
        return redirect(url_for('admin.services'))
    services = Service.query.all()
    return render_template(
        'services.html',
        form=form,
        services=services,
    )


@admin_bp.route('/services/edit/<int:service_id>', methods=['GET', 'POST'])
@login_required
def edit_service(service_id):
    service = Service.query.get_or_404(service_id)
    form = ServiceForm(obj=service)
    form.category.choices = [
        (c.id, c.name) for c in Category.query.all()
    ]
    form.unit.choices = [
        (u.id, u.abbreviation) for u in UnitOfMeasurement.query.all()
    ]
    if form.validate_on_submit():
        service.name = form.name.data
        service.price = form.price.data
        service.category_id = form.category.data or None
        service.unit_id = form.unit.data or None
        db.session.commit()
        return redirect(url_for('admin.services'))
    return render_template(
        'services.html',
        form=form,
        services=Service.query.all(),
    )


@admin_bp.route('/services/delete/<int:service_id>')
@login_required
def delete_service(service_id):
    service = Service.query.get_or_404(service_id)
    db.session.delete(service)
    db.session.commit()
    return redirect(url_for('admin.services'))


@admin_bp.route('/services/delete-selected', methods=['POST'])
@login_required
def delete_selected_services():
    ids = request.form.getlist('service_ids')
    for sid in ids:
        svc = Service.query.get(sid)
        if svc:
            db.session.delete(svc)
    if ids:
        db.session.commit()
    return redirect(url_for('admin.services'))


@admin_bp.route('/services/export')
@login_required
def export_services():
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['name', 'price', 'category', 'unit'])
    for svc in Service.query.all():
        writer.writerow([
            svc.name,
            f"{svc.price}",
            svc.category.name if svc.category else '',
            svc.unit.abbreviation if svc.unit else '',
        ])
    response = Response(output.getvalue(), mimetype='text/csv')
    response.headers['Content-Disposition'] = (
        'attachment; filename=services.csv'
    )
    return response


@admin_bp.route('/services/import', methods=['POST'])
@login_required
def import_services():
    file = request.files.get('file')
    if not file or file.filename == '':
        abort(400, 'No file provided')

    try:
        stream = io.StringIO(file.stream.read().decode('utf-8'))
        reader = csv.DictReader(stream)
    except Exception:
        abort(400, 'Invalid CSV')

    required = {'name', 'price', 'category', 'unit'}
    if not reader.fieldnames or not required.issubset(reader.fieldnames):
        abort(400, 'Missing columns')

    category_cache = {}
    unit_cache = {}

    for row in reader:
        name = row.get('name')
        price = row.get('price')
        category_name = row.get('category')
        unit_abbrev = row.get('unit')

        if isinstance(name, str):
            name = name.strip()
        if isinstance(category_name, str):
            category_name = category_name.strip()
        if isinstance(unit_abbrev, str):
            unit_abbrev = unit_abbrev.strip()

        if not name or not price:
            abort(400, 'Missing data')

        try:
            price = float(price)
        except ValueError:
            abort(400, 'Invalid price')

        category = None
        if category_name:
            cat_key = category_name.lower()
            category = category_cache.get(cat_key)
            if not category:
                category = Category.query.filter(
                    func.lower(Category.name) == cat_key
                ).first()
                if not category:
                    category = Category(name=category_name)
                    db.session.add(category)
                    db.session.flush()
                category_cache[cat_key] = category

        unit = None
        if unit_abbrev:
            unit_key = unit_abbrev.lower()
            unit = unit_cache.get(unit_key)
            if not unit:
                unit = UnitOfMeasurement.query.filter(
                    func.lower(UnitOfMeasurement.abbreviation) == unit_key
                ).first()
                if not unit:
                    unit = UnitOfMeasurement(
                        name=unit_abbrev,
                        abbreviation=unit_abbrev,
                    )
                    db.session.add(unit)
                    db.session.flush()
                unit_cache[unit_key] = unit

        svc = Service.query.filter(
            func.lower(Service.name) == name.lower()
        ).first()
        if svc:
            svc.price = price
            svc.category = category
            svc.unit = unit
        else:
            svc = Service(
                name=name,
                price=price,
                category=category,
                unit=unit,
            )
            db.session.add(svc)

    db.session.commit()
    flash('Services imported')
    return redirect(url_for('admin.services'))


@admin_bp.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    form = DefaultSettingsForm()
    lang_setting = Setting.query.filter_by(key="default_language_id").first()
    cur_setting = Setting.query.filter_by(key="default_currency_id").first()

    if request.method == "GET":
        if lang_setting:
            form.language.data = lang_setting.value
        if cur_setting:
            form.currency.data = cur_setting.value

    if form.validate_on_submit():
        try:
            if not lang_setting:
                lang_setting = Setting(key="default_language_id")
                db.session.add(lang_setting)
            lang_setting.value = form.language.data

            if not cur_setting:
                cur_setting = Setting(key="default_currency_id")
                db.session.add(cur_setting)
            cur_setting.value = form.currency.data

            db.session.commit()
            flash("Settings saved")
            return redirect(url_for("admin.settings"))
        except Exception:
            db.session.rollback()
            flash("Failed to save settings", "error")

    return render_template("settings.html", form=form)

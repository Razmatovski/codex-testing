from admin_app import create_app, ensure_db_initialized, db
from admin_app.models import User


def test_auto_init_db(tmp_path, monkeypatch):
    db_path = tmp_path / "auto.db"
    monkeypatch.setenv("SQLALCHEMY_DATABASE_URI", f"sqlite:///{db_path}")

    app = create_app()
    app.config["TESTING"] = True

    ensure_db_initialized(app)

    with app.app_context():
        tables = (
            db.engine.table_names()
            if hasattr(db.engine, "table_names")
            else db.inspect(db.engine).get_table_names()
        )
        assert tables
        user = User.query.filter_by(username="admin").first()
        assert user is not None
        db.session.remove()
        db.drop_all()

from admin_app import create_app, db
from admin_app.models import Language, Currency, Category


def test_sync_default_data_command(tmp_path, monkeypatch):
    db_path = tmp_path / "cli.db"
    monkeypatch.setenv("SQLALCHEMY_DATABASE_URI", f"sqlite:///{db_path}")

    app = create_app()
    app.config["TESTING"] = True
    with app.app_context():
        db.create_all()
        # existing data
        db.session.add(Language(code="en", name="English"))
        db.session.add(Currency(code="USD", name="US Dollar", symbol="$"))
        cat = Category(name="KeepCat")
        db.session.add(cat)
        db.session.commit()

    runner = app.test_cli_runner()
    result = runner.invoke(args=["sync-default-data"])
    assert result.exit_code == 0

    with app.app_context():
        codes = {l.code for l in Language.query.all()}
        assert {"en", "ru", "pl", "uk"} <= codes
        cur_codes = {c.code for c in Currency.query.all()}
        assert {"USD", "EUR", "PLN"} <= cur_codes
        assert Category.query.filter_by(name="KeepCat").first() is not None


from admin_app.models import User


def test_password_hashing():
    user = User(username='alice')
    user.set_password('secret')
    assert user.check_password('secret')
    assert not user.check_password('wrong')

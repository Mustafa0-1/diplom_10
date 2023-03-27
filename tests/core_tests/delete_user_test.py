import pytest


@pytest.mark.django_db
# @pytest.mark.skip
def test_delete_user(client):
    """Тест на проверку удаления пользователя"""
    user_data = {
        'username': 'est',
        'first_name': 'test',
        'last_name': 'test',
        'email': 'test@test.ru',
        'password': 'test12234567',
        'password_repeat': 'test12234567'
    }

    create_user_response = client.post(
        '/core/signup',
        data=user_data,
        content_type='application/json')

    login_user_response = client.post(
        '/core/login',
        {'username': 'test', 'password': 'test12234567'},
        content_type='application/json')

    user_delete_response = client.delete(
        '/core/profile',
    )

    assert create_user_response.status_code == 201
    assert login_user_response.status_code == 403
    assert user_delete_response.status_code == 403

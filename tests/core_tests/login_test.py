import pytest


@pytest.mark.django_db
# @pytest.mark.skip
def test_login(client):
    """Тест на проверку входа (login) пользователя"""
    user_data = {
        'username': 'test',
        'first_name': 'Test',
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
        {'username': user_data['username'], 'password': user_data['password']},
        content_type='application/json')

    assert create_user_response.status_code == 201
    assert login_user_response.status_code == 200

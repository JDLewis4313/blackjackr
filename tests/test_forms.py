import pytest
from domains.player.forms import RegistrationForm, LoginForm


def test_registration_form_valid():
    form = RegistrationForm(
        data={
            'name': 'Raviroyashe',
            'email': 'raviro.mahere@gmail.com',
            'password': 'Mahere123'
        }
    )
    assert form.validate() is True


def test_registration_form_missing_name():
    form = RegistrationForm(
        data={
            'name': '',
            'email': 'raviro.mahere@gmail.com',
            'password': 'Mahere123'
        }
    )
    assert not form.validate()
    assert 'name' in form.errors


def test_registration_form_invalid_email():
    form = RegistrationForm(
        data={
            'name': 'Raviroyashe',
            'email': 'raviro.mahere@gmail',
            'password': 'password@123'
        }
    )
    assert not form.validate()
    assert 'email' in form.errors


def test_registration_form_short_password():
    form = RegistrationForm(
        data={
            'name': 'Raviroyashe',
            'email': 'raviro.mahere@gmail.com',
            'password': '123'
        }
    )
    assert not form.validate()
    assert 'password' in form.errors



def test_login_form_valid():
    form = LoginForm(
        data={
            'email': 'raviro.mahere@gmail.com',
            'password': 'Mahere123'
        }
    )
    assert form.validate() is True


def test_login_form_missing_email():
    form = LoginForm(
        data={
            'email': '',
            'password': 'Mahere123'
        }
    )
    assert not form.validate()
    assert 'email' in form.errors


def test_login_form_missing_password():
    form = LoginForm(
        data={
            'email': 'raviro.mahere@gmail.com',
            'password': ''
        }
    )
    assert not form.validate()
    assert 'password' in form.errors


def test_login_form_invalid_email_format():
    form = LoginForm(
        data={
            'email': 'raviro.mahere@gmail',
            'password': 'Mahere123'
        }
    )
    assert not form.validate()
    assert 'email' in form.errors

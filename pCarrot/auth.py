#!/usr/bin/env python
# -*- coding: utf-8 -*-

# MIT License
#
# Copyright (c) 2023 Iñaki Amatria-Barral
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import hashlib
import functools

from flask import g
from flask import session
from flask import url_for
from flask import redirect
from flask import Blueprint
from flask import render_template

from flask_wtf import FlaskForm

from wtforms import StringField
from wtforms import SubmitField
from wtforms import PasswordField

from wtforms.validators import Length
from wtforms.validators import EqualTo
from wtforms.validators import DataRequired

from .model import get_account_id
from .model import AccountNotFoundError
from .model import register_new_account
from .model import AccountNameInUseError

class LoginForm(FlaskForm):
    account_name = StringField(
        "Account name",
        validators=[
            DataRequired("You must enter your account name")
        ],
        render_kw={"placeholder": "Type your account name"}
    )
    password = PasswordField(
        "Password",
        validators=[
            DataRequired("You must enter your password")
        ],
        render_kw={"placeholder": "Type your password"}
    )
    submit = SubmitField("Submit")

class RegisterForm(FlaskForm):
    account_name = StringField(
        "Account name",
        validators=[
            DataRequired("You must enter an account name"),
            Length(
                min=4,
                max=16,
                message="Your account account name must be between 4 and 16"
                        " characters long"
            )
        ],
        render_kw={"placeholder": "Type your account name"}
    )
    password = PasswordField(
        "Password",
        validators=[
            DataRequired("You must enter a password"),
            Length(
                min=8,
                max=32,
                message="Your password must be between 8 and 32 characters long"
            )
        ],
        render_kw={"placeholder": "Type your password"}
    )
    confirm_password = PasswordField(
        "Confirm password",
        validators=[
            DataRequired("You must confirm your password"),
            EqualTo("password", message="Your passwords do not match")
        ],
        render_kw={"placeholder": "Confirm your password"}
    )
    submit = SubmitField("Submit")

def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.account_id is None:
            return redirect(url_for("auth.login"))
        return view(**kwargs)
    return wrapped_view

bp = Blueprint("auth", __name__)

@bp.before_app_request
def load_logged_in_user():
    account_id = session.get("account_id")
    g.account_id = None if account_id is None else account_id

@bp.route("/login", methods=("GET", "POST"))
def login():
    form = LoginForm()
    if form.validate_on_submit():
        account_name = form.account_name.data
        password = hashlib.sha1(form.password.data.encode("utf-8")).hexdigest()

        try:
            account_id = get_account_id(account_name, password)
        except AccountNotFoundError as e:
            form.account_name.errors.append(e)
            form.password.errors.append(e)
            return render_template("auth/login.html", form=form)
        except:
            form.form_errors.append("Oops! Something went wrong, try again")
            return render_template("auth/login.html", form=form)
        session["account_id"] = account_id

        return redirect(url_for("account.index"))
    return render_template("auth/login.html", form=form)

@bp.route("/register", methods=("GET", "POST"))
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        account_name = form.account_name.data
        password = hashlib.sha1(form.password.data.encode("utf-8")).hexdigest()

        try:
            register_new_account(account_name, password)
        except AccountNameInUseError as e:
            form.account_name.errors.append(e)
            return render_template("auth/register.html", form=form)
        except:
            form.form_errors.append("Oops! Something went wrong, try again")
            return render_template("auth/register.html", form=form)

        return render_template("auth/register_success.html")
    return render_template("auth/register.html", form=form)

@bp.route("/logout")
def logout():
    session.clear()
    g.account_id = None
    return render_template("auth/logout_success.html")

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

from flask import g
from flask import Blueprint
from flask import render_template

from flask_wtf import FlaskForm

from wtforms import SubmitField
from wtforms import PasswordField

from wtforms.validators import Length
from wtforms.validators import EqualTo
from wtforms.validators import DataRequired

from .auth import login_required

from .model import change_account_password
from .model import AccountChangePasswordError

class ChangePasswordForm(FlaskForm):
    current_password = PasswordField(
        "Current password",
        validators=[
            DataRequired("You must enter your current password")
        ],
        render_kw={"placeholder": "Type your current password"}
    )
    new_password = PasswordField(
        "New password",
        validators=[
            DataRequired("You must enter your new password"),
            Length(
                min=8,
                max=32,
                message="Your new password must be between 8 and 32 characters"
                        " long"
            )
        ],
        render_kw={"placeholder": "Type your new password"}
    )
    confirm_password = PasswordField(
        "Confirm new password",
        validators=[
            DataRequired("You must confirm your new password"),
            EqualTo("new_password", message="Your new password does not match")
        ],
        render_kw={"placeholder": "Confirm your new password"}
    )
    submit = SubmitField("Submit")

bp = Blueprint("account", __name__)

@bp.route("/account", methods=("GET", "POST"))
@login_required
def index():
    form = ChangePasswordForm()
    if form.validate_on_submit():
        current_password = hashlib.sha1(
            form.current_password.data.encode("utf-8")
        ).hexdigest()
        new_password = hashlib.sha1(
            form.new_password.data.encode("utf-8")
        ).hexdigest()

        if current_password == new_password:
            form.new_password.errors.append(
                "Your new password must be different from your current password"
            )
            return render_template("account/index.html", form=form)

        try:
            change_account_password(
                g.account_id,
                current_password,
                new_password
            )
        except AccountChangePasswordError as e:
            form.current_password.errors.append(e)
            return render_template("account/index.html", form=form)
        except:
            form.form_errors.append("Oops! Something went wrong, try again")
            return render_template("account/index.html", form=form)

        return render_template("account/change_password_success.html")

    return render_template("account/index.html", form=form)

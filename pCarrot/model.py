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

import time
import markdown

from .db import get_db
from .cache import cache

class AccountNotFoundError(Exception): ...
class AccountNameInUseError(Exception): ...
class AccountChangePasswordError(Exception): ...

@cache.memoize()
def get_latest_news(num_latest_news):
    with get_db().cursor() as cursor:
        cursor.execute(
            "SELECT * FROM `pcarrot_news` ORDER BY `date` DESC LIMIT %s",
            (num_latest_news, )
        )
        news = cursor.fetchall()
        for n in news:
            n["body"] = markdown.markdown(n["body"])
        return news

def register_new_account(account_name, password):
    db = get_db()
    with db.cursor() as cursor:
        cursor.execute(
            "SELECT * FROM `accounts` WHERE `name` = %s", (account_name, )
        )
        if cursor.fetchone():
            raise AccountNameInUseError("Account name already in use")
        cursor.execute(
            "INSERT INTO `accounts` (`name`, `password`, `creation`)"
            " VALUES (%s, %s, %s)",
            (account_name, password, int(time.time()))
        )
    db.commit()

def change_account_password(account_id, old_password, new_password):
    db = get_db()
    with db.cursor() as cursor:
        cursor.execute(
            "SELECT * FROM `accounts` WHERE `id` = %s AND `password` = %s",
            (account_id, old_password)
        )
        if not cursor.fetchone():
            raise AccountChangePasswordError("Invalid current password")
        cursor.execute(
            "UPDATE `accounts` SET `password` = %s WHERE `id` = %s",
            (new_password, account_id)
        )
    db.commit()

def get_account_id(account_name, password):
    with get_db().cursor() as cursor:
        cursor.execute(
            "SELECT id FROM `accounts` WHERE `name` = %s AND `password` = %s",
            (account_name, password)
        )
        account = cursor.fetchone()
        if account is None:
            raise AccountNotFoundError("Invalid account name or password")
        return account["id"]

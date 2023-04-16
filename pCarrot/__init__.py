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

import os

from flask import Flask

__version__ = "0.0.0"
__date__ = "April 2023"

__license__ = "MIT"
__copyright__ = "Copyright (c) 2023 Iñaki Amatria-Barral"

__author__ = "Iñaki Amatria-Barral"
__email__ = "i.amatria@udc.es"

def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        # OT realted config
        OT_SERVER_NAME="pCarrot",
        OT_SERVER_DESCRIPTION="A Python AAC for OpenTibia",
        OT_NUM_LATEST_NEWS=3,
        OT_DATABASE_HOST="localhost",
        OT_DATABASE_USER="forgotten",
        OT_DATABASE_PASSWORD="forgotten",
        OT_DATABASE_NAME="forgotten",
        # Flask related config
        SECRET_KEY="dev",
        # Flask-Caching related config
        CACHE_TYPE="FileSystemCache",
        CACHE_DEFAULT_TIMEOUT=300,
        CACHE_DIR=os.path.join(app.instance_path, "cache")
    )

    if test_config is None:
        app.config.from_pyfile("config.py", silent=True)
    else:
        app.config.from_mapping(test_config)

    os.makedirs(app.instance_path, exist_ok=True)

    from . import db
    db.init_app(app)

    from . import cache
    cache.init_app(app)

    from . import auth
    from . import public
    app.register_blueprint(auth.bp)
    app.register_blueprint(public.bp)

    return app

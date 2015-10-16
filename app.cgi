#! /usr/bin/pyvenv-3.4*

""" For deployment on ix under CGI """

import site
site.addsitedir("/home/users/logand/public_html/htbin/cis399/proj3-ajax/env/lib/python3.4/site-packages")

from wsgiref.handlers import CGIHandler
from app import app

CGIHandler().run(app)

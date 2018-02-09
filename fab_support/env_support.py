# -*- coding: utf-8 -*-
"""env_support
This supports using a .env environment file to store secrets in a file and then to make them available
to the local programs as environment variables.
"""


import datetime as dt
import os

from dotenv import load_dotenv, find_dotenv


# .Env
# Get any required secret environment variables
load_dotenv(find_dotenv())

os.environ['UPDATE_DATESTAMP'] = dt.datetime.now().isoformat()


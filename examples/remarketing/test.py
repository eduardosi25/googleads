#!/usr/bin/env python
# Copyright 2020 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""Uses Customer Match to create and add users to a new user (audience) list.

Note: It may take up to several hours for the list to be populated with users.
Email addresses must be associated with a Google account.
For privacy purposes, the user list size will show as zero until the list has
at least 1,000 users. After that, the size will be rounded to the two most
significant digits.
"""
import pymysql
import argparse
import hashlib
import sys
import uuid
import os
import logging
import json
logger = logging.getLogger()
logger.setLevel(logging.INFO)
from google.ads.googleads.client import GoogleAdsClient
from google.ads.googleads.errors import GoogleAdsException

rds_host  = os.environ['DB_HOST']
name = os.environ['DB_USERNAME']
password = os.environ['DB_PASSWORD']
db_name = os.environ['DB_DATABASE']
developer_token = os.environ['TOKEN_DEV']
client_id = os.environ['CLIENT_ID']
client_secret = os.environ['CLIENT_SECRET']
db_nameAudience = os.environ['DB_AUDIENCE']
audienceId=470

port = 3306

try:
    conn = pymysql.connect(rds_host, user=name, passwd=password, db=db_name, connect_timeout=5)
    connAudience = pymysql.connect(rds_host, user=name, passwd=password, db=db_nameAudience, connect_timeout=5)
    print("connection",conn)

except Exception as e: 
    print(e)
    # logger.error("ERROR: Unexpected error: Could not connect to MySql instance.")
    # sys.exit()
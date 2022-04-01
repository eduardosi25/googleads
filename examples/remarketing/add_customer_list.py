import hashlib
import json
import csv
import boto3
import os
import sys
import pymysql
import hashlib
import logging
# Import appropriate modules from the client library.
from google.ads.googleads.client import GoogleAdsClient
from google.ads.googleads.errors import GoogleAdsException

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def NormalizeAndSHA256(s):
  """Normalizes (lowercase, remove whitespace) and hashes a string with SHA-256.

  Args:
    s: The string to perform this operation on.

  Returns:
    A normalized and SHA-256 hashed string.
  """
  return hashlib.sha256(s.strip().lower().encode('utf-8')).hexdigest()

def remove_spaces(string):
    return ''.join(string.split())

def remove_dots_before_at(string):
    parts = string.split('@')
    if len(parts) > 1:
        parts[0] = ''.join(parts[0].split('.'))
    print('@'.join(parts))
    return '@'.join(parts)

def python_none():
    pass

def python_cc(cc):
    if cc.lower() == 'peruana':
        cc = 'PE'
    return cc


def lambda_handler(event, context):
    rds_host  = os.environ['DB_HOST']
    name = os.environ['DB_USERNAME']
    password = os.environ['DB_PASSWORD']
    db_name = os.environ['DB_DATABASE']
    developer_token = os.environ['TOKEN_DEV']
    client_id = os.environ['CLIENT_ID']
    client_secret = os.environ['CLIENT_SECRET']
    db_nameAudience = os.environ['DB_AUDIENCE']

    port = 3306

    try:
        conn = pymysql.connect(rds_host, user=name, passwd=password, db=db_name, connect_timeout=5)
        connAudience = pymysql.connect(rds_host, user=name, passwd=password, db=db_nameAudience, connect_timeout=5)
    #print(conn)
    except:
        logger.error("ERROR: Unexpected error: Could not connect to MySql instance.")
        sys.exit()

    try:
        clientId = event['clientId']
        audienceId = event['audienceId']

        mycursorAudience = connAudience.cursor()
        mycursor = conn.cursor()
        mycursor.execute("SELECT name, description, targetId FROM audiences where audienceId={}".format(audienceId))
        result = mycursor.fetchone()
        segmentName = str(audienceId) + ' - ' + str(result[0])
        description = result[1]
        targetsIds = result[2]

        mycursor.execute("SELECT keyType, isHash, query, appIdGAds,attributes FROM segmentConfiguration where audienceId={}".format(audienceId))
        result = mycursor.fetchone()
        print(result)
        keyType = result[0] or 0
        isHash = result[1]
        keysArrayHeader = result[2].split(',')
        print('keysArrayHeader',keysArrayHeader)
        attributes = result[4]
        switcher={
                    1:'mobile',
                    2:'email',
                    3:'customer',
                    4:'mobileAdId'
                 }

        type = switcher.get(int(keyType), 'email')
        print('type', type)
        if type == 'mobileAdId':
            appId = result[3]
            print('appId', appId)

        mycursor.execute("SELECT data FROM targets where targetId in ({})".format(targetsIds))
        targetsList = mycursor.fetchone()
        jsonTarget = json.loads(targetsList[0])
        access_token = jsonTarget['token_gads']
        accountId = jsonTarget['client_customer_id']


        mycursorAudience.execute("SELECT {} FROM audience_{} where status=0 group by {}".format(attributes,audienceId,attributes))

        rows = mycursorAudience.fetchall()
        totalRows = len(rows)


        yaml_doc = """adwords:
        developer_token: {}
        client_id: {}
        client_customer_id: {}
        client_secret: {}
        refresh_token: {}""".format(developer_token, client_id, accountId, client_secret, access_token)



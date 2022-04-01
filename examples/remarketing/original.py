#!/usr/bin/env python
#
# Copyright 2016 Google Inc. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


"""

#cd adwords/lib/python3.7/site-packages  cd adwords/lib/python3.7/site-packages
zip -r9 ${OLDPWD}/function.zip
"""


"""Adds a user list and populates it with hashed email addresses.

Note: It may take several hours for the list to be populated with members. Email
addresses must be associated with a Google account. For privacy purposes, the
user list size will show as zero until the list has at least 1000 members. After
that, the size will be rounded to the two most significant digits.
"""


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
from googleads import adwords, common

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


        adwords_client = adwords.AdWordsClient.LoadFromString(yaml_doc)
        adwords_client.cache = common.ZeepServiceProxy.NO_CACHE
        print("PREPARANDO API")

        x = 0
        keyArray = []
        arrayMobileAdId = []
        arrayEmails = []
        arrayPhones = []
        arrayAddress = []
        totalContacs = 0
        for row in rows:
            totalContacs = totalContacs + 1
            values = row
            cont = 0
            for header in keysArrayHeader:
                if (header == 'email'):
                    arrayEmails.append(values[cont])

                if (header == 'mobile advertising id'):
                    arrayMobileAdId.append(values[cont])

                if (header == 'phone'):
                    arrayPhones.append(values[cont])

                if (header == 'firstname'):
                    firstName = values[cont]
                    lastName = values[cont+1]

                    if len(firstName) == 0:
                        firstName = python_none()

                    if len(lastName) == 0:
                        lastName = python_none()

                    if(int(isHash) == 0):
                        hashedFirstName =  NormalizeAndSHA256(remove_spaces(firstName))
                        hashedLastName =   NormalizeAndSHA256(remove_spaces(lastName))
                    else:
                        hashedFirstName =  firstName
                        hashedLastName =   lastName

                    countryCode = values[cont+2]
                    zipCode = values[cont+3]

                    if len(countryCode)!=2:
                        countryCode = python_cc(countryCode)


                    validName = str(hashedFirstName)
                    validlastName = str(hashedLastName)
                    if len(zipCode) > 0 and len(countryCode) == 2 and len(validName.encode('utf-8')) == 64 and len(validlastName.encode('utf-8')) == 64:
                        arrayAddress.append({
                            'addressInfo': {
                              # First and last name must be normalized and hashed.
                              'hashedFirstName':hashedFirstName,
                              'hashedLastName': hashedLastName,
                              # Country code and zip code are sent in plaintext.
                              'countryCode': countryCode,
                              'zipCode': zipCode
                            }
                            })
                cont = cont + 1

        print("CREANDO LISTA")
        user_list_service = adwords_client.GetService('AdwordsUserListService', 'v201809')

        uploadKeyType =  'CONTACT_INFO'
        if keyType == 4:
            uploadKeyType = 'MOBILE_ADVERTISING_ID'

        user_list = {
            'xsi_type': 'CrmBasedUserList',
            'listType': 'CRM_BASED',
            'name': segmentName,
            'description': description,
            'membershipLifeSpan': 30,
            'uploadKeyType': uploadKeyType
        }

        if keyType == 4:
            user_list['appId'] = appId

        # Create an operation to add the user list.
        operations = [{
            'operator': 'ADD',
            'operand': user_list
        }]

        print("CREANDO Y ACTUALIZANDO ADUIENCIA LISTA")
        result = user_list_service.mutate(operations)
        user_list_id = result['value'][0]['id']
        queryUpdate = "UPDATE `hexagonmatch`.`audiences` SET status=1, googleListId='{}' WHERE (`audienceId` = {});".format(user_list_id,audienceId)
        mycursor.execute(queryUpdate)
        conn.commit()
        print("SE CREO LA LISTA")
        members = []
        if (len(arrayEmails) > 0):
            if(int(isHash) == 0):
                for value in arrayEmails:
                    members.append({'hashedEmail': NormalizeAndSHA256(remove_dots_before_at(value))})
            else:
               for value in arrayEmails:
                   emailStr = str(value)
                   if len(emailStr.encode('utf-8')) == 64:
                       members.append({'hashedEmail': value})

        if (len(arrayPhones) > 0):
            if(int(isHash) == 0):
                for value in arrayPhones:
                    members.append({'hashedPhoneNumber': NormalizeAndSHA256(value)})
            else:
                for value in arrayPhones:
                    phoneStr = str(value)
                    if len(phoneStr.encode('utf-8')) == 64:
                        members.append({'hashedPhoneNumber': value})

        if (len(arrayAddress) > 0):
            for address in arrayAddress:
                members.append(address)


        if (int(keyType) == 4):
            members = [{'mobileId': value} for value in arrayMobileAdId]


        print('members', len(members))
        mutate_members_operation = {
            'operand': {
                'userListId': user_list_id,
                'membersList': members
            },
            'operator': 'ADD'
        }


        print("Emmpezando el mutate")
        response = user_list_service.mutateMembers([mutate_members_operation])
        print('Response', response)


        if 'userLists' in response:
          for user_list in response['userLists']:
            print('User list with name "%s" and ID "%d" was added.'
                  % (user_list['name'], user_list['id']))
        else:
            print('ErrorUserList', response)

        totalContacs = len(members)
        queryUpdate = "UPDATE `hexagonmatch`.`audiences` SET `status` = 2,reach={} WHERE (`audienceId` = {});".format(totalContacs,audienceId)
        mycursor.execute(queryUpdate)
        mycursorAudience.execute("update audience_{} set status=1".format(audienceId))


        description = 'Se genero una audiencia con el nombre {} con {} registros'.format(segmentName, totalContacs)
        event = 'Envío de audiencia a Google Ads'
        querySegment = "INSERT INTO `hexagonmatch`.`audience_detail` (`audienceId`,`date`,`event`,`type`,`description`) VALUES ({},Now(),'{}','Error','{}')".format(audienceId,event,description)
        mycursor.execute(querySegment)

        conn.commit()
        connAudience.commit()
        connAudience.close()
        conn.close()
    except Exception as e:
        querySegment = "UPDATE `hexagonmatch`.`audiences` SET `status` = 3 WHERE (`audienceId` = '{}');".format(audienceId)
        mycursor.execute(querySegment)
        conn.commit()
        conn.close()
        connAudience.close()
        print("match rate error:", sys.exc_info()[0])
        print("Unexpecteds:", sys.exc_info())
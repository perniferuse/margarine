# -*- coding: UTF-8 -*-
#
# Copyright (C) 2013 by Alex Brandt <alex.brandt@rackspace.com>
#
# margarine is freely distributable under the terms of an MIT-style license.
# See COPYING or http://www.opensource.org/licenses/mit-license.php.

import mock

import logging
import bson
import json

from test_margarine.test_unit.test_blend import BaseBlendTest

from margarine.blend import information

logger = logging.getLogger(__name__)

class BaseBlendUserTest(BaseBlendTest):
    def setUp(self):
        super(BaseBlendUserTest, self).setUp()

        self.accounts = {
                'alunduil': { 'email': 'alunduil@alunduil.com', },
                }

        self.base_url = '/{i.API_VERSION}/users/'.format(i = information)

class BlendUserCreateTest(BaseBlendUserTest):
    '''User Create

    .. note::
        Possible race condition if two people nearly simultaneously submit a
        create user request for the same username.  Nearly simultaneous being
        the window between the first request entering the message queue and
        that same request being processed and added to the datastore for query
        by the next request.

        This is best shown with cases:
        * User—Submitted,Incomplete IS EQUIVALENT TO User—Unsubmitted
        * User—Submitted,Complete → User is in system and ready for query

    '''

    def test_user_create_unsubmitted(self):
        '''User Create—Unsubmitted
        
        .. note::
            This is also User Update—Unsubmitted
        
        '''

        for account, properties in self.accounts.iteritems():
            response = self.application.put(self.base_url + account, data = properties)

            properties.update({ 'username': account })
            message = json.dumps(properties)

            self.mock_channel.basic_publish.assert_called_once_with(
                    body = message,
                    exchange = 'margarine.users.topic',
                    properties = mock.ANY,
                    routing_key = 'users.create',
                    )

            self.mock_channel.reset_mock()

            self.assertIn('202', response.status)

    def test_user_create_submitted_complete(self):
        '''User Create—Submitted,Complete

        .. note::
            This is also User Update—Submitted,Complete,Unauthorized
        
        '''

        for account, properties in self.accounts.iteritems():
            self.mock_collection.find_one.return_value = {
                    '_id': bson.ObjectId(),
                    'username': account,
                    }
            self.mock_collection.find_one.return_value.update(properties)

            response = self.application.put(self.base_url + account, data = properties)

            self.mock_collection.find_one.assert_called_once_with({ 'username': account })
            self.mock_collection.reset_mock()

            self.assertIn('401', response.status)

class BlendUserReadTest(BaseBlendUserTest):
    def setUp(self):
        self.mock_mask = [
                'container',
                ]

        super(BlendUserReadTest, self).setUp()

    def test_user_read_unsubmitted(self):
        '''User Read—Unsubmitted'''

        self.mock_collection.find_one.return_value = None

        for account, properties in self.accounts.iteritems():
            response = self.application.get(self.base_url + account)

            self.assertIn('404', response.status)

    # TODO Add other Content-Type
    def test_user_read_submitted_complete(self):
        '''User Read—Submitted,Complete'''

        for account, properties in self.accounts.iteritems():
            self.mock_collection.find_one.return_value = {
                    '_id': bson.ObjectId(),
                    'username': account,
                    }
            self.mock_collection.find_one.return_value.update(properties)

            response = self.application.get(self.base_url + account)

            self.mock_collection.find_one.assert_called_once_with({ 'username': account }, { 'hash': 0 })
            self.mock_collection.reset_mock()

            self.assertIn('200', response.status)
            
            self.assertEqual('application/json', response.headers.get('Content-Type'))
            # TODO Verify configured domain.
            self.assertEqual('http://margarine.raxsavvy.com', response.headers.get('Access-Control-Allow-Origin'))

            # TODO Body Check

class BlendUserUpdateTest(BaseBlendUserTest):
    '''User Update

    .. note::
        See User Create for the following cases:
        * User Update—Unsubmitted
        * User Update—Submitted,Complete,Unauthorized

    '''

    def setUp(self):
        self.mock_mask = [
                'container',
                ]

        super(BlendUserUpdateTest, self).setUp()

    def test_user_update_submitted_complete_authorized(self):
        '''User Update—Submitted,Complete,Authorized'''

        modifications = {
                'alunduil': { 'name': 'Alex Brandt' },
                }

        token = 'c2d52150-08d1-4ae3-b19c-323c9e37813d'
        headers = { 'X-Auth-Token': token }

        for account, properties in self.accounts.iteritems():
            self.mock_keyspace.get.return_value = account

            self.mock_collection.find_one.return_value = {
                    '_id': bson.ObjectId(),
                    'username': account,
                    }
            self.mock_collection.find_one.return_value.update(properties)

            response = self.application.put(self.base_url + account, headers = headers, data = modifications[account])

            self.mock_keyspace.get.assert_called_once_with(token)
            self.mock_keyspace.reset_mock()

            self.mock_collection.find_one.assert_called_once_with({ 'username': account })
            self.mock_collection.reset_mock()

            properties.update({ 'username': account })
            properties['requested_username'] = modifications[account].pop('username', account)
            message = json.dumps(properties)

            self.mock_channel.basic_publish.assert_called_once_with(
                    body = message,
                    exchange = 'margarine.users.topic',
                    properties = mock.ANY,
                    routing_key = 'users.update',
                    )

            self.mock_channel.reset_mock()

            self.assertIn('202', response.status)

class BlendUserDeleteTest(BaseBlendUserTest):
    def test_user_delete_unauthorized(self):
        '''User Delete—Unauthorized'''

        for account, properties in self.accounts.iteritems():
            response = self.application.delete(self.base_url + account)

            self.assertIn('401', response.status)

    def test_user_delete_authorized(self):
        '''User Delete—Authorized'''

        token = 'c2d52150-08d1-4ae3-b19c-323c9e37813d'
        headers = { 'X-Auth-Token': token }

        for account, properties in self.accounts.iteritems():
            self.mock_keyspace.get.return_value = account

            response = self.application.delete(self.base_url + account, headers = headers)

            self.mock_keyspace.get.assert_called_once_with(token)
            self.mock_keyspace.reset_mock()

            self.mock_collection.remove.assert_called_once_with({ 'username': account })
            self.mock_collection.reset_mock()

            self.assertIn('200', response.status)

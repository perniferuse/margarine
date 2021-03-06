# -*- coding: UTF-8 -*-
#
# Copyright (C) 2013 by Alex Brandt <alex.brandt@rackspace.com>
#
# margarine is freely distributable under the terms of an MIT-style license.
# See COPYING or http://www.opensource.org/licenses/mit-license.php.

import mock

import logging
import uuid
import datetime

from test_margarine.test_unit.test_blend import BaseBlendTest

from margarine.blend import information

logger = logging.getLogger(__name__)

class BaseBlendArticleTest(BaseBlendTest):
    # TODO Make this simpler.
    mock_mask = BaseBlendTest.mock_mask | set(['keyspace'])

    def setUp(self):
        super(BaseBlendArticleTest, self).setUp()

        self.articles = [
                'http://blog.alunduil.com/posts/an-explanation-of-lvm-snapshots.html',
                'http://developer.rackspace.com/blog/got-python-questions.html',
                ]

        self.articles = dict([ (uuid.uuid5(uuid.NAMESPACE_URL, _), _) for _ in self.articles ])

        self.base_url = '/{i.API_VERSION}/articles/'.format(i = information)

class BlendArticleCreateTest(BaseBlendArticleTest):
    def test_article_create(self):
        '''Blend::Article Create'''

        for uuid, url in self.articles.iteritems():
            response = self.application.post(self.base_url, data = {
                'url': url,
                })

            self.mock_channel.basic_publish.assert_called_once_with(
                    body = '{"url": "' + url + '", "_id": "' + uuid.hex + '"}',
                    exchange = 'margarine.articles.topic',
                    properties = mock.ANY,
                    routing_key = 'articles.create'
                    )

            self.mock_channel.reset_mock()

            self.assertIn('202', response.status)

            self.assertIn(self.base_url + str(uuid), response.headers.get('Location'))

class BlendArticleReadTest(BaseBlendArticleTest):
    # TODO Make this simpler.
    mock_mask = BaseBlendArticleTest.mock_mask | set(['channel'])

    def test_article_read_unsubmitted(self):
        '''Blend::Article Read—Unsubmitted

        .. note::
            The article in question has not been submitted and thus nothing
            exists in the system for the requested article.

        '''

        self.mock_collection.find_one.return_value = None

        for uuid, url in self.articles.iteritems():
            response = self.application.get(self.base_url + str(uuid))

            self.assertIn('404', response.status)

    def test_article_read_submitted_incomplete(self):
        '''Blend::Article Read—Submitted,Incomplete

        .. note::
            The article in question has been submitted but the spread process
            has not populated any information beyond the first consumption.

            * created_at

        '''

        for uuid, url in self.articles.iteritems():
            self.mock_collection.find_one.return_value = {
                    '_id': uuid.hex,
                    'url': url,
                    'created_at': datetime.datetime(2013, 8, 4, 14, 4, 12, 639560),
                    }

            response = self.application.get(self.base_url + str(uuid))

            self.mock_collection.find_one.assert_called_once_with({ '_id': uuid.hex })

            self.mock_collection.reset_mock()

            self.assertIn('404', response.status)

    def test_article_read_submitted_complete(self):
        '''Blend::Article Read—Submitted,Complete

        .. note::
            The article in question has been submitted and the spread process
            has finished processing the following items:

            * HTML Sanitization

        '''

        for uuid, url in self.articles.iteritems():
            self.mock_collection.find_one.return_value = {
                    '_id': uuid.hex,
                    'url': url,
                    'created_at': datetime.datetime(2013, 8, 4, 14, 16, 20, 77773),
                    'etag': 'bf6285d832a356e1bf509a63edc8870f',
                    'parsed_at': datetime.datetime(2013, 8, 4, 14, 16, 21, 77773),
                    'size': 31052,
                    'text_container_name': '44d85795',
                    'text_object_name': '248d-5899-b8ca-ac2bd8233755',
                    }

            mock_object = self._get_attached_mock(self.mock_container.get_object)
            mock_object.fetch.return_value = 'Redacted for testing purposes'

            response = self.application.get(self.base_url + str(uuid))

            self.mock_collection.find_one.assert_called_once_with({ '_id': uuid.hex })
            self.mock_collection.reset_mock()

            mock_object.fetch.assert_called_once_with()

            self.assertIn('200', response.status)

            self.assertEqual('application/json', response.headers.get('Content-Type'))
            # TODO Verify configured domain.
            self.assertEqual('http://margarine.raxsavvy.com', response.headers.get('Access-Control-Allow-Origin'))

class BlendArticleUpdateTest(BaseBlendArticleTest):
    # TODO Make this simpler.
    mock_mask = BaseBlendArticleTest.mock_mask | set([
        'collection',
        'channel',
        ])

    def test_article_update(self):
        '''Blend::Article Update'''

        for uuid, url in self.articles.iteritems():
            response = self.application.put(self.base_url + str(uuid))

            self.assertIn('405', response.status)

class BlendArticleDeleteTest(BaseBlendArticleTest):
    # TODO Make this simpler.
    mock_mask = BaseBlendArticleTest.mock_mask | set([
        'collection',
        'channel',
        ])

    def test_article_delete(self):
        '''Blend::Article Delete'''

        for uuid, url in self.articles.iteritems():
            response = self.application.delete(self.base_url + str(uuid))

            self.assertIn('405', response.status)

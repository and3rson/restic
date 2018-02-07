from unittest import TestCase
from restic.tests.app import app, reset


class GenericAPITest(TestCase):
    def setUp(self):
        reset()

    def test_list(self):
        _, response = app.test_client.get('/items')
        self.assertEqual(len(response.json), 2)
        self.assertEqual(response.json[0]['id'], 1)

    def test_retrieve(self):
        _, response = app.test_client.get('/items/3')
        self.assertEqual(response.status, 404)
        _, response = app.test_client.get('/items/2')
        self.assertEqual(response.status, 200)
        self.assertIsInstance(response.json, dict)
        self.assertEqual(response.json['id'], 2)

    def test_create(self):
        _, response = app.test_client.post('/items/', data='{}')
        self.assertEqual(response.status, 400)
        _, response = app.test_client.post('/items/3', data='{"name": "Foo"}')
        self.assertEqual(response.status, 405)
        _, response = app.test_client.post('/items/', data='{"name": "Foo"}')
        self.assertEqual(response.status, 201)
        _, response = app.test_client.get('/items/3')
        self.assertEqual(response.json['name'], 'Foo')

    def test_update(self):
        _, response = app.test_client.patch('/items/1', data='{"name": "Foo 2"}')
        self.assertEqual(response.status, 200)
        print(response.json)
        _, response = app.test_client.get('/items/1')
        self.assertEqual(response.json['name'], 'Foo 2')
        _, response = app.test_client.patch('/items/3', data='{}')
        self.assertEqual(response.status, 404)

        _, response = app.test_client.patch('/items/1', data='{"date_created": "garbage"}')
        self.assertEqual(response.status, 400)
        _, response = app.test_client.patch('/items/1', data='{"date_created": "2010-12-31 12:34:56.421337"}')
        self.assertEqual(response.status, 200)

    def test_delete(self):
        _, response = app.test_client.delete('/items/2')
        self.assertEqual(response.status, 204)
        _, response = app.test_client.get('/items/2')
        self.assertEqual(response.status, 404)

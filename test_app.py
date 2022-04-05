import unittest

from url_shortener import app
from url_shortener.models import Link
from url_shortener.utils import *

class TestRootRoute(unittest.TestCase):

    def setUp(self):
        self.client = app.test_client()
        self.response = self.client.get('/')
    
    def test_get_returns_200(self):
        self.assertEqual(self.response.status_code, 200)
    
    def test_get_response_has_json_content_type(self):
        self.assertEqual(self.response.content_type, 'application/json')

class TestDecodeRoute(unittest.TestCase):

    def setUp(self):
        self.client = app.test_client()
     
    def tearDown(self):
        Link.query.delete()
        
    def test_post_with_non_json_content_type_returns_400_and_error_message(self):
        response = self.client.post('/decode', content_type='text/pdf')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json['error_message'], 'Request content type is not application/json')
    
    def test_post_without_short_url_in_request_returns_400_and_error_message(self):
        response = self.client.post('/decode', json={'wrong-key': 'value'})
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json['error_message'], 'Request json body missing short_url key')
    
    def test_post_with_empty_short_url_in_request_returns_400_and_error_message(self):
        response = self.client.post('/decode', json={'short_url': ''})
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json['error_message'], 'short_url in request json body cannot by empty string')
    
    def test_post_with_short_url_as_None_in_request_returns_400_and_error_message(self):
        response = self.client.post('/decode', json={'short_url': None})
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json['error_message'], 'short_url in request json body cannot be None / null')
    
    def test_post_with_incorrect_base_url_returns_400_and_error_message(self):
        expected_error_message = 'short_url is invalid. Valid format - http://short.est/unique-string - Unique string can contain only a-z, A-Z and 0-9'
        response = self.client.post('/decode', json={'short_url': 'http://goo.gl/m8z4f458'})
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json['error_message'], expected_error_message)
    
    def test_post_with_correct_base_url_but_more_than_1_path_parameter_returns_400_and_error_message(self):
        expected_error_message = 'short_url is invalid. Valid format - http://short.est/unique-string - Unique string can contain only a-z, A-Z and 0-9'
        response = self.client.post('/decode', json={'short_url': 'http://short.est/w8po1nLP/second-path-parameter'})
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json['error_message'], expected_error_message)
    
    def test_post_with_correct_base_url_but_invalid_characters_in_unique_string_returns_400_and_error_message(self):
        expected_error_message = 'short_url is invalid. Valid format - http://short.est/unique-string - Unique string can contain only a-z, A-Z and 0-9'
        response = self.client.post('/decode', json={'short_url': 'http://short.est/p$!m9'})
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json['error_message'], expected_error_message)
    
    def test_post_with_correct_base_url_and_empty_unique_string_returns_400_and_error_message(self):
        expected_error_message = 'short_url is invalid. Valid format - http://short.est/unique-string - Unique string can contain only a-z, A-Z and 0-9'
        response = self.client.post('/decode', json={'short_url': 'http://short.est/'})
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json['error_message'], expected_error_message)
    
    def test_post_with_non_existent_short_url_returns_400_and_error_message(self):
        response = self.client.post('/decode', json={'short_url': 'http://short.est/nonexistent'})
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json['error_message'], 'URL does not exist in database')
    
    def test_post_with_valid_existing_short_url_returns_200_and_long_url(self):
        test_url = 'https://www.youtube.com/watch?v=dQw4w9WgXcQ'
        response = self.client.post('/encode', json={'long_url': test_url})
        short_url = response.json['short_url']
        response = self.client.post('/decode', json={'short_url': short_url})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['long_url'], test_url)

class TestEncodeRoute(unittest.TestCase):
    
    def setUp(self):
        self.client = app.test_client()
    
    def tearDown(self):
        Link.query.delete()
    
    def test_post_with_non_json_content_type_returns_400_and_error_message(self):
        response = self.client.post('/encode', content_type='text/plain')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json['error_message'], 'Request content type is not application/json')
    
    def test_post_without_long_url_in_request_returns_400_and_error_message(self):
        response = self.client.post('/encode', json={'wrong-key': 'value'})
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json['error_message'], 'Request json body missing long_url key')
    
    def test_post_with_empty_long_url_in_request_returns_400_and_error_message(self):
        response = self.client.post('/encode', json={'long_url': ''})
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json['error_message'], 'long_url in request json body cannot by empty string')
    
    def test_post_with_long_url_as_None_in_request_returns_400_and_error_message(self):
        response = self.client.post('/encode', json={'long_url': None})
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json['error_message'], 'long_url in request json body cannot be None / null')
    
    def test_reg_ex_match(self):
        response = self.client.post('/encode', json={'long_url': 'this is not a url'})
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json['error_message'], 'Provided URL is not a valid URL')
    
    def test_post_with_long_url_returns_201_and_shortened_url(self):
        test_url = 'https://www.this-is-a-long-url.com/with-additional-path-parameters'
        response = self.client.post('/encode', json={'long_url': test_url})
        self.assertEqual(response.status_code, 201)
        short_string = response.json['short_url'].split('/')[-1]
        db_url = Link.query.get(short_string).url
        self.assertEqual(db_url, test_url)
    
    def test_post_with_already_existing_long_url_returns_400_error_message_and_existing_shortened_url(self):
        test_url = 'https://www.google.com'
        response = self.client.post('/encode', json={'long_url': test_url})
        existing_short_url = response.json['short_url']
        response = self.client.post('/encode', json={'long_url': test_url})
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json['error_message'], 'URL has already been shortened before')
        self.assertEqual(response.json['short_url'], existing_short_url)

class TestBase62Conversion(unittest.TestCase):

    def test_input_zero_returns_zero(self):
        result = decimal_to_base_62(0)
        self.assertEqual(result, [0])
    
    def test_input_1_returns_1(self):
        result = decimal_to_base_62(1)
        self.assertEqual(result, [1])
    
    def test_input_63_returns_11(self):
        result = decimal_to_base_62(63)
        self.assertEqual(result, [1, 1])
    
    def test_input_64_returns_12(self):
        result = decimal_to_base_62(64)
        self.assertEqual(result, [1, 2])

class TestMapBase62ToChar(unittest.TestCase):

    def test_input_0_returns_a(self):
        char = map_base_62_digit_to_char(0)
        self.assertEqual(char, 'a')

    def test_input_65_returns_hyphen(self):
        char = map_base_62_digit_to_char(65)
        self.assertEqual(char, '-')


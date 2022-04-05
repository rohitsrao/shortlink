import random
import string

from datetime import datetime, timezone
from sqlalchemy import exc
from url_shortener import db
from url_shortener.models import Link

db.create_all()

def decimal_to_base_62(num):
    
    if num == 0:
        return [0]
    
    digits = []
    while num > 0:
        remainder = int(num % 62)
        digits.append(remainder)
        num = int(num / 62)
    digits.reverse()
    return digits

def map_base_62_digit_to_char(num):
    letters = list(string.ascii_lowercase) + list(string.ascii_uppercase) + [str(num) for num in range(0, 10)]
    try:
        char = letters[num]
    except IndexError as e:
        char = '-'
    return char

def unique_random_num_generator():
    dt = datetime.now()
    utc_time = dt.replace(tzinfo=timezone.utc)
    utc_timestamp = utc_time.timestamp()
    
    max_rand_range = 999
    random_num_1 = random.randint(1, max_rand_range)
    random_num_2 = random.randint(1, max_rand_range)
    random_num = random_num_1 / random_num_2
    
    unique_random_num = utc_timestamp + random_num
    
    unique_random_num = str(unique_random_num)
    unique_random_num = unique_random_num.split('.')
    unique_random_num = ''.join(unique_random_num)
    unique_random_num = int(unique_random_num)
    
    return unique_random_num

def generate_short_url_string():
    unique_random_num = unique_random_num_generator()
    digits = decimal_to_base_62(unique_random_num)
    short_url = [map_base_62_digit_to_char(digit) for digit in digits]
    short_url = ''.join(short_url)
    return short_url

def add_link_to_database(short, url):
    link = Link(short=short, url=url)
    
    return_dict = {}
    
    try:
        db.session.add(link)
        db.session.commit()
    except exc.IntegrityError as e:
        db.session.rollback()
        existing_link = Link.query.filter_by(url=url).first()
        return_dict['status'] = 'failed'
        return_dict['existing_short'] = existing_link.short
        return return_dict
    
    return_dict['status'] = 'success'
    return return_dict


import os
import django
from models import KeyWord


words = [
    'python',
    'вакансии',
    'вакансия',
    'работа',
    'джун',
    'IT',
    'компания',
    'занятость',
    'зарплата',
    'ЗП',
]

for word in words:
    obj, created = KeyWord.objects.get_or_create(word=word)
# -*- coding: utf-8 -*-
from setuptools import setup, find_packages

from model_log import __version__

long_description = """Simple model logging helper for django projects. Covers functionality of discovering action taken on object: DELETE, UPDATE, CREATE and creates and saves suitable message to database. Supports simple db.models.Models objects as well as forms, formset and inlineformset based on Django ORM Models."""


setup(
    name='model_log',
    version=".".join(map(str, __version__)),
    description='model_log reusable application for loggin models changes.',
    long_description=long_description,
    author='Wu Weiru',
    author_email='heizai3@gmail.com',
    url='https://github.com/nuty/django-model-log',
    packages=find_packages(),
    zip_safe=False,
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Framework :: Django',
    ],
    # test_suite='modelhistory.tests.runtests.runtests'
)

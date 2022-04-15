#!/usr/bin/env python

import uuid
import os
from setuptools import setup, find_packages
from pip._internal.req import parse_requirements

import djangow2ui

def get_requirements(source):
    try:
        install_reqs = parse_requirements(source, session=uuid.uuid1())
    except TypeError:
        # Older version of pip.
        install_reqs = parse_requirements(source)
    required = set([str(ir.req) for ir in install_reqs])
    return required

setup(
    name="django-w2ui",
    version=djangow2ui.__version__,
    description="Integration with W2UI for the Django web framework.",
    long_description="Integration with W2UI for the Django web framework.",
    author="Antonio Galea",
    author_email="antonio.galea@gmail.com",
    url="https://github.com/ant9000/django-w2ui",
    license="GPLv3",
    platforms="OS Independent",
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    classifiers=['Development Status :: 3 - Alpha',
                 'Environment :: Web Environment',
                 'Framework :: Django',
                 'Intended Audience :: Developers',
                 'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
                 'Operating System :: OS Independent',
                 'Programming Language :: Python',
                 'Topic :: Utilities'],
    install_requires=get_requirements('requirements.txt'),
)

import os
import re

from setuptools import find_packages, setup


setup(
    name="django-statusboard-notify",
    packages=find_packages(include=["statusboard_notify", "statusboard_notify.*"]),
    include_package_data=True,
    license='GPLv2+',
    description='Utility for django-statusboard to notify status changes',
    long_description=open('README.md').read(),
    long_description_content_type="text/markdown",
    url='http://github.com/edigiacomo/django-statusboard-notify',
    author='Emanuele Di Giacomo',
    author_email="emanuele@digiacomo.cc",
    python_requires=">=3.6",
    install_requires=[
        'django>=2.2', 'django-statusboard', 'pypandoc',
    ],
    extras_require={
        'with_telegram': 'python-telegram-bot',
        'with_matrix': 'matrix-nio',
    },
    test_suite="runtests.runtests",
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'License :: OSI Approved :: GNU General Public License v2 or later (GPLv2+)',
        'Framework :: Django',
        'Framework :: Django :: 3.2',
        'Framework :: Django :: 4.2',
        'Framework :: Django :: 5.0',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
    ],
)

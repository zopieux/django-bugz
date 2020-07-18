import os.path
from setuptools import setup, find_namespace_packages

with open(os.path.join(os.path.dirname(__file__), "README.md"), "r") as fh:
    long_description = fh.read()

setup(
    name="django-bugz",
    version='0.1.0',
    author="Alexandre Macabies",
    author_email="web+oss@zopieux.com",
    license="GPL3",
    packages=find_namespace_packages(include=['bugz', 'bugz.*']),
    include_package_data=True,
    description="A standalone Django issue tracking app.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    python_requires='>=3.7',
    package_data={'bugz': ['static/bugz/*', 'templates/bugz/*']},
    install_requires=[
        "bleach>=3",  # HTML sanitizer
        "rules>=2",  # Permission management
        "django>=2",
        "markdown>=3",
    ],
    classifiers=[
        'Environment :: Web Environment',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'Topic :: Internet :: WWW/HTTP',
    ],
    project_urls={
        'Source': 'https://github.com/zopieux/django-bugz/',
        'Issue Tracker': 'https://github.com/zopieux/django-bugz/issues',
    },
)

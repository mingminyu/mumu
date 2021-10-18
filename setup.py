from __future__ import absolute_import
import versioneer
from setuptools import setup, find_packages


def readme():
    with open('README.md', 'r') as f:
        return f.read()


setup(
    name='mumu',
    version=versioneer.get_version(),
    cmdclass=versioneer.get_cmdclass(),
    platforms=["all"],
    packages=find_packages(),
    url='https://github.com/mingminyu/mumu',
    license='Apache License, Version 2.0',
    author='yumingmin',
    author_email='yu_mingm623@163.com',
    long_description_content_type='text/markdown',
    long_description=readme(),
    maintainer='yumingmin',
    maintainer_email="yu_mingm623@163.com",
    classifiers=[
            'Programming Language :: Python :: 3.6',
            'Programming Language :: Python :: 3.7',
            'Programming Language :: Python :: 3.8',
            'Programming Language :: Python :: 3.9'
        ],
    keywords=('machine-learning python impala hive sql monitor'
              'email airflow'),
    install_package_data=True,
    install_requires=["impyla", "requests", "matplotlib"],
    zip_safe=False,
    extras_require={},
    description='mumu is an integrated tool for machine learning.'
)

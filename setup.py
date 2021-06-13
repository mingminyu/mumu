from setuptools import setup


def readme():
    with open('README.md', 'r') as f:
        return f.read()


setup(
    name='mumu',
    version='0.0.4',
    packages=[''],
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
    install_package_data=True,
    install_requires=[],
    zip_safe=False,
    description='mumu is an integrated tool for machine learning.'
)
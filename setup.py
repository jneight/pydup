# coding=utf-8

from setuptools import setup, find_packages

setup(
        name='pydup',
        version='0.10',
        install_requires=[],
        url='https://github.com/jneight/pydup',
        description='Simple implementation of LSH Algorithm',
        packages=find_packages(),
        include_package_data=True,
        license='Apache 2.0',
        classifiers=[
            'Environment :: Web Environment',
            'Intended Audience :: Developers',
            'License :: OSI Approved :: Apache Software License',
            'Operating System :: OS Independent',
            'Programming Language :: Python',
            'Programming Language :: Python :: 2.7',
            'Programming Language :: Python :: 3',
            ],
        author='Javier Cordero Martinez',
        author_email='jcorderomartinez@gmail.com'
)

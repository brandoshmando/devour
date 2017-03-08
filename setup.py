from setuptools import setup

setup(
    name='devour',
    version='0.4.3',
    url='',
    author='http://github.com/brandoshmando',
    author_email='brancraft@gmail.com',
    license='MIT',
    packages=['devour', 'devour.utils'],
    install_requires=[
        'pykafka',
        'kazoo'
    ],
    include_package_data=True,
    test_suite='nose.collector',
    tests_require=['nose'],
    zip_safe=False,
    entry_points={
        'console_scripts': [
            'devour = devour.bin.devour_commands:main'
        ]
    },
    keywords = ['kafka', 'django', 'pykafka', 'python', 'devour']
)

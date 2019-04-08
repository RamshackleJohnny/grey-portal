from setuptools import find_packages, setup

setup(
    name='portal',
    version='0.0.0',
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'flask',
        'gunicorn',
        'psycopg2',
    ],
    extras_require={
        'test': [
            'pytest',
            'coverage',
        ],
    },
)


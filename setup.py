from setuptools import setup, find_packages

setup(
    name="cronda",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        'click',
        'google-cloud-storage',
        'google-cloud-resource-manager',
        'google-auth',
        'fastapi>=0.68.0',
        'uvicorn>=0.15.0',
        'pydantic>=1.8.2',
        'python-multipart>=0.0.5',
        'jinja2>=2.11.3',
    ],
    entry_points={
        'console_scripts': [
            'cronda=src.cli.resource_cli:cli',
        ],
    },
)
"""Install airview."""
import setuptools

with open('README.md') as f:
  long_description = f.read()
description = 'Measure and share data from Raspberry Pi.'


install_requires = [
    'uvicorn',
    'fastapi',
    'pandas',
]


setuptools.setup(
    name='airview',
    author='Zeb Engberg',
    author_email='zebengberg@gmail.com',
    description=description,
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/zebengberg/airview',
    packages=setuptools.find_packages(),
    python_requires='>=3.9.0',
    install_requires=install_requires,
    version='0.0.1',
    license='MIT')

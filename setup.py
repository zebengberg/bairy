"""Install pypeck."""
import setuptools

with open('README.md') as f:
  long_description = f.read()
description = 'Display data from Raspberry Pi.'


install_requires = [
    'uvicorn',
    'fastapi',
    'dash',
    'plotly',
    'pandas',
    'requests',
    'smbus2',
    'gpiozero'
]

setuptools.setup(
    name='pypeck',
    author='Zeb Engberg',
    author_email='zebengberg@gmail.com',
    description=description,
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/zebengberg/pypeck',
    packages=setuptools.find_namespace_packages(),
    python_requires='>=3.7.0',
    install_requires=install_requires,
    include_package_data=True,
    version='0.0.1',
    license='MIT')

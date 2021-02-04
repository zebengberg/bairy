"""Install bairy."""
import setuptools

with open('README.md') as f:
  long_description = f.read()
description = 'Display data from Raspberry Pi.'


install_requires = [
    'uvicorn',
    'fastapi',
    'pydantic',
    'dash',
    'plotly',
    'pandas',
    'nest_asyncio',
    'aiohttp',
    'smbus2',
    'gpiozero'
]

setuptools.setup(
    name='bairy',
    author='Zeb Engberg',
    author_email='zebengberg@gmail.com',
    description=description,
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/zebengberg/bairy',
    packages=setuptools.find_namespace_packages(exclude=['tests*']),
    python_requires='>=3.7.0',
    install_requires=install_requires,
    entry_points={'console_scripts': ['bairy = bairy.__main__:main']},
    version='0.1.4',
    classifiers=['License :: OSI Approved :: MIT License',
                 'Programming Language :: Python :: 3',
                 'Programming Language :: Python :: 3.7',
                 'Topic :: Internet :: WWW/HTTP :: WSGI',
                 'Topic :: Scientific/Engineering :: Visualization'],
    license='MIT')

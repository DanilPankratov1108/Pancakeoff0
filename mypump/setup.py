
from setuptools import setup, find_packages

def readme():
  with open('README.md', 'r') as f:
    return f.read()

setup(
  name='mypump',
  version='0.0.1',
  author='Pancakeoff',
  author_email='gamerx66@yandex.ru',
  description='Библиотека команд для управления насосом Runze Fluid',
  long_description=readme(),
  long_description_content_type='text/markdown',
  url='https://github.com/DanilPankratov1108/Pancakeoff/tree/main/mypump',
  packages=find_packages(),
  install_requires=['requests>=2.25.1'],
  classifiers=[
    'Programming Language :: Python :: 3.11',
    'License :: OSI Approved :: MIT License',
    'Operating System :: OS Independent'
  ],
  keywords='files speedfiles ',
  project_urls={
    'GitHub': 'https://github.com/DanilPankratov1108/Pancakeoff/tree/main/mypump'
  },
  python_requires='>=3.6'
)
from setuptools import setup, find_packages

setup_requires = []

install_requires = [
    'PyMySQL==0.7.11'
]

dependency_link = []

setup(
    name='NpmCrawler',
    version='1.0',
    description='Npm module crawl',
    author='Young Jae, Shin',
    author_email='youngjae82.shin@secui.com',
    packages=find_packages(),
    install_requires=install_requires

)

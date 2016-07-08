from setuptools import setup

with open('README.rst') as f:
    long_description = f.read()

with open('requirements.txt') as r:
    requirements = r.read()
req_list = requirements.split('\n')

setup(
    name='DPlayer',
    version='1.0.1',
    install_requires=req_list,
    description='A music player',
    long_description=long_description,
    url='https://github.com/DanislavKirov/DPlayer',
    author='Danislav Kirov',
    author_email='danislav.kirov@gmail.com',
    license='GNU GPL v2',
    packages=['dplayer'],
    package_data={'dplayer': ['icons/*.png']},
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: End Users/Desktop',
        'License :: OSI Approved :: GNU General Public License v2 (GPLv2)',
        'Natural Language :: English',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python :: 3.5',
        'Topic :: Multimedia :: Sound/Audio :: Players'
    ],
    keywords='music player'
)

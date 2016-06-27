from setuptools import setup

with open('README.md') as f:
    long_description = f.read()

setup(
    name='DPlayer',
    version='0.1.0',
    description='A music player',
    long_description=long_description,
    url='https://github.com/DanislavKirov/DPlayer',
    author='Danislav Kirov',
    author_email='danislav.kirov@gmail.com',
    license='GNU GPL v2',
    packages=['dplayer'],
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: End Users/Desktop',
        'License :: OSI Approved :: GNU General Public License v2 (GPLv2)',
        'Natural Language :: English',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python :: 3.5',
        'Topic :: Multimedia :: Sound/Audio :: Players :: MP3'
    ],
    keywords='music player'
)

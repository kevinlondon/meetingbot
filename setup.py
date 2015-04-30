from distutils.core import setup

setup(
    name='meetingbot',
    version='0.1.0',
    packages=['meetingbot', ],
    description="Send notifications to meeting attendees.",
    url="http://github.com/kevinlondon/meetingbot",
    license='MIT',
    author="Kevin London",
    author_email="kevinlondon@gmail.com",
    long_description=open('README.md').read(),
    include_package_data=True,
    classifier=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Environment :: Console',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
    ],
    install_requires=[
        "arrow>=0.5.4",
        "google-api-python-client>=1.4.0",
        "pycrypto>=2.6.1",
        "hypchat>=0.18",
        "pypubsub>=3.3.0",
    ]
)

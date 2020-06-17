from setuptools import setup

setup(
    name='sup',
    version='0.1.0',
    py_modules=['sup'],
    install_requires=[
        'Click',
        'parsedatetime',
        'PyGithub',
        'python-dotenv',
        'python-frontmatter',
        'pytz',
        'pyunfurl',
        'urlextract',
    ],
    entry_points='''
        [console_scripts]
        sup=sup:main
    ''',
)

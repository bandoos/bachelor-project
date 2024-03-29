from setuptools import setup, find_namespace_packages
setup(
    name="sim",
    version="0.1",
    summary="""
    Bachelor Project software, Inequality in Proof-of-stake Schemes: A simulation study.
    """,
    author='Luca Bandelli',
    author_email='l.bandelli@student.rug.nl',
    packages=find_namespace_packages(include=['sim.*']),
    entry_points={
        'setuptools.installation': [
            'eggsecutable = sim.core.main:main',
        ],
        'console_scripts': [
            'sim-stake = sim.core.main:main'
        ]
    },
    install_requires=[
        'numpy',
        'scipy',
        'matplotlib',
        'seaborn',
        'tabulate',
        'statsmodels',
        'jupyter',
        'argcomplete',
        'coloredlogs',
        'python-dotenv',
        'ipython',
        'sphinx',
        'groundwork-sphinx-theme',
        'celery==4.4.3',
        'pymongo',
        'redis',
    ],
    package_data={
        # If any package contains *.txt or *.rst files, include them:
        '': ['*.txt', '*.rst', "*.sh","*.edn"],
    }
)

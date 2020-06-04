from setuptools import setup, find_namespace_packages
setup(
    name="sim.core",
    version="0.1",
    packages=find_namespace_packages(include=['sim.*']),
    entry_points={
        'setuptools.installation': [
            'eggsecutable = sim.core.main:main',
        ]
    },
    package_data={
        # If any package contains *.txt or *.rst files, include them:
        '': ['*.txt', '*.rst', "*.sh","*.edn"],
    }
)


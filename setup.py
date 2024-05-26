from setuptools import setup, find_packages

setup(
    name="ClientApplication",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        # Dependencies like 'requests' for HTTP communication, etc.
        'requests',
        'pytest',    # For testing purposes
    ],
    entry_points={
        # If your application has a specific entry point for execution
        'console_scripts': [
            'start-client=src.client:main',  # Adjust depending on actual implementation
        ],
    },
)
from setuptools import setup, find_packages

setup(
    name="matverse-copilot",
    version="1.0.0",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'web3>=6.0.0',
        'watchdog>=3.0.0',
        'tweepy>=4.14.0',
        'python-dotenv>=1.0.0',
        'requests>=2.31.0',
        'pillow>=10.0.0',
        'click>=8.1.0',
        'colorama>=0.4.6',
        'psutil>=5.9.0',
        'schedule>=1.2.0',
    ],
    entry_points={
        'console_scripts': [
            'matverse-copilot=src.cli:main',
        ],
    },
    author="MatVerse Hub",
    author_email="contact@matverse.io",
    description="Automated deployment and NFT minting system for MatVerse",
    long_description=open('README.md').read(),
    long_description_content_type="text/markdown",
    url="https://github.com/MatVerse-Hub/test",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
    python_requires='>=3.8',
)

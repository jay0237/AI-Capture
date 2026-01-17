from setuptools import setup, find_packages

setup(
    name="screensense_ai",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        'opencv-python',
        'mss',
        'pywin32',
        'numpy',
        'pillow',
    ],
    python_requires='>=3.6',
)

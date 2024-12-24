from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="orionwave",  # Changed from voicechanger to match directory
    version="1.0.0",
    author="Pradyumn Tandon",
    author_email="pradyumn.tandon@hotmail.com",
    description="Professional real-time voice changing and audio processing system",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Gamecooler19/orionwave",
    packages=find_packages(include=['orionwave', 'orionwave.*']),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Multimedia :: Sound/Audio :: Speech",
        "Topic :: Multimedia :: Sound/Audio :: Sound Synthesis",
    ],
    python_requires=">=3.8",
    install_requires=[
        "numpy>=1.21.0",
        "scipy>=1.7.0",
        "pyaudio>=0.2.11",
        "pyyaml>=6.0",
        "sounddevice>=0.4.1",
    ],
    extras_require={
        'gui': [
            'PyQt5>=5.15.0',
            'pyqtgraph>=0.12.0',
        ],
        'audio': [
            'librosa>=0.8.1',
            'soundfile>=0.10.0',
            'webrtcvad>=2.0.10',
            'pyrubberband>=0.3.0',
            'resampy>=0.3.1', 
        ],
        'effects': [
            'pyloudnorm>=0.1.0',
            'pedalboard>=0.5.4',
        ],
        'network': [
            'websockets>=10.0',
            'aiohttp>=3.8.0',
            'fastapi>=0.68.0',
            'uvicorn>=0.15.0',
        ],
        'ml': [
            'torch>=1.9.0',
            'torchaudio>=0.9.0',
        ],
        'dev': [
            'pytest>=6.0.0',
            'pytest-cov>=2.12.0',
            'black>=21.0.0',
            'isort>=5.0.0',
            'mypy>=0.900',
            'flake8>=3.9.0',
            'sphinx>=4.0.0',
        ],
    },
    entry_points={
        'console_scripts': [
            'orionwave=orionwave.cli:main',
            'orionwave-gui=orionwave.gui.main_window:main [gui]',
            'orionwave-server=orionwave.network.server:main [network]',
        ],
    },
    include_package_data=True,
    package_data={
        'orionwave': [
            'config/*.yaml',
            'presets/*.json',
            'models/*.pth',
        ],
    },
)

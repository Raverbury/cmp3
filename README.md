# Custom Music Player 3

## Setup
Use conda or venv to set up a development environment

- Installing packages
```commandline
pip install -r requirements.txt
```

## Build
### Windows
```commandline
python -m nuitka --standalone app.py --plugin-enable=pyside6 --disable-console
```
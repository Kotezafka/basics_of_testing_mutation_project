def init():
    return {
        'runner': 'python -m pytest',
        'python_version': '3.10',
        'python_path': '.venv/bin/python',
        'paths_to_mutate': ['billing'],
        'test_command': 'python -m pytest',
    } 
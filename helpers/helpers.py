import os


def get_project_root() -> str:
    current_file = os.path.abspath(__file__)
    while not os.path.isfile(os.path.join(current_file, 'test_task.pdf')):
        current_file = os.path.dirname(current_file)

    return current_file

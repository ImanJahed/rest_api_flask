import subprocess


def flask_run():
    try:
        subprocess.run(['flask', 'run', '--debug'])

    except subprocess.CalledProcessError as e:
        print('Error occurred', e)


if __name__ == '__main__':
    flask_run()

import os

if __name__ == '__main__':
    dataFile = os.environ.get('DATAFILE', '')

    print(f"*** Got dataFile from env: {dataFile}")

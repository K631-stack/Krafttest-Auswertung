import glob
import os
import pandas as pd


def read_null_files(folder):
    data = []
    column_names = ['date', 'tag', 'comment', 'unit', 'max', 'avg', 'duration']

    for filename in glob.glob(os.path.join(os.getcwd(), folder, '*.null')):
        if 'endurance' not in filename:
            with open(filename, "r") as file:

                # disregard rof measurements
                tag = file.readline()
                if 'rof' not in tag:
                    measurement = file.readline().replace("\"", "")
                    measurement = measurement.replace(",\n", "").split(",")
                    data.append(measurement)

    data_frame = pd.DataFrame(data, columns=column_names)
    return data_frame


def read_csv_files(folder):
    data = []
    column_names = ['date', 'tag', 'comment', 'unit', 'max', 'avg', 'duration']

    for filename in glob.glob(os.path.join(os.getcwd(), folder, '*.csv')):
        with open(filename, "r") as file:
            # disregard rof measurements
            tag = file.readline()
            if 'rof' not in tag:
                measurement = file.readline().replace("\"", "")
                measurement = measurement.replace(",\n", "")
                measurement = measurement.replace("\n", "").split(",")
                if len(measurement) == 9:
                    del measurement[:2]
                data.append(measurement)

    data_frame = pd.DataFrame(data, columns=column_names)
    return data_frame


def read_files(folder='Data'):
    """
    Takes a folder of .null / .csv files of measurements and converts it into a dataframe
    :param folder: name of the sub folder that contains the files
    :return: Dataframe with one measurement per row of form ['date', 'tag', 'comment', 'unit', 'max', 'avg', 'duration']
    """
    null_files = read_null_files(folder)
    csv_files = read_csv_files(folder)
    return pd.concat([null_files, csv_files])

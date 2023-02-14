import numpy as np
import pandas as pd


def clean_data(data_one_hand):
    """
    param data_one_hand: Dataframe of form ['date', 'tag', 'comment', 'unit', 'max', 'avg', 'duration']
    :return: Dataframe of form ['date', 'max', 'name', 'hand', 'test']
    """
    # get name, hand, and type of test from tag column - clean up unneeded columns
    data_one_hand[['name', 'hand', 'test']] = data_one_hand.tag.str.split(" ", expand=True).drop([3], axis=1)

    data_one_hand = data_one_hand.drop(['tag', 'duration', 'avg', 'unit'], axis=1)
    data_one_hand = data_one_hand[data_one_hand['test'].isin(['Finger', '90', '120'])]

    # convert str-Date to datetime -> back to str in desired formatting -> back to datetime
    data_one_hand['date'] = pd.to_datetime(data_one_hand['date'])
    data_one_hand['date'] = data_one_hand['date'].dt.strftime('%d-%m-%Y')
    data_one_hand['date'] = pd.to_datetime(data_one_hand['date'], format='%d-%m-%Y')

    data_one_hand['max'] = data_one_hand['max'].apply(pd.to_numeric)

    data_one_hand = data_one_hand.rename(columns={"comment": "weight"})
    data_one_hand['weight'] = data_one_hand['weight'].apply(pd.to_numeric).fillna(-1)

    # remove duplicate measurements
    # duplicate is same test for same person, day, and hand
    data_one_hand = data_one_hand.sort_values(by=['date', 'name', 'test', 'hand', 'max'], ascending=True)
    data_one_hand = data_one_hand.drop_duplicates(subset=['date', 'name', 'test', 'hand'], keep='last')

    # get sum of both hands for all measurements
    data_both_hands = data_one_hand.groupby([
        pd.Grouper(key='date', freq='D'),
        'test',
        'name'
    ]).sum(numeric_only=True).reset_index()
    data_both_hands['hand'] = 'both'

    # don't do sum of weight
    data_both_hands['weight'] = data_both_hands['weight'] * 0.5

    return pd.concat([data_one_hand, data_both_hands])


def filter_people(data, people_filter):
    if people_filter:
        return data[data['name'].isin(people_filter)]
    return data


def split_data_per_person(data_both_hands, mode):
    measurements_per_person = {}

    for person in data_both_hands['name'].unique():
        data_person = data_both_hands[data_both_hands.name == person]
        data_person = calculate_relative_measurements(data_person, mode)
        measurements_per_person[person] = data_person\
            .pivot(index='date', columns=('test', 'hand'), values='max')\
            .fillna(method='ffill')

    return measurements_per_person


def calculate_relative_measurements(data_absolute, mode):
    """
    Sets strength values of measurements in context to weight of person.
    max is calculated as a percentage of body weight at time of the test.
    if no weight data is available absolute values are use.
    If no current body weight is available the most recent one is used.
    If the first measurement has no weight the weight of the next following measurement with weight data is used.
    param data_absolute:  measurements of absolute max values in Kg for one person.
    :return: measurements with relative max values as percentage of body weight of person.
    """

    if mode == 'absolute':
        return data_absolute.drop(['weight'], axis=1)

    elif mode == 'relative':
        data_absolute = data_absolute.replace({-1: np.nan})

        # all NaN in weight if person has no weight measurement
        if data_absolute['weight'].isnull().values.all():
            return data_absolute.drop(['weight'], axis=1)

        # fill missing weight measurements
        data_absolute = data_absolute\
            .sort_values(by=['date'], ascending=True)\
            .fillna(method='ffill')\
            .fillna(method='bfill')
        # TODO: Check for mistakes in the input data i.e. different weights for tests on the same day Bsp. Lausi Finger 17.09.2022

        # calculate relative max
        data_absolute['max'] = data_absolute['max'] / data_absolute['weight']
        return data_absolute.drop(['weight'], axis=1)

    else:
        raise ValueError('mode must be relative or absolute')


def process_data(imported_data, people_to_plot, data_source, mode):
    if data_source == 'new':
        cleaned_data = clean_data(imported_data)
        cleaned_data.to_csv('ProcessedData.csv', sep='\t', encoding='utf-8', index=False)
    elif data_source == 'old':
        cleaned_data = pd.read_csv('ProcessedData.csv', sep='\t', encoding='utf-8')
        # reformat date column
        cleaned_data['date'] = pd.to_datetime(cleaned_data['date'])
        cleaned_data['date'] = cleaned_data['date'].dt.strftime('%d-%m-%Y')
        cleaned_data['date'] = pd.to_datetime(cleaned_data['date'], format='%d-%m-%Y')
    else:
        raise ValueError('data source must be old or new')

    filtered_data = filter_people(cleaned_data, people_to_plot)
    return split_data_per_person(filtered_data, mode)



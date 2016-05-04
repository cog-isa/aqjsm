import pandas as pd
from aq.aq_description import Fact

column_ranges = {}
column_names = []


def load_data(file_path, class_index, nominal_data):
    data = pd.read_csv(file_path, encoding='cp1251', sep=';', index_col=False, na_values='?', decimal=',')
    column_names.extend(list(data.columns))
    data.columns = [Fact.canon_prefix + str(x) for x in range(data.shape[1])]

    # categorize nominal columns
    if nominal_data:
        for nominal_line in nominal_data.split(';'):
            nom_column, nom_data = nominal_line.split(':')
            nom_id = int(nom_column)
            data.iloc[:, nom_id] = data.iloc[:, nom_id].astype('category')
            data.iloc[:, nom_id] = data.iloc[:, nom_id].cat.rename_categories(nom_data.split(','))

    # discretize all non categorical columns
    for index, column in enumerate(data.columns.values):
        if not data[column].dtype.name == 'category':
            data[column] = pd.cut(data[column], 3)
            column_ranges[column_names[index]] = data[column].cat.categories.values
            data[column] = data[column].cat.rename_categories(['1', '2', '3'])

    return data, Fact.canon_prefix + str(class_index)

import pandas as pd

data = pd.read_csv('psy_20151221.csv', encoding='cp1251', sep=';', index_col=False, na_values='?', decimal=',')
nominal_data = '0:1,2'
for nominal_line in nominal_data.split(';'):
    nom_column, nom_data = nominal_line.split(':')
    nom_id = int(nom_column)
    data.iloc[:, nom_id] = data.iloc[:, nom_id].astype('category')
    data.iloc[:, nom_id] = data.iloc[:, nom_id].cat.rename_categories(nom_data.split(','))

# discretize all non categorical columns
for index, column in enumerate(data.columns.values):
    if not data[column].dtype.name == 'category':
        data[column] = pd.cut(data[column], 3)
        data[column] = data[column].cat.rename_categories(['1', '2', '3'])

f = open('psy_20151221_d.gqj', 'w')
f.write('1\n')
f.write(','.join(map(str, range(1, data.shape[1] + 1))) + '\n')
f.write('1:1,2;' + ';'.join([str(x) + ':1,2,3' for x in range(2, data.shape[1] + 1)]) + '\n')
f.flush()
f.close()

data.to_csv('psy_20151221_d.gqj', encoding='cp1251', sep='\t', index=False, mode='a', float_format=',', na_rep='?',
            header=True)

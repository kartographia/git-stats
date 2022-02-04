import pandas as pd

import matplotlib.pyplot as plt


user_to_org = {
    'Peter Borissow': 'Kartographia',
    'Jordan.Dobson': 'Culmen',
    'JohnKim': 'Culmen',
    'pborissow': 'Kartographia',
    'Peter.Borissow': 'Kartographia',
    'Logan Mohseni': 'Culmen',
    'Peter': 'Kartographia',
    'Kenneth': 'Kartographia',
    'Jan': 'Kartographia',
    'Jordan': 'Culmen',
    'jhkcm0219': 'Culmen',
    'sashatrubetskoy': 'Kartographia',
    'Erik Raith': 'Kartographia',
    'Velazquez': 'Azimuth1',
    'swordysrepo': 'Kartographia',
    'Sasha Trubetskoy': 'Kartographia',
    'Ryan V': 'Azimuth1',
    'Amanda W': 'Azimuth1',
    'Sasha T': 'Kartographia',
}

user_to_user = {
    'Peter Borissow': 'Peter Borissow',
    'Jordan.Dobson': 'Jordan Dobson',
    'JohnKim': 'John Kim',
    'pborissow': 'Peter Borissow',
    'Peter.Borissow': 'Peter Borissow',
    'Logan Mohseni': 'Logan Mohseni',
    'Peter': 'Peter Borissow',
    'Kenneth': 'Ken McQuade',
    'Jan': 'Jan',
    'Jordan': 'Jordan Dobson',
    'jhkcm0219': 'John Kim',
    'sashatrubetskoy': 'Sasha Trubetskoy',
    'Erik Raith': 'Erik Raith',
    'Velazquez': 'Ryan Velazquez',
    'swordysrepo': 'Ken McQuade',
    'Sasha Trubetskoy': 'Sasha Trubetskoy',
    'Ryan V': 'Ryan Velazquez',
    'Amanda W': 'Amanda West',
    'Sasha T': 'Sasha Trubetskoy',
}



df = pd.read_csv('allCommits.csv')

df['org'] = df['username'].map(user_to_org)
df['user'] = df['username'].map(user_to_user)
df = df[df['num_lines_changed'] < 10000]

df.to_csv('allCommits-users-orgs.csv')

df['date'] = pd.to_datetime(df['date'])
df = df.sort_values('date')

# df = df[df['date']>'2021-02-01']
GROUPCOL = 'user'

cumlines = df.groupby(GROUPCOL)['num_lines_changed'].cumsum()
df['cum_lines_changed'] = cumlines
print(df)


print(df.sort_values('num_lines_changed')[['date', 'username', 'num_lines_changed']])

fig, ax = plt.subplots()
for user_name, user_df in df.groupby(GROUPCOL):
    user_df[user_name] = user_df['cum_lines_changed']
    user_df.plot('date', user_name, ax=ax)
plt.grid()
plt.title('Cumulative lines changed')
plt.show()
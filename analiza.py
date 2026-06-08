import pandas as pd

#wczytanie danych

LATA = [str(r) for r in range(2015, 2023)]

def wczytaj_plik(sciezka, nazwa_zmiennej):
    df = pd.read_csv(sciezka, sep=';', encoding='utf-8', dtype={'Kod': str})
    df = df.loc[:, ~df.columns.str.startswith('Unnamed')]
    df.columns = ['kod', 'nazwa'] + [f'{nazwa_zmiennej}_{r}' for r in range(2015, 2025)]
    df = df[df['kod'].str.len() == 7]
    df = df[~df['kod'].str.endswith('000')]
    df = df.reset_index(drop=True)
    return df

dochody = wczytaj_plik(
    'dane/FINA_2622_CTAB_20260608161005.csv',
    'dochody'
)
wydatki = wczytaj_plik(
    'dane/FINA_2633_CTAB_20260608160916.csv',
    'wydatki'
)
ludnosc = wczytaj_plik(
    'dane/LUDN_1336_CTAB_20260608161213.csv',
    'ludnosc'
)

#laczenie w df
df = dochody.merge(wydatki[['kod'] + [f'wydatki_{r}' for r in range(2015, 2025)]], on='kod')
df = df.merge(ludnosc[['kod'] + [f'ludnosc_{r}' for r in range(2015, 2025)]], on='kod')

#typ gminy z TERYT
def typ_gminy(kod):
    ostatnia = kod[-1]
    typy = {
        '1': 'miejska',
        '2': 'wiejska',
        '3': 'miejsko-wiejska',
        '4': 'miejsko-wiejska',
        '5': 'miejsko-wiejska',
        '8': 'dzielnica/delegatura',
        '9': 'obszar wiejski'
    }
    return typy.get(ostatnia, 'inny')

df['typ'] = df['kod'].apply(typ_gminy)

#zamiana kolumn liczbowych przecinek na kropke
kolumny_liczbowe = [f'{zm}_{r}' for zm in ['dochody', 'wydatki', 'ludnosc'] for r in range(2015, 2025)]
for kol in kolumny_liczbowe:
    df[kol] = df[kol].astype(str).str.replace(',', '.', regex=False)
    df[kol] = pd.to_numeric(df[kol], errors='coerce')

#oblicenie per capita
for r in range(2015, 2023):
    df[f'dochody_pc_{r}'] = df[f'dochody_{r}'] / df[f'ludnosc_{r}']
    df[f'wydatki_pc_{r}'] = df[f'wydatki_{r}'] / df[f'ludnosc_{r}']

#podglad
print(df.shape)
print(df['typ'].value_counts())
print(df.head(3))

import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')
import os

os.makedirs('wykresy', exist_ok=True)

#statystki opisowe

for zm in ['dochody_pc', 'wydatki_pc']:
    kolumny = [f'{zm}_{r}' for r in range(2015, 2023)]
    df[f'{zm}_srednia'] = df[kolumny].mean(axis=1)

print("\n--- Statystyki opisowe ---")
print(df[['dochody_pc_srednia', 'wydatki_pc_srednia']].describe().round(2))

#wykres: trend avg wydatkow inwestycyjnych per capita 
fig, ax = plt.subplots(figsize=(10, 6))

for typ in ['miejska', 'miejsko-wiejska', 'wiejska']:
    podzb = df[df['typ'] == typ]
    srednie = [podzb[f'wydatki_pc_{r}'].mean() for r in range(2015, 2023)]
    ax.plot(range(2015, 2023), srednie, marker='o', label=typ)

ax.set_title('Średnie wydatki inwestycyjne per capita wg typu gminy (2015–2022)')
ax.set_xlabel('Rok')
ax.set_ylabel('PLN per capita')
ax.legend()
ax.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig('wykresy/trend_wydatki_typ.png', dpi=150)
plt.close()
print("Zapisano: wykresy/trend_wydatki_typ.png")

#wykres: boxplot wydatkow inwestycyjnych per capita w 2022 w typu gminy
fig, ax = plt.subplots(figsize=(9, 6))

dane_box = [
    df[df['typ'] == typ]['wydatki_pc_2022'].dropna().values
    for typ in ['miejska', 'miejsko-wiejska', 'wiejska']
]
ax.boxplot(dane_box, labels=['miejska', 'miejsko-wiejska', 'wiejska'], showfliers=False)
ax.set_title('Rozkład wydatków inwestycyjnych per capita w 2022 r. wg typu gminy')
ax.set_xlabel('Typ gminy')
ax.set_ylabel('PLN per capita')
ax.grid(True, alpha=0.3, axis='y')
plt.tight_layout()
plt.savefig('wykresy/boxplot_wydatki_2022.png', dpi=150)
plt.close()
print("Zapisano: wykresy/boxplot_wydatki_2022.png")
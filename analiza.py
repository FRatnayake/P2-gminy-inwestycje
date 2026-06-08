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
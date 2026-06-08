import pandas as pd
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# --- Testy podstawowe ---

def test_kolumny_po_wczytaniu():
    """Sprawdza czy przetworzony dataset zawiera wymagane kolumny."""
    df = pd.read_csv('dane/gminy_przetworzone.csv', sep=';', dtype={'kod': str})
    wymagane = ['kod', 'nazwa', 'typ', 'dochody_pc_2022', 'wydatki_pc_2022']
    for kol in wymagane:
        assert kol in df.columns, f"Brak kolumny: {kol}"
    print("OK: wszystkie wymagane kolumny obecne")

def test_liczba_gmin():
    """Sprawdza czy liczba gmin mieści się w oczekiwanym przedziale."""
    df = pd.read_csv('dane/gminy_przetworzone.csv', sep=';', dtype={'kod': str})
    assert 2400 < len(df) < 2700, f"Nieoczekiwana liczba gmin: {len(df)}"
    print(f"OK: liczba gmin = {len(df)}")

def test_typy_gmin():
    """Sprawdza czy kolumna typ zawiera tylko oczekiwane wartości."""
    df = pd.read_csv('dane/gminy_przetworzone.csv', sep=';', dtype={'kod': str})
    dozwolone = {'miejska', 'wiejska', 'miejsko-wiejska', 'dzielnica/delegatura', 'obszar wiejski', 'inny'}
    faktyczne = set(df['typ'].unique())
    nieznane = faktyczne - dozwolone
    assert not nieznane, f"Nieznane typy gmin: {nieznane}"
    print(f"OK: typy gmin = {faktyczne}")

def test_brak_ujemnych_wydatkow():
    """Sprawdza czy wydatki inwestycyjne pc są nieujemne."""
    df = pd.read_csv('dane/gminy_przetworzone.csv', sep=';', dtype={'kod': str})
    for r in range(2015, 2023):
        kol = f'wydatki_pc_{r}'
        ujemne = df[df[kol] < 0]
        assert len(ujemne) == 0, f"Ujemne wydatki w {r}: {len(ujemne)} gmin"
    print("OK: brak ujemnych wydatków inwestycyjnych")

def test_kody_gmin_7_cyfr():
    """Sprawdza czy wszystkie kody gmin mają 7 cyfr."""
    df = pd.read_csv('dane/gminy_przetworzone.csv', sep=';', dtype={'kod': str})
    niepoprawne = df[df['kod'].str.len() != 7]
    assert len(niepoprawne) == 0, f"Kody o złej długości: {len(niepoprawne)}"
    print("OK: wszystkie kody gmin mają 7 cyfr")

if __name__ == '__main__':
    test_kolumny_po_wczytaniu()
    test_liczba_gmin()
    test_typy_gmin()
    test_brak_ujemnych_wydatkow()
    test_kody_gmin_7_cyfr()
    print("\nWszystkie testy zaliczone.")
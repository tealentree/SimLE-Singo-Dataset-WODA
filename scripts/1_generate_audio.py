import os
import random
import numpy as np
import librosa
import soundfile as sf
import glob
import warnings

# Ignorujemy ostrzeżenia librosa
warnings.filterwarnings('ignore')

# --- 1. KONFIGURACJA STRUKTURY I KLAS ---
FOLDER_WEJSCIOWY = "1_raw_audio/targets"
PLIK_DRONA = "1_raw_audio/backgrounds/drone-sound.wav"
FOLDER_WYJSCIOWY = "2_processed_audio"

DLUGOSC_SEK = 30.0
SR = 44100
ILOSC_WERSJI = 5  # Ile 30-sekundowych próbek wygenerować dla każdej klasy

# Słownik definiujący zasady dla poszczególnych folderów
KLASY_DZWIEKOW = {
    "woda": {"typ": "ciagly"},
    "pozar": {"typ": "ciagly"},
    "kolumna": {"typ": "ciagly"},
    "krab": {"typ": "przerywany", "liczba": 5},
    "bomba": {"typ": "przerywany", "liczba": 5},
    "karabin": {"typ": "przerywany", "liczba": 3}
}

def przygotuj_podklad_drona(calkowita_dlugosc_probki):
    """Wczytuje i zapętla szum drona do 30 sekund."""
    try:
        szum_drona, _ = librosa.load(PLIK_DRONA, sr=SR)
        plotno = np.copy(szum_drona)
        # Zapętlanie, jeśli nagranie jest za krótkie
        while len(plotno) < calkowita_dlugosc_probki:
            plotno = np.concatenate((plotno, plotno))
        
        plotno = plotno[:calkowita_dlugosc_probki]
        # TWOJA MODYFIKACJA: Podbicie głośności drona
        plotno = plotno * 1.5 
        return plotno
    except Exception as e:
        print(f"❌ Błąd wczytywania szumu drona: {e}")
        print(f"Upewnij się, że plik istnieje w: {PLIK_DRONA}")
        return None

def wczytaj_pule_dzwiekow(sciezka_folderu):
    """Wczytuje wszystkie pliki .wav z danego folderu (np. wszystkie nagrania Kraba)."""
    pliki_wav = glob.glob(os.path.join(sciezka_folderu, "*.wav"))
    zaladowane = []
    for plik in pliki_wav:
        try:
            dzwiek, _ = librosa.load(plik, sr=SR)
            zaladowane.append(dzwiek)
        except Exception as e:
            print(f"Błąd ładowania {plik}: {e}")
    return zaladowane

def generuj_dataset():
    calkowita_dlugosc_probki = int(DLUGOSC_SEK * SR)
    
    # 1. Przygotowanie tła
    podklad_drona_bazowy = przygotuj_podklad_drona(calkowita_dlugosc_probki)
    if podklad_drona_bazowy is None: return

    # 2. Główna pętla idąca przez wszystkie klasy zdefiniowane w słowniku
    for nazwa_klasy, konfiguracja in KLASY_DZWIEKOW.items():
        folder_zrodlowy = os.path.join(FOLDER_WEJSCIOWY, nazwa_klasy)
        folder_docelowy = os.path.join(FOLDER_WYJSCIOWY, nazwa_klasy)
        
        # Wczytujemy wszystkie dostępne warianty dźwięków dla danej klasy
        pula_dzwiekow = wczytaj_pule_dzwiekow(folder_zrodlowy)
        
        if not pula_dzwiekow:
            print(f"⚠️ Pomijam klasę '{nazwa_klasy}': Brak plików .wav w {folder_zrodlowy}")
            continue

        os.makedirs(folder_docelowy, exist_ok=True)
        print(f"\n⚙️ Przetwarzam klasę: {nazwa_klasy.upper()} (Typ: {konfiguracja['typ']}, Źródeł: {len(pula_dzwiekow)})")
        
        for i in range(ILOSC_WERSJI):
            # Kopia czystego podkładu z drona na nową próbkę
            plotno = np.copy(podklad_drona_bazowy)
            
            # --- LOGIKA DLA DŹWIĘKÓW CIĄGŁYCH (Woda, Pożar, Kolumna) ---
            if konfiguracja["typ"] == "ciagly":
                # Losujemy jedno nagranie z folderu
                dzwiek_celu = random.choice(pula_dzwiekow)
                dzwiek_ciagly = np.copy(dzwiek_celu)
                
                # Zapętlamy dźwięk celu, żeby grał przez całe 30 sekund
                while len(dzwiek_ciagly) < calkowita_dlugosc_probki:
                    dzwiek_ciagly = np.concatenate((dzwiek_ciagly, dzwiek_ciagly))
                dzwiek_ciagly = dzwiek_ciagly[:calkowita_dlugosc_probki]
                
                # TWOJA MODYFIKACJA: Zmieniona głośność
                glosnosc = random.uniform(0.1, 0.7)
                plotno += (dzwiek_ciagly * glosnosc)

            # --- LOGIKA DLA DŹWIĘKÓW PRZERYWANYCH (Krab, Bomba, Karabin) ---
            elif konfiguracja["typ"] == "przerywany":
                liczba_zdarzen = konfiguracja["liczba"]
                rozmiar_segmentu = calkowita_dlugosc_probki // liczba_zdarzen
                
                for j in range(liczba_zdarzen):
                    # Wylosowanie dźwięku (dla każdego strzału może być inny z folderu!)
                    dzwiek_celu = random.choice(pula_dzwiekow)
                    dlugosc_celu = len(dzwiek_celu)
                    
                    # TWOJA MODYFIKACJA: Zmieniona głośność strzału
                    glosnosc_strzalu = random.uniform(0.1, 0.7)
                    zmodyfikowany_dzwiek = dzwiek_celu * glosnosc_strzalu
                    
                    margines_na_koncu = rozmiar_segmentu - dlugosc_celu
                    start_w_segmencie = random.randint(0, margines_na_koncu) if margines_na_koncu > 0 else 0
                        
                    start_calkowity = (j * rozmiar_segmentu) + start_w_segmencie
                    koniec_calkowity = start_calkowity + dlugosc_celu
                    
                    if koniec_calkowity > calkowita_dlugosc_probki:
                        dostepne_miejsce = calkowita_dlugosc_probki - start_calkowity
                        plotno[start_calkowity:calkowita_dlugosc_probki] += zmodyfikowany_dzwiek[:dostepne_miejsce]
                    else:
                        plotno[start_calkowity:koniec_calkowity] += zmodyfikowany_dzwiek

            # --- ZABEZPIECZENIE I ZAPIS ---
            # Jeśli nałożenie drona (*1.5) i strzału (*0.7) przekroczy cyfrowe maksimum głośności (1.0),
            # wyciszamy całość proporcjonalnie, żeby uniknąć trzasków sprzętowych (Clipping)
            max_val = np.max(np.abs(plotno))
            if max_val > 1.0:
                plotno = plotno / max_val 

            nazwa_pliku = f"{nazwa_klasy}_wersja_{i+1}.wav"
            sciezka_wyjsciowa = os.path.join(folder_docelowy, nazwa_pliku)
            sf.write(sciezka_wyjsciowa, plotno, SR)
            print(f"  ✅ Zapisano: {nazwa_pliku}")

# --- URUCHOMIENIE ---
if __name__ == "__main__":
    print("Rozpoczynam pracę na strukturze plików 1_raw_audio -> 2_processed_audio")
    generuj_dataset()
    print("\n🎉 Zakończono generowanie wszystkich klas!")
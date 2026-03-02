import librosa
import librosa.display
import matplotlib.pyplot as plt
import numpy as np
import os
import glob
import warnings

# Ignorujemy ostrzeżenia (np. o braku PySoundFile dla niektórych formatów), żeby konsola była czytelna
warnings.filterwarnings('ignore')

def audio_to_melspectrogram(audio_path, output_path, sr=44100, n_mels=128):
    """
    Konwertuje plik audio (.wav) na obraz Mel-spektrogramu (.png).
    Obraz jest "czysty" (brak osi i ramek) - idealny dla sieci YOLO.
    """
    try:
        y, sr = librosa.load(audio_path, sr=sr)
        
        mel_spect = librosa.feature.melspectrogram(y=y, sr=sr, n_fft=2048, hop_length=512, n_mels=n_mels)
        mel_spect_db = librosa.power_to_db(mel_spect, ref=np.max)
        
        plt.figure(figsize=(10, 4), frameon=False)
        plt.axis('off')
        
        librosa.display.specshow(mel_spect_db, sr=sr, hop_length=512, x_axis='time', y_axis='mel', cmap='magma')
        
        plt.savefig(output_path, bbox_inches='tight', pad_inches=0, transparent=True)
        plt.close() # Zwolnienie pamięci - MEGA ważne przy pętli!
        
    except Exception as e:
        print(f"❌ Błąd podczas przetwarzania pliku {audio_path}: {e}")

def konwertuj_wszystkie_klasy(folder_bazowy_wejscie, folder_bazowy_wyjscie):
    """
    Skanuje główny folder wejściowy, znajduje wszystkie podfoldery (klasy),
    a następnie konwertuje znajdujące się w nich pliki .wav na spektrogramy .png
    z zachowaniem struktury katalogów.
    """
    if not os.path.exists(folder_bazowy_wejscie):
        print(f"⚠️ Błąd: Folder wejściowy '{folder_bazowy_wejscie}' nie istnieje!")
        return

    # Pobranie listy wszystkich podfolderów (np. ['krab', 'bomba', 'woda', ...])
    podfoldery_klas = [f for f in os.listdir(folder_bazowy_wejscie) 
                       if os.path.isdir(os.path.join(folder_bazowy_wejscie, f))]

    if not podfoldery_klas:
        print(f"⚠️ Nie znaleziono żadnych podfolderów w '{folder_bazowy_wejscie}'.")
        return

    print(f"Znaleziono {len(podfoldery_klas)} klas do przetworzenia: {podfoldery_klas}")

    # Pętla przez każdą klasę (folder)
    for klasa in podfoldery_klas:
        sciezka_wejsciowa_klasy = os.path.join(folder_bazowy_wejscie, klasa)
        sciezka_wyjsciowa_klasy = os.path.join(folder_bazowy_wyjscie, klasa)
        
        # Tworzymy folder docelowy dla danej klasy (np. 3_spectrograms/krab)
        os.makedirs(sciezka_wyjsciowa_klasy, exist_ok=True)
        
        sciezki_wav = glob.glob(os.path.join(sciezka_wejsciowa_klasy, "*.wav"))
        liczba_plikow = len(sciezki_wav)
        
        if liczba_plikow == 0:
            print(f"⚠️ Pomijam klasę '{klasa}': Brak plików .wav")
            continue
            
        print(f"\n⚙️ Konwertowanie klasy '{klasa}' ({liczba_plikow} plików)...")
        
        # Pętla przetwarzająca pliki wewnątrz danej klasy
        for index, sciezka_audio in enumerate(sciezki_wav, start=1):
            nazwa_pliku = os.path.basename(sciezka_audio)
            nazwa_png = os.path.splitext(nazwa_pliku)[0] + ".png"
            sciezka_wyjsciowa = os.path.join(sciezka_wyjsciowa_klasy, nazwa_png)
            
            audio_to_melspectrogram(sciezka_audio, sciezka_wyjsciowa)
            print(f"  [{index}/{liczba_plikow}] ✅ Zapisano: {nazwa_png}")

# --- Konfiguracja ścieżek i uruchomienie ---
if __name__ == "__main__":
    # Teraz podajemy główne foldery z naszej nowej struktury!
    FOLDER_ZRODLOWY = "2_processed_audio" 
    FOLDER_DOCELOWY = "3_spectrograms"
    
    print("Rozpoczynam generowanie spektrogramów...")
    konwertuj_wszystkie_klasy(FOLDER_ZRODLOWY, FOLDER_DOCELOWY)
    print("\n🎉 Zakończono! Dataset obrazkowy jest gotowy do etykietowania.")
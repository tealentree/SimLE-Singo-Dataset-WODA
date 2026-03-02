import subprocess
import sys
import os
import time

def uruchom_skrypt(nazwa_skryptu):
    """
    Uruchamia podany skrypt Pythona jako osobny proces i przechwytuje jego działanie.
    """
    print(f"\n{'='*55}")
    print(f"🚀 ROZPOCZYNAM ETAP: {nazwa_skryptu}")
    print(f"{'='*55}\n")
    
    try:
        # sys.executable to bezpieczny sposób na wywołanie dokładnie tego samego Pythona, 
        # którego używasz obecnie (ważne, jeśli masz np. wirtualne środowisko venv)
        sciezka_do_skryptu = os.path.join("scripts", nazwa_skryptu)
        
        subprocess.run([sys.executable, sciezka_do_skryptu], check=True)
        
        print(f"\n✅ ETAP ZAKOŃCZONY SUKCESEM: {nazwa_skryptu}")
        
    except subprocess.CalledProcessError as e:
        # Jeśli skrypt wewnątrz rzuci błędem, pipeline zostanie bezpiecznie zatrzymany
        print(f"\n❌ BŁĄD KRYTYCZNY: Skrypt '{nazwa_skryptu}' uległ awarii (kod błędu: {e.returncode}).")
        print("Zatrzymuję pipeline, aby nie generować błędnych danych.")
        sys.exit(1)
        
    except FileNotFoundError:
        print(f"\n❌ NIE ZNALEZIONO SKRYPTU: '{sciezka_do_skryptu}'.")
        print("⚠️ Pamiętaj, aby uruchamiać run_pipeline.py z GŁÓWNEGO folderu projektu!")
        sys.exit(1)

if __name__ == "__main__":
    print("🤖 Uruchamiam zautomatyzowany Pipeline Generowania Datasetu...")
    czas_start = time.time()
    
    # Lista skryptów do wykonania w sztywnej kolejności
    kolejnosc_wykonywania = [
        "1_generate_audio.py",
        "2_generate_spectograms.py"
    ]
    
    # Wykonujemy skrypty pętla po pętli
    for skrypt in kolejnosc_wykonywania:
        uruchom_skrypt(skrypt)
        # Krótka pauza dla stabilności systemu plików
        time.sleep(1) 
        
    czas_stop = time.time()
    czas_trwania = round(czas_stop - czas_start, 2)
    
    print(f"\n{'='*55}")
    print(f"🎉 PIPELINE ZAKOŃCZONY W 100% SUKCESEM!")
    print(f"⏱️ Całkowity czas generowania: {czas_trwania} sekund.")
    print(f"{'='*55}")
    print("Twój pełny dataset znajduje się w folderze '3_spectrograms'.")
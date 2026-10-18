Press Fish

Apraksts:
    Press Fish spēle, kurā tu spēlē zivs lomā, lecot cauri caurulēm. Ir tikai trīs cauruļu līmeņi. Pēc katra līmeņa pabeigšanas caurules sāks sašaurināties, un beigās notiks boss cīņa ar haizivi, kas izšauj spēcīgu ūdens straumi. Pareizi trāpot boss centrā, tiks piešķirti vairāk punktu.


Izmantotās tehnoloģijas:
    Python 3.12 (pārbaudīta versija)
    Pygame
    pygame-widgets
    FastAPI (servera daļai)
    Uvicorn
    Pārējās atkarības ir norādītas failā requirements.txt.
    
    

Instalēšana un palaišana:
Windows:
    1. Klonē repozitoriju vai lejupielādē projekta failus.
    2. Atver termināli projekta saknes mapē.
    3. Ja mape .venv jau tika izveidota ar citu Python versiju, izdzēs veco vidi:
            Remove-Item -Recurse -Force .venv
       Izveido virtuālo vidi ar Python 3.12:
        py -3.12 -m venv .venv

    4. Ja PowerShell bloķē aktivizācijas skriptu, atļauj tā palaišanu tikai pašreizējā terminālī:
        Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
    5. Aktivizē virtuālo vidi:
        .\.venv\Scripts\Activate.ps1
    6. Instalē atkarības:
        python -m pip install -r requirements.txt
    7. Palaid serveri:
        python -m uvicorn api.main:app --reload
    8. Atver otru PowerShell termināli projekta saknes mapē. Ja nepieciešams, izpildi iepriekšējo politikas komandu, aktivizē jau izveidoto vidi un palaid spēli:
        .\.venv\Scripts\Activate.ps1
        python -m client.main

Linux(Ubuntu, Mint):
    1. Klonē repozitoriju vai lejupielādē projekta failus.
    2. Atver termināli projekta saknes mapē.
    3. Izveido virtuālo vidi:
        python3.12 -m venv .venv

    4. Aktivizē virtuālo vidi.
            source .venv/bin/activate
    5. Instalē atkarības:
            pip install -r requirements.txt
    6. Palaid serveri:
        .venv/bin/python -m uvicorn api.main:app --reload
    7. Atver otru termināli un palaid spēles galveno Python failu, izmantojot projekta virtuālo vidi.
       source .venv/bin/activate
        .venv/bin/python -m client.main




Spēles vadība:
    Space — likt zivtiņai lēkt un sākt spēli.

    Esc — apturēt spēli vai turpināt to pēc pauzes.

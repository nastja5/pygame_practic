Press Fish

Apraksts:
    Press Fish spēle, kurā tu spēlē zivs lomā, lecot cauri caurulēm. Ir tikai trīs cauruļu līmeņi. Pēc katra līmeņa pabeigšanas caurules sāks sašaurināties, un beigās notiks boss cīņa ar haizivi, kas izšauj spēcīgu ūdens straumi. Pareizi trāpot boss centrā, tiks piešķirti vairāk punktu.


Izmantotās tehnoloģijas:
    Python 3.11 vai jaunāks
    Pygame
    pygame-widgets
    FastAPI (servera daļai)
    Uvicorn
    Pārējās atkarības ir norādītas failā requirements.txt.
    
    

Instalēšana un palaišana
    1. Klonē repozitoriju vai lejupielādē projekta failus.
    2. Atver termināli projekta saknes mapē.
    3. Izveido virtuālo vidi:
        python3 -m venv .venv

    4. Aktivizē virtuālo vidi.
        Linux:
            source .venv/bin/activate
    5. Instalē atkarības:
            pip install -r requirements.txt
    6. Palaid serveri:
        .venv/bin/python -m uvicorn api.main:app --reload
    7. Atver otru termināli un palaid spēles galveno Python failu, izmantojot projekta virtuālo vidi.
        .venv/bin/python -m client.main



Spēles vadība:
    Space — likt zivtiņai lēkt un sākt spēli.

    Esc — apturēt spēli vai turpināt to pēc pauzes.

## 📋 Wymagania Funkcjonalne

* **Mechanika Poruszania się (Rdzeń Gry):**
    * Płynny ruch postaci w poziomie z uwzględnieniem minimalnej bezwładności.
    * Skok o zmiennej wysokości (zależny od czasu przytrzymania klawisza skoku).
    * Mechanika odbijania się od określonych wrogów lub przeszkód.
* **System Pułapek (Troll Mechaniki):**
    * **Niewidzialne bloki:** Obiekty z kolizją pojawiające się dopiero w momencie uderzenia przez gracza (najlepiej umieszczane nad przepaściami, aby zablokować skok).
    * **Fałszywe obiekty:** Elementy tła, które posiadają zabójcze hitboxy, oraz wizualne "kolce/przepaście", które w rzeczywistości są bezpieczne.
    * **Wyzwalacze (Triggers):** Niewidzialne strefy, których przekroczenie przez gracza aktywuje ruchome pułapki (np. spadający sufit, lecące pociski).
    * **Złośliwe interakcje:** Przedmioty takie jak monety, checkpointy lub power-upy, które celowo uciekają przed graczem lub powodują natychmiastową śmierć.
* **Zarządzanie Stanem Gry:**
    * Globalny oraz lokalny (per poziom) licznik śmierci (Death Counter).
    * System szybkiego resetu (tzw. "Quick Death") – po śmierci gracz musi natychmiast wracać do punktu startowego/checkpointu bez żadnych ekranów ładowania.

---

## ⚙️ Wymagania Niefunkcjonalne

* **Wydajność:** Gra musi działać w stabilnych 60 klatkach na sekundę (FPS). Spadki wydajności i "ścinanie" w grach wymagających precyzji są niedopuszczalne.
* **Precyzja i Responsywność:**
    * Hitboxy (pola kolizji) muszą być niezwykle precyzyjne i oparte na prostokątach (AABB). Hitbox postaci gracza powinien być minimalnie mniejszy niż jej grafika, aby zapewnić graczowi margines błędu i poczucie, że gra jest "sprawiedliwie trudna".
    * Opóźnienie (input lag) między wciśnięciem klawisza a akcją na ekranie musi być zerowe.
* **Zarządzanie Poziomami:** Mapy nie mogą być zapisane na sztywno (hardkodowane) w kodzie Pythona. Gra powinna dynamicznie wczytywać poziomy z zewnętrznych plików z danymi (np. format `.json` lub `.tmx`).
\# Let\_s\_play



Projekt gry platformowej 2D stworzonej w języku Python z wykorzystaniem biblioteki Pygame. Gra inspirowana jest tytułami typu "troll platformer", w których gracz musi nie tylko wykazać się zręcznością, ale również przewidywać pułapki i nieoczywiste zachowania poziomów.



\---



\# Uruchomienie projektu



\## Wymagania



\- Python 3.13 lub nowszy

\- Biblioteki z pliku `requirements.txt`



\## Instalacja zależności



```bash

pip install -r requirements.txt

```



\## Uruchomienie gry



```bash

python main.py

```



\---



\# Sterowanie



| Klawisz | Akcja |

|----------|----------|

| ← → | Ruch postaci |

| Spacja | Skok |



\---



\# Wykorzystane technologie



\## Python



Główny język programowania projektu.



\## Pygame CE



Biblioteka odpowiedzialna za:



\- renderowanie grafiki

\- obsługę dźwięku

\- obsługę wejścia użytkownika

\- zarządzanie oknem gry

\- wykrywanie kolizji



\## PyTMX



Biblioteka umożliwiająca odczyt map zapisanych w formacie `.tmx` z programu Tiled Map Editor.



\## PyScroll



Biblioteka wspierająca wyświetlanie dużych map oraz obsługę kamery podążającej za graczem.



\## Tiled Map Editor



Narzędzie wykorzystywane do tworzenia poziomów gry.



\---



\# Struktura projektu



```text

Let\_s\_play/

│

├── assets/

│   ├── Sounds/

│   └── screens/

│

├── maps/

│   ├── LevelOne.tmx

│   ├── LevelTwo.tmx

│   └── LevelThree.tmx

│

├── main.py

├── levelOne.py

├── levelTwo.py

├── levelThree.py

├── tiled\_parser.py

├── test\_tiled\_parser.py

└── requirements.txt

```



\---



\# Zaimplementowane funkcjonalności



\## System poruszania się



Gracz może:



\- poruszać się w lewo i prawo,

\- wykonywać skoki,

\- poruszać się po platformach,

\- wchodzić w interakcję z elementami poziomu.



Mechanika została zaimplementowana z wykorzystaniem systemu kolizji opartych na prostokątach (AABB).



\---



\## System poziomów



Gra zawiera kilka poziomów:



\- Level One

\- Level Two

\- Level Three



Każdy poziom posiada własną konfigurację mapy oraz rozmieszczenie przeszkód.



\---



\## System punktacji



W trakcie rozgrywki gracz zdobywa punkty widoczne w prawym górnym rogu ekranu.



Przykład:



```text

SCORE: 0

```



\---



\## System przeciwników i przeszkód



W grze występują:



\- przeciwnicy,

\- kolce,

\- ruchome elementy poziomu,

\- obiekty powodujące śmierć postaci.



\---



\## Efekty dźwiękowe



Zaimplementowano obsługę:



\- skoku,

\- trafienia,

\- śmierci,

\- śmierci przeciwnika,

\- muzyki w tle.



Pliki dźwiękowe znajdują się w katalogu:



```text

assets/Sounds

```



\---



\## Obsługa map z Tiled Map Editor



Poziomy gry nie są zapisane bezpośrednio w kodzie programu.



Mapy tworzone są w programie Tiled Map Editor i przechowywane jako pliki `.tmx`.



Przykład:



```text

maps/LevelOne.tmx

```



Do obsługi map wykorzystano bibliotekę PyTMX oraz własny parser:



```text

tiled\_parser.py

```



Parser umożliwia odczyt podstawowych informacji o mapie:



\- szerokość mapy,

\- wysokość mapy,

\- rozmiar kafelków,

\- nazwy warstw.



Przykładowy wynik działania parsera:



```python

{

&#x20;   'width': 200,

&#x20;   'height': 20,

&#x20;   'tile\_width': 16,

&#x20;   'tile\_height': 16,

&#x20;   'layers': \[

&#x20;       'tło\_główne',

&#x20;       'dekoracje',

&#x20;       'ruch',

&#x20;       'pułapki',

&#x20;       'ruchome'

&#x20;   ]

}

```



\---



\# Wymagania funkcjonalne



\## Mechanika poruszania się



\- ruch postaci w poziomie,

\- skoki,

\- interakcja z otoczeniem,

\- system kolizji.



\## System pułapek



Projekt przewiduje wykorzystanie:



\- niewidzialnych bloków,

\- fałszywych obiektów,

\- wyzwalaczy aktywujących pułapki,

\- złośliwych interakcji z przedmiotami.



\## Zarządzanie stanem gry



\- licznik punktów,

\- obsługa śmierci gracza,

\- szybki restart poziomu.



\---



\# Wymagania niefunkcjonalne



\## Wydajność



Gra powinna działać płynnie przy 60 FPS.



\## Responsywność



\- natychmiastowa reakcja na wejście użytkownika,

\- precyzyjne kolizje.



\## Zarządzanie poziomami



Poziomy powinny być ładowane dynamicznie z plików TMX tworzonych w Tiled Map Editor.



\---



\# Zrzuty ekranu



\## Start gry



!\[Start gry](assets/screens/screen1.png)



\## Rozgrywka



!\[Rozgrywka](assets/screens/screen2.png)



\## Platformy i przeszkody



!\[Platformy](assets/screens/screen3.png)



\## Kolejny poziom



!\[Poziom](assets/screens/screen4.png)



\## Walka i zdobywanie punktów



!\[Punkty](assets/screens/screen5.png)



\# Film prezentujący grę



Plik znajduje się w repozytorium:



\[▶ Obejrzyj film](assets/video/gameplay.mp4)

\---



\# Autorzy



Projekt realizowany w ramach zajęć i rozwijany zespołowo.

Michał Potocki, Stanisław Mikołajek, Dominik Pyzowski



\---



\# Możliwe kierunki rozwoju



\- rozbudowany system przeciwników,

\- system checkpointów,

\- licznik śmierci,

\- animacje postaci,

\- nowe pułapki,

\- bossowie,

\- dodatkowe poziomy,

\- pełna integracja map z Tiled Map Editor.


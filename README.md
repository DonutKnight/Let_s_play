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
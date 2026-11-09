# Mit mondjak el — rövid szöveg a bemutatóhoz (~3 perc)

## Az adat (a táblázatnál)

Az amerikai környezetvédelmi hivatal hivatalos fogyasztási adatbázisát választottam. Ebben **50 ezer autóváltozat**
van 1984-től 2027-ig, és mindegyiket laborban, ugyanazzal a teszttel mérték. A célváltozóm az **éves üzemanyagköltség
dollárban**. Azért ezt választottam, mert minden autóra ugyanabban az egységben van, a benzinestől az elektromosig.
Mindhárom feltétel teljesül: elég nagy, érdekel, és a változók jól magyarázzák a célt.

## 1. ábra — az elektromos hullám

Ez az ábra azt mutatja, milyen arányban kínáltak évente benzines, dízel, hibrid és elektromos modelleket. **2010-ig
szinte minden autó benzines volt.** Utána megjelennek a hibridek és az elektromos autók, és **2025-ben már a modellek
negyede elektromos**. Ezért izgalmas az adat: egy egész iparág átalakulását látjuk benne.

## 2. ábra — mennyibe kerül egy év autózás

Ez a célváltozó, fajtánként. A pötty a középső autó, a vastag sáv az autók középső fele. **Egy elektromos autóval
évente kb. 800 dollár autózni, egy benzinessel 3450**, tehát kb. négyszer annyi. A dízel azért tűnik a
legdrágábbnak, mert Amerikában a dízelek főleg nagy pickupok. Ezért a modellben az autó kategóriáját is figyelembe
kell majd venni.

## 3. ábra — nagyobb motor, nagyobb számla

Itt csak a benzines autók vannak. Vízszintesen a motor mérete, függőlegesen az éves költség. A sötétebb hatszögekben
van több autó, a narancs vonal a tipikus költség motorméretenként. **Minél nagyobb a motor, annál drágább: egy 1 literes
motorral kb. 1800 dollár egy év, egy 7 literessel kb. 7000.** A vízszintes csíkok azért vannak, mert a hivatal kerekítve
adja meg a fogyasztást.

## 4. ábra — magyarázzák-e a változók a célt?

Gyorsan lefuttattam két modellt, hogy lássam, van-e értelme az adatnak. **Csak az évjárattal és az üzemanyag
fajtájával a költség 23%-át lehet megmagyarázni. Az összes változóval (motor, váltó, hajtás, kategória) már 93%-át.**
A mérésnél figyeltem arra, hogy ugyanaz az autómodell ne legyen a tanító és a teszt adatban is, különben túl szép lenne
az eredmény.

## Zárás (a "To watch out for" résznél)

Amire figyelni kell: sok a majdnem-duplikátum, ugyanannak a modellnek több változata, ezért autómodell szerint kell
majd szétvágni az adatot. Az elektromos autóknak nincs motormérete, ezért nekik külön jelölés kell. A költséget pedig
mai árakon számolják, így az autók technológiáját hasonlítja össze, nem azt, amit a tulajdonosok annak idején fizettek.

**A tervem:** regressziós modell az éves költségre, és megnézni, hogy a régebbi autókon tanított modell mennyire tudja
megjósolni a legújabb, egyre inkább elektromos modellek költségét.

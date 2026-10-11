# Házi feladat – Hiperparaméter-vadászat a Titanic-adatsoron

## Mit jelent ez a feladat?

A modell egy példából próbálja megtanulni, hogy az utas túlélte-e a
Titanic-katasztrófát. A **hiperparaméter** olyan, még a tanítás előtt
beállított érték, amely meghatározza, hogyan tanuljon a modell: például hány
fát építsen, milyen mélyek legyenek a fák, vagy hány szomszédot vegyen
figyelembe a KNN. A **tanuló pontosság** azt mutatja, mennyire jól jósol a
modell azokon az utasokon, amelyeken tanult; a **teszt pontosság** pedig azt,
mennyire jól teljesít korábban nem látott utasokon. Ha a tanuló pontosság
jóval magasabb a tesztpontosságnál, a modell valószínűleg **túlilleszkedett**
(overfitting): megjegyezte a tanulóadatok részleteit, ezért új adatokon
rosszabbul teljesít. A cél tehát nem pusztán a magas tanuló pontosság, hanem a
jó tesztpontosság és a kettő közötti kicsi különbség.

## Módszer

Az órai `demo.ipynb` előkészítését és felosztását használtam: a hiányzó
életkorokat mediánnal, a hiányzó beszállási kikötőt a leggyakoribb értékkel
pótoltam, a kategóriákat kódoltam, majd az adatokat 75% tanuló- és 25%
tesztrészre bontottam (`random_state=7`, rétegzett felosztás). Ugyanazt a
felosztást használtam minden modellnél. Három Random Forest- és három
Gradient Boosting-beállítást vizsgáltam; bónuszként három KNN-beállítást is.
A KNN távolságokkal dolgozik, ezért a jellemzőket standardizáltam. A táblázat
minden értéke pontosság; például a 0,843 azt jelenti, hogy a tesztadat
84,3%-át találta el a modell.

## Eredmények

### Órai modellek viszonyítási alapja

| Modell | Tesztpontosság |
|---|---:|
| Logisztikus regresszió | 77,1% |
| SVM | 82,5% |
| Döntési fa | 82,1% |
| Random Forest | 82,1% |
| Gradient Boosting | **84,3%** |
| Neurális háló | 79,8% |

### Hiperparaméter-kísérletek

| Modell | Beállítás | Tanuló pontosság | Teszt pontosság | Különbség |
|---|---|---:|---:|---:|
| Random Forest | 50 fa, max. mélység 3, levél minimuma 4 | 83,1% | 80,7% | 2,4 százalékpont |
| Random Forest | 200 fa, max. mélység 6 | 86,5% | 82,1% | 4,5 százalékpont |
| Random Forest | 500 fa, korlátozás nélküli mélység | 98,7% | 79,8% | 18,8 százalékpont |
| Gradient Boosting | 100 fa, tanulási ráta 0,05, mélység 2 | 84,9% | 82,1% | 2,8 százalékpont |
| Gradient Boosting | sklearn alapbeállítás | 90,9% | **84,3%** | 6,6 százalékpont |
| Gradient Boosting | 300 fa, tanulási ráta 0,2, mélység 4 | 98,7% | 81,2% | 17,5 százalékpont |
| KNN (bónusz) | 3 szomszéd, egyenlő súly | 88,6% | 75,8% | 12,8 százalékpont |
| KNN (bónusz) | 7 szomszéd, egyenlő súly | 85,8% | 79,4% | 6,4 százalékpont |
| KNN (bónusz) | 15 szomszéd, távolságalapú súly | 98,7% | 78,0% | 20,6 százalékpont |

## Értékelés

A vizsgált beállítások közül a Gradient Boosting alapbeállítása lett a legjobb, 84,3%-os tesztpontossággal, de ez az órai eredményt nem múlta felül.  
Ennél a modellnél a tanuló pontosság 90,9%, vagyis 6,6 százalékponttal magasabb a tesztpontosságnál, ami valamennyi túlillesztést jelez, de kisebb rést mutat, mint az agresszív beállítások.  
Egyértelmű túlillesztést láttam a korlátozás nélküli Random Forestnél (98,7% tanuló, 79,8% teszt) és az agresszív Gradient Boostingnál (98,7% tanuló, 81,2% teszt).  
A KNN 15 szomszéddal szintén nagy rést mutatott (98,7% és 78,0%), míg 7 szomszéddal kiegyensúlyozottabb, de gyengébb eredményt adott (85,8% és 79,4%).  
A KNN érzékeny a skálázásra, ezért standardizáltam az adatokat; a dimenzió-átka azt jelenti, hogy sok jellemző esetén a pontok közötti távolságok kevésbé informatívvá válhatnak, bár ennél a nyolc jellemzőnél ez kevésbé erős, mint több száz dimenziónál.

## Futtatás

A mérési eredményeket előállító program: [homework_titanic_hyperparameter_hunt.py](./homework_titanic_hyperparameter_hunt.py).
Futtatás a projekt gyökeréből:

```bash
python -m pip install -r requirements_titanic_homework.txt
python homework_titanic_hyperparameter_hunt.py
```

Az elemzéshez használt órai adatkészlet a [data/titanic.csv](./data/titanic.csv)
fájlban található.

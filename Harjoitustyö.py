import calendar
import datetime
import json

kalenteri = {}

tanaan = datetime.datetime.now()
c = calendar.TextCalendar(calendar.MONDAY)
k = c.formatmonth(tanaan.year,tanaan.month, 0, 0)
print(k)

def nayta_UI():
    
        while True:
            print("Valitse toiminto:")
            print("1. Lisää muistutus")
            print("2. Hae muistutus")
            print("3. Näytä kuukausi")
            print("4. Näytä kaikki muistutukset")
            print("5. Näytä koko vuoden kalenteri")
            print("6. Poista muistutus")
            print("0. Sulje kalenteri")
            valinta = int(input("Valintasi: "))
            if valinta > 6:
                print("Pitää antaa luku väliltä 0-5")
                print("")
                print (k)

            elif valinta == 1:
                lisaa_muistutus()
                print("")
                print("Muistutus lisätty")
                print("")
                print(k)
            
            elif valinta == 2:
                print("")
                hae_muistutus()
                print("")
                print(k)

            elif valinta == 3:
                nayta_kuukausi()

            elif valinta == 4:
                print("")
                print("Kaikki Muistutukset: ")
                nayta_kaikki_muistutukset()
                print(k)

            elif valinta == 5:
                nayta_koko_vuosi()

            elif valinta == 6:
                poista_muistutus()

            elif valinta == 0:  
                  
                break

def lisaa_muistutus():
    vuosi = int(input("Anna vuosi: "))
    kuukausi = int(input("Anna kuukauden numero: "))
    paiva = int(input("Anna päivämäärä: "))
    muistutus = input("Anna muistutus: ")
    pvm = datetime.date(vuosi, kuukausi, paiva)
    list=[]
    if kalenteri.get(str(pvm)) != None:
        data = kalenteri.get(str(pvm))
        list.append(data)
        list.append(muistutus)
        kalenteri[str(pvm)] = list
    else:
        list.append(muistutus)
    kalenteri[str(pvm)] = list


def hae_muistutus():
    muistutus = (input("Anna muistutuksen nimi: "))
    with open("kalenteri.json","r") as t:
        data = json.load(t)
        for rivi in data.values():
            if muistutus in rivi:
                print(data)
            else: 
                print("Ei tuloksia.")

def nayta_kuukausi():
    kknro = int(input("Anna Kuukausi numero: "))
    kk = c.formatmonth(2022, kknro, 0, 0)
    print(kk)

def nayta_kaikki_muistutukset():
    print(kalenteri)
    print("")
            
def nayta_koko_vuosi():
    vuosi = int(input("Anna vuosi: "))
    for i in range(1,13):
        print(c.formatmonth(vuosi,i,0,0))

def poista_muistutus():
    muistutus = (input('Anna muistutuksen nimi: '))
    for pvm, muist in kalenteri.items():
        if muist == muistutus:
            del kalenteri[str(pvm)]

    
try:
    with open('kalenteri.json', 'r') as json_file:
        data = json.load(json_file)
    
except FileNotFoundError:
    print("File not found.")
except json.JSONDecodeError:
    pass

nayta_kaikki_muistutukset()
nayta_UI()
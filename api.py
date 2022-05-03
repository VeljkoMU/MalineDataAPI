import datetime
from flask import Flask, jsonify, make_response, request
from flask_cors import CORS
import pymysql as MySQLdb
import numpy as np


#KORISNICI
qAllUsers='SELECT * FROM  RADNIK'
qAddUser='INSERT INTO RADNIK(IME, GAJBE, MESTO, JMBG, ZIRO_RACUN_BANKA, BROJ_GAZ) VALUES (%s,%s,%s,%s, %s, %s)'
qUpdateUser='UPDATE RADNIK SET GAJBE=GAJBE+%s WHERE ID_RADNIK=%s'
qDeleteUser='DELETE FROM RADNIK WHERE ID_RADNIK = %s'
qUser='SELECT * FROM RADNIK WHERE IME = %s'

#STAVKE
qAddEntry="""INSERT INTO STAVKA (DATUM , RADNIK_ID   ,CENA_ORGANSKIH  , CENA_KONTROLISANIH  , 
    CENA_KOMERCIJALNIH   ,CRVENE_GAJBE_IN , ZELENE_GAJBE_IN  , PLAVE_GAJBE_IN,PLAVE_GAJBE_OUT     ,CRVENE_GAJBE_OUT, ZELENE_GAJBE_OUT ,ORGANSKE , KOMERCIJALNE, KONTROLISANE , ISPLACENO )
    VALUES
    (%s,%s, %s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"""
qDeleteEntry='DELETE FROM STAVKA WHERE ID_STAVKA = %s'
qUpdateEntry="""UPDATE STAVKA 
SET 
 DATUM = %s,
 ORGANSKE = %s ,
 KONTROLISANE = %s ,
 KOMERCIJALNE = %s,
 ZELENE_GAJBE_IN = %s  ,
 ZELENE_GAJBE_OUT   = %s,
 PLAVE_GAJBE_IN = %s,
 PLAVE_GAJBE_OUT  = %s,
 CRVENE_GAJBE_IN = %s,
 CRVENE_GAJBE_OUT = %s,
 CENA_ORGANSKIH  =  %s,
 CENA_KONTROLISANIH = %s,
 CENA_KOMERCIJALNIH =  %s,
 ISPLACENO = %s ,
 RADNIK_ID = %s
 where ID_STAVKA = %s """
qUserEntry='SELECT * FROM STAVKA WHERE RADNIK_ID = %s ORDER BY DATUM DESC'
qSorteddataEntry="""SELECT DATUM , SUM(ORGANSKE) AS ORGANSKE_KG, SUM(KOMERCIJALNE) AS KOMERCIJALNE_KG,
SUM(KONTROLISANE ) AS KONTROLISANE_KG, CENA_ORGANSKIH, CENA_KONTROLISANIH, CENA_KOMERCIJALNIH
FROM STAVKA 
GROUP BY DATUM 
ORDER BY DATUM DESC"""
qSumEntry='SELECT SUM(KOMERCIJALNE) , SUM(KONTROLISANE), SUM(ORGANSKE) FROM STAVKA'


#####OVDE SI STAO MAJMUNE############################################################################

#IZVOZ
qSorteddataExport="""SELECT DATUM , CENA_ORGANSKIH , CENA_KONTROLISANIH, CENA_KOMERCIJALNIH,
SUM(KOMERCIJALNE) AS KOMERCIJALNE_KG , SUM(ORGANSKE) AS ORGANSKE_KG , 
SUM(KONTROLISANE) AS KONTROLISANE_KG, 
FROM IZVOZ 
GROUP BY DATUM 
ORDER BY DATUM DESC """
qAddExport='INSERT INTO IZVOZ (DATUM , KOMERCIJALNE , ORGANSKE , KONTROLISANE , CENA_ORGANSKIH ,  CENA_KONTROLISANIH ,CENA_KOMERCIJALNIH, GP, GT, GC ) VALUES (%s,%s,%s,%s,%s,%s,%s, %s, %s, %s)'
qAllExport="""SELECT DATUM , CENA_ORGANSKIH , CENA_KONTROLISANIH, CENA_KOMERCIJALNIH,KOMERCIJALNE AS KOMERCIJALNE_KG , ORGANSKE AS ORGANSKE_KG , KONTROLISANE AS KONTROLISANE_KG, ID_IZVOZA, GP, GT, GC FROM IZVOZ"""
qDeleteExport='DELETE FROM IZVOZ WHERE ID_IZVOZA = %s'
qSumExport='SELECT SUM(KOMERCIJALNE) , SUM(KONTROLISANE), SUM(ORGANSKE) FROM IZVOZ'

#GAJBE
qUpdateCrate="""UPDATE GAJBE  
SET 
ZELENE_DOSTUPNE = %s,PLAVE_DOSTUPNE = %s,CRVENE_DOSTUPNE = %s,ZELENE_IZNAJMLJENE = %s,PLAVE_IZNAJMLJENE = %s,CRVENE_IZNAJMLJENE = %s
where id_gajbe >=0"""
qAllCrate='SELECT ZELENE_DOSTUPNE, ZELENE_IZNAJMLJENE, CRVENE_DOSTUPNE, CRVENE_IZNAJMLJENE, PLAVE_DOSTUPNE, PLAVE_IZNAJMLJENE FROM GAJBE'





app = Flask(__name__)
config = {
  'user': 'root',
  'password': 'root',
  'host': 'localhost',
  'database': 'malinedb'
}

def exeQuery(query, params):
    cnx = MySQLdb.connect(host='localhost', user='root', password='root', database='malinedb')
    cursor=cnx.cursor()
    cursor.execute(query, params)

    if 'INSERT' in query or 'UPDATE' in query or 'DELETE' in query:
        cnx.commit()
        cnx.close()
        return None
    else:
        data=cursor.fetchall()
        print(data)
        cnx.close()
        return data


# RADI NE DIRAJ!!!!!!
@app.route('/addUser', methods=["POST"])
def addUser():
    data=request.get_json()
    name=data['name']
    cretes=data['cretes']
    place=data['place']
    jmbg=data['jmbg']
    account=data['account']
    farm_num=data['farm_num']

    exeQuery(qAddUser,[name, cretes, place, jmbg, account, farm_num])
    return "Zeljko ovo nista ne valja"
 
# RADI NE DIRAJ!!!!!!
@app.route('/allUsers')
def allUsers():
    data=exeQuery(qAllUsers, [])
    print(data)
    return jsonify(data)


# @app.route('/qUser')
# def qUser():
#     name=request.args.get('name')
#     data=exeQuery(qUser,[name])
#     return jsonify(data)

# RADI NE DIRAJ!!!!!!
@app.route('/deleteUser', methods=["DELETE"])
def deleteUser():
    id=request.args.get('id_user')
    exeQuery(qDeleteUser,[id])
    return ""

#DATUM , ORGANSKE, KONTROLISANE , KOMERCIJALNE , ZELENE_GAJBE_IN ,  ZELENE_GAJBE_OUT   , PLAVE_GAJBE_IN  
# ,PLAVE_GAJBE_OUT  ,CRVENE_GAJBE_IN ,CRVENE_GAJBE_OUT  ,CENA_ORGANSKIH  , CENA_KONTROLISANIH  , 
#  CENA_KOMERCIJALNIH  ,  ISPLACENO , RADNIK_ID 

#KAD SE DODA NOV ENTRY, MORA DA SE MENJA STANJE GAJBI U TABLI GAJBE, I STANJE GAJBI U KORISNIKU

# RADI NE DIRAJ!!!!!!
@app.route('/addEntry', methods=["POST"])
def addEntry():
    data=request.get_json()

    arr=[]
    for key in data:
        arr.append(data[key])
    exeQuery(qAddEntry,arr)
    ajbeInC= data["gajbeInC"]
    ajbeInZ= data["gajbeInZ"]
    ajbeInP= data["gajbeInP"]
    ajbeOutP= data["gajbeOutP"]
    ajbeOutZ= data["gajbeOutZ"]
    ajbeOutC= data["gajbeOutC"]
    
    cretes = exeQuery(qAllCrate, [])
    cretes1 = [0,0,0,0,0,0]
    cretes1[0] = cretes[0][0] + ajbeInZ - ajbeOutZ
    cretes1[1] = cretes[0][4] +ajbeInP - ajbeOutP
    cretes1[2] = cretes[0][2] +ajbeInC - ajbeOutC
    cretes1[3] = cretes[0][1] + ajbeOutZ - ajbeInZ
    cretes1[4] = cretes[0][5] +ajbeOutP - ajbeInP
    cretes1[5] = cretes[0][3] +ajbeOutC - ajbeInC

    exeQuery(qUpdateCrate, cretes1)

    inn=ajbeInC+ajbeInP+ajbeInZ
    outt=ajbeOutC+ajbeOutP+ajbeOutZ
    sub=outt - inn
    exeQuery(qUpdateUser,[sub, data["korisnik"]])

    return ""
    

@app.route('/deleteEntry', methods = ["DELETE"])
def deleteEntry():
    id=request.args.get('id_entry')
    exeQuery(qDeleteEntry,[id])
    return ""

@app.route('/updateEntry')
def updateEntry():
    id=request.args.get('id_entry')
    data=request.get_json()
    arr=[]
    for key in data:
        arr.append(data[key])
    arr.append(id)
    exeQuery(qAddEntry,arr)

    ajbeInC= data["gajbeInC"]
    ajbeInZ= data["gajbeInZ"]
    ajbeInP= data["gajbeInP"]
    ajbeOutP= data["gajbeOutP"]
    ajbeOutZ= data["gajbeOutZ"]
    ajbeOutC= data["gajbeOutC"]

    cretes = exeQuery(qAllCrate, [])
    cretes1 = [0,0,0,0,0,0]
    cretes1[0] = cretes[0][0] + ajbeInZ - ajbeOutZ
    cretes1[4] = cretes[0][4] +ajbeInP - ajbeOutP
    cretes1[2] = cretes[0][2] +ajbeInC - ajbeOutC
    cretes1[1] = cretes[0][1] + ajbeOutZ - ajbeInZ
    cretes1[5] = cretes[0][5] +ajbeOutP - ajbeInP
    cretes1[3] = cretes[0][3] +ajbeOutC - ajbeInC

    exeQuery(qUpdateCrate, cretes1)

    inn=ajbeInC+ajbeInP+ajbeInZ
    outt=ajbeOutC+ajbeOutP+ajbeOutZ
    sub=inn-outt
    exeQuery(qUpdateUser,[sub, data["id"]])

    return ""

# RADI NE DIRAJ!!!!!!
@app.route('/userEntry')
def userEntry():
    id=request.args.get('id_user')
    data=exeQuery(qUserEntry, [id])
    return jsonify(data)

# RADI NE DIRAJ!!!!!!
@app.route('/sortedDataEntry')
def sortedDataEntry():
    data=exeQuery(qSorteddataEntry,[])
    return jsonify(data)

#VEKI treAb da teStIRA
@app.route('/sumEntry')
def sumEntry():
    data=exeQuery(qSumEntry,[])
    return jsonify(data)

# RADI NE DIRAJ!!!!!!
@app.route('/sortDataExport')
def sortDataExport():
    data=exeQuery(qSorteddataExport,[])
    return jsonify(data)

# DATE DA BUDE STRING U BAZI I REDOSLED 
@app.route('/addExport', methods=["POST"])
def addExport():
    data=request.get_json()
    arr= [0,0,0,0,0,0,0,0,0,0]
    arr[0]=data['date']
    arr[1]=data['kom']
    arr[2]=data['org']
    arr[3]=data['kont']
    arr[4]=data['cKom']
    arr[5]=data['cOrg']
    arr[6]=data['cKont']
    arr[7] = data['p']
    arr[8] = data['z']
    arr[9] = data['c']

    exeQuery(qAddExport,arr)
    return ""

@app.route('/allExport')
def allExport():
    data=exeQuery(qAllExport,[])
    return jsonify(data)

@app.route('/deleteExport', methods = ["DELETE"])
def deleteExport():
    id=request.args.get('id_export')
    exeQuery(qDeleteExport,[id])
    return ""

#VEKI treAb da teStIRA
@app.route('/sumExport')
def sumExport():
    data=exeQuery(qSumExport,[])
    return jsonify(data)

# RADI NE DIRAJ!!!!!!
@app.route('/updataCrate', methods = ["PUT"])
def updataCrate():
    data=request.get_json()
    arr=[]
    arr.append(data['dostupneZ'])
    arr.append(data['p'])
    arr.append(data['c'])
    arr.append(data['iznajmljene'])
    arr.append(data['pt'])
    arr.append(data['ct'])

    exeQuery(qUpdateCrate,arr)
    return ""

# RADI NE DIRAJ!!!!!!
@app.route('/allCrate')
def allCrate():
    data=exeQuery(qAllCrate,[])
    return jsonify(data)


#VEKI treAb da teStIRA
@app.route('/everSubstraction')
def ev():
    data1=exeQuery(qSumEntry,[])
    data2=exeQuery(qSumExport)
    suma1=[]
    suma2=[]
    suma=[]
    for key in data1:
        suma1.append(data1[key])
    for key in data2:
        suma2.append(data2[key])
    for i in range(0,3):
        suma.append(suma1[i]-suma2[i])
    return jsonify(suma)
    
# RADI NE DIRAJ!!!!!!
CORS(app, origins="*", methods=["GET", "HEAD", "POST", "OPTIONS", "PUT","PATCH", "DELETE"])
app.run("0.0.0.0", 5000)
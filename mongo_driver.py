import os
from pymongo import MongoClient
from datetime import datetime

mongo_uri = os.environ['MONGO_URI']
client = MongoClient(mongo_uri)
db = client.pythonbackend
list_nasabah = db["nasabah"]
list_mutasi = db["mutasi"]

def post_nasabah(nik, nama, no_hp, no_rekening):
  list_nasabah.insert_one({
    "nik": nik,
    "nama": nama,
    "no_hp": no_hp,
    "no_rekening": no_rekening,
    "saldo": 0
  })

def is_data_exist(nik, no_hp):
  result = list_nasabah.find_one({
    "nik": {"$eq": "nik"},
    "no_hp": {"$eq": "no_hp"}
  })
  return result == None

def change_saldo(no_rekening, nominal, is_tabung):
  nasabah = list_nasabah.find_one({"no_rekening": no_rekening})
  if nasabah == None:
    return False, 0
  else:
    list_mutasi.insert_one({
      "no_rekening": no_rekening,
      "waktu": datetime.now(),
      "kode_transaksi": "C" if is_tabung else "D",
      "nominal": nominal
    })
    
    nominal *= 1 if is_tabung else -1
    new_saldo = nasabah['saldo'] + nominal

    if new_saldo < 0:
      return False, -1
      
    list_nasabah.update_one({"no_rekening": no_rekening}, {"$set": {"saldo": new_saldo}})
      
    return True, new_saldo

def check_saldo(no_rekening):
  nasabah = list_nasabah.find_one({"no_rekening": no_rekening})
  if nasabah == None:
    return False, 0
  else:
    return True, nasabah['saldo']

def mutasi_rekening(no_rekening):
  rekening_exist, _ = check_saldo(no_rekening)
  print(rekening_exist)
  if rekening_exist == False:
    return False, []
    
  list_mutasi_filtered = list_mutasi.find({"no_rekening": no_rekening})
  results = []
  for document in list_mutasi_filtered:
      results.append({
        "waktu": document["waktu"],
        "kode_transaksi": document["kode_transaksi"],
        "nominal": document["nominal"],
      })
  return True, results
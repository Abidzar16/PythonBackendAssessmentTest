from flask import Flask, request
import random

from mongo_driver import post_nasabah, is_data_exist, change_saldo, check_saldo, mutasi_rekening

app = Flask(__name__)

def generate_random_number(length, seed):
  random.seed(seed)
  return ''.join([str(random.randint(0, 9)) for _ in range(length)])

@app.route('/')
def index():
  return 'Hello from Flask!'

@app.route('/daftar', methods=['POST'])
def daftar():
  request_data = request.get_json()
  
  try:
    nama = request_data['nama'],
    nik = request_data['nik']
    no_hp = request_data['no_hp']
    
    if is_data_exist(nik, no_hp):
      raise

    no_rekening = generate_random_number(10, nik)

    post_nasabah(nama, nik, no_hp, no_rekening)

    return {
      "no_rekening": no_rekening
    }, 200
    
  except Exception:
    remark = { "remark": "nik dan/atau no_hp sudah terdaftar" }
    return remark, 400

@app.route('/tabung', methods=['POST'])
def tabung():
  request_data = request.get_json()
  no_rekening = request_data['no_rekening']
  nominal = request_data['nominal']

  status, saldo = change_saldo(no_rekening, nominal, True)

  if status:
    return {
      "saldo": saldo
    }, 200
  return {
    "remark": "no_rekening tidak dikenali"
  }, 400

@app.route('/tarik', methods=['POST'])
def tarik():
  request_data = request.get_json()
  no_rekening = request_data['no_rekening']
  nominal = request_data['nominal']

  status, saldo = change_saldo(no_rekening, nominal, False)

  if status:
    return {
      "saldo": saldo
    }, 200

  message = "no_rekening tidak dikenali" if saldo == 0 else "saldo tidak cukup"
  return {
    "remark": message
  }, 400

@app.route('/saldo/<no_rekening>')
def cek_saldo(no_rekening):

  status, saldo = check_saldo(no_rekening)

  if status:
    return {
      "saldo": saldo
    }, 200
  return {
    "remark": "no_rekening tidak dikenali"
  }, 400

@app.route('/mutasi/<no_rekening>')
def mutasi(no_rekening):

  status, list_mutasi = mutasi_rekening(no_rekening)

  if status:
    return {
      "mutasi": list_mutasi
    }, 200
  else :
    return {
      "remark": "no_rekening tidak dikenali"
    }, 400
  
if __name__ == "__main__":
  app.run(host='0.0.0.0', port=81)


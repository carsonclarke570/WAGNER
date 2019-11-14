import base64
import hashlib
import hmac
import json
import os

from flask import Flask
from flask import request

app = Flask(__name__)

@app.route('/', methods=['GET'])
def crc_check():
  # creates HMAC SHA-256 hash from incomming token and your consumer secret
  key = bytes(os.getenv('API_SECRET'), 'utf-8')
  msg = request.args.get('crc_token')
  print(key)
  print(msg)
  digest = hmac.new(key, msg=msg.encode('utf-8'), digestmod=hashlib.sha256).digest()

  # construct response data with base64 encoded hash
  response = {
    'response_token': 'sha256=' + base64.b64encode(digest).decode('utf-8')
  }

  # returns properly formatted json response
  return json.dumps(response)

@app.route('/', methods=['POST'])
def trigger():

  return json.dumps({})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
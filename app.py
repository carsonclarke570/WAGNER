import base64
import hashlib
import hmac
import json
import os

from flask import Flask
from flask import request

app = Flask(__name__)

@app.route('/', methods=['GET'])
def example():
  # creates HMAC SHA-256 hash from incomming token and your consumer secret
  key = bytes(os.getenv('API_SECRET').encode('utf-8'))
  msg = request.args.get('crc_token')
  digest = hmac.new(key, msg=msg, digestmod=hashlib.sha256).digest()

  # construct response data with base64 encoded hash
  response = {
    'response_token': 'sha256=' + base64.b64encode(digest)
  }

  # returns properly formatted json response
  return json.dumps(response)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
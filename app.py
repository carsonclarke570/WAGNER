from flask import Flask

app = Flask(__name__)

@app.route('/', methods=['GET'])
def example():
    # creates HMAC SHA-256 hash from incomming token and your consumer secret
  sha256_hash_digest = hmac.new(API_SECRET, msg=request.args.get('crc_token'), digestmod=hashlib.sha256).digest()

  # construct response data with base64 encoded hash
  response = {
    'response_token': 'sha256=' + base64.b64encode(sha256_hash_digest)
  }

  # returns properly formatted json response
  return json.dumps(response)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
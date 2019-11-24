from enum import Enum
from flask import Flask, Response, request

from worker.factory import WorkerFactory, FactoryError

app = Flask(__name__)

@app.route('/trigger', methods=['POST'])
def trigger():
  if not request.content_type == 'application/json':
    return Response('Error: Invalid Content-Type header', status=400, mimetype='text/plain')

  name = request.json.get('type', None)
  args = request.json.get('args', None)
  if name is None:
    return Response('Error: Requires \'type\' field', status=400, mimetype='text/plain')
  if args is None:
    args = {}

  try:
    worker = WorkerFactory.build(app, name, args)
    worker.start()
  except FactoryError as e:
    return Response('Error: ' + str(e), status=400, mimetype='text/plain')

  return Response(f"Launched '{worker.WORKER_ID}' worker", status=200, mimetype='text/plain')

@app.route('/ping', methods=['GET'])
def ping():
  return Response('OK', status=200, mimetype='text/plain')

if __name__ == '__main__':
  WorkerFactory.setup(app)
  app.run(debug=True, host='0.0.0.0')
  WorkerFactory.teardown(app)
import pygame

from enum import Enum
from flask import Flask, Response, request

from scheduler.scheduler import Scheduler, SchedulerError
from worker.factory import WorkerFactory

app = Flask(__name__)

@app.route('/trigger', methods=['POST'])
def trigger():
  if not request.content_type == 'application/json':
    return Response('Error: Invalid Content-Type header', status=400, mimetype='text/plain')

  try:
    scheduler = Scheduler(request.json, 420)
    scheduler.start()
  except SchedulerError as e:
    return Response('Error: ' + str(e), status=400, mimetype='text/plain')

  return Response(f"Launched scheduler", status=200, mimetype='text/plain')

@app.route('/ping', methods=['GET'])
def ping():
  return Response('OK', status=200, mimetype='text/plain')

if __name__ == '__main__':
  # Init stuff
  pygame.init()
  pygame.mixer.init()
  WorkerFactory.init()
  
  app.run(debug=True, host='0.0.0.0')

# example_consumer.py
import pika, os, csv
from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS
from datetime import datetime

my_bucket = os.environ.get('BUCKET')
db_token = os.environ.get('DBTOKEN')
my_org = os.environ.get('ORG')
rabbit_user = os.environ.get('RABBIT_USER')
rabbit_password = os.environ.get('RABBIT_PASSWORD')


client = InfluxDBClient(url="http://influxdb:8086", token=db_token, org=my_org)
write_api = client.write_api(write_options=SYNCHRONOUS)
query_api = client.query_api()

def process_function(msg):
  mesage = msg.decode("utf-8")
  print(mesage)
  point = Point("temperatura").tag("place", "1").field("used_percent", float(mesage)).time(datetime.utcnow(), WritePrecision.NS)
  write_api.write(my_bucket, my_org, point)
  return

while 1:
  url = os.environ.get('CLOUDAMQP_URL', 'amqp://guest:{}@{}:5672/%2f'.format(rabbit_user, rabbit_password))
  params = pika.URLParameters(url)
  connection = pika.BlockingConnection(params)
  channel = connection.channel() # start a channel
  channel.queue_declare(queue='mensajes') # Declare a queue
  # create a function which is called on incoming messages
  def callback(ch, method, properties, body):
    process_function(body)

  # set up subscription on the queue
  channel.basic_consume('mensajes', callback, auto_ack=True)

  # start consuming (blocks)
  channel.start_consuming()
  connection.close()

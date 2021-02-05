# example_consumer.py
import pika, os, time, csv, time

def save(data, file_name):
  with open(file_name, 'a', newline='') as file:
    writer = csv.writer(file, delimiter=',')
    writer.writerow(data)

def process_function(msg):
  file_name = "data/data_base.csv" 
  if not os.path.isfile(file_name):
    headers = ["","Date","sensor","value"]
    save(headers, file_name)
  print(" [x] Received " + str(msg))
  mesage = msg.decode("utf-8")
  data = mesage.split("-")
  save(data, file_name)
  return

while 1:
  time.sleep(5)
  url = os.environ.get('CLOUDAMQP_URL', 'amqp://guest:guest@rabbit:5672/%2f')
  params = pika.URLParameters(url)
  connection = pika.BlockingConnection(params)
  channel = connection.channel() # start a channel
  channel.queue_declare(queue='mensajes') # Declare a queue

  # create a function which is called on incoming messages
  def callback(ch, method, properties, body):
    process_function(body)

  # set up subscription on the queue
  channel.basic_consume('mensajes',
    callback,
    auto_ack=True)

  # start consuming (blocks)
  channel.start_consuming()
  connection.close()

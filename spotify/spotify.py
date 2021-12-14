import os, time
import pika

time.sleep(10)

########### CONNEXIÓN A RABBIT MQ #######################

HOST = os.environ['RABBITMQ_HOST']
print("rabbit:"+HOST)

connection = pika.BlockingConnection(
    pika.ConnectionParameters(host=HOST))
channel = connection.channel()

#El consumidor utiliza el exchange 'cartero'
channel.exchange_declare(exchange='cartero', exchange_type='topic', durable=True)

#Se crea un cola temporaria exclusiva para este consumidor (búzon de correos)
result = channel.queue_declare(queue="spotify", exclusive=True, durable=True)
queue_name = result.method.queue

#La cola se asigna a un 'exchange'
channel.queue_bind(exchange='cartero', queue=queue_name, routing_key="spotify")


##########################################################


########## ESPERA Y HACE ALGO CUANDO RECIBE UN MENSAJE ####

print(' [*] Waiting for messages. To exit press CTRL+C')

#----------------------------------

import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

def TopSongs(name):
	sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(client_id="client_id",
                                                           client_secret="client_secret"))
	results = sp.search(q='artist:' + name, type='artist')
	items = results['artists']['items']
	if len(items) > 0:
		artist = items[0]
		lz_uri = artist['uri']

	results = sp.artist_top_tracks(lz_uri)
	top= name.capitalize() + "$"
	top= top + artist['images'][0]['url'] + "$"

	for track in results['tracks'][:10]:
		top = top + "track    : " + track["name"] + "\n"

		if(track["preview_url"]):
			top = top + "audio    : " + track["preview_url"] + "\n \n"
		else:
			top = top + "audio    : " + "        ---------" + "\n \n"

	return top

#---------------------------------

def callback(ch, method, properties, body):
	print(body.decode("UTF-8"))
	arguments = body.decode("UTF-8").split(" ")

	name = " ".join(arguments[1:])
	result = TopSongs(name)
	########## PUBLICA EL RESULTADO COMO EVENTO EN RABBITMQ ##########
	print("send a new message to rabbitmq: "+result)
	channel.basic_publish(exchange='cartero',routing_key="discord_writer",body=result)


channel.basic_consume(
    queue=queue_name, on_message_callback=callback, auto_ack=True)

channel.start_consuming()



#######################

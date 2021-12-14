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
result = channel.queue_declare(queue="traductor", exclusive=True, durable=True)
queue_name = result.method.queue

#La cola se asigna a un 'exchange'
channel.queue_bind(exchange='cartero', queue=queue_name, routing_key="traductor")


##########################################################


########## ESPERA Y HACE ALGO CUANDO RECIBE UN MENSAJE ####

print(' [*] Waiting for messages. To exit press CTRL+C')

#----------------------------------
import requests

def Traduccion(source, target, text):
	parametros = {'sl': source, 'tl': target, 'q': text}
	cabeceras = {"Charset":"UTF-8","User-Agent":"AndroidTranslate/5.3.0.RC02.130475354-53000263 5.1 phone TRANSLATE_OPM5_TEST_1"}
	url = "https://translate.google.com/translate_a/single?client=at&dt=t&dt=ld&dt=qca&dt=rm&dt=bd&dj=1&hl=es-ES&ie=UTF-8&oe=UTF-8&inputm=2&otf=2&iid=1dd3b944-fa62-4b55-b330-74909a99969e"
	response = requests.post(url, data=parametros, headers=cabeceras)
	if response.status_code == 200:
		for x in response.json()['sentences']:
			return x['trans']
	else:
		return "Ocurrió un error"

#---------------------------------

def callback(ch, method, properties, body):
	print(body.decode("UTF-8"))
	arguments = body.decode("UTF-8").split(" ")

	idioma = arguments[1]
	frase = " ".join(arguments[2:])
	result = Traduccion("es", idioma, frase)

	########## PUBLICA EL RESULTADO COMO EVENTO EN RABBITMQ ##########
	print("send a new message to rabbitmq: "+result)
	channel.basic_publish(exchange='cartero',routing_key="discord_writer",body=result)


channel.basic_consume(
    queue=queue_name, on_message_callback=callback, auto_ack=True)

channel.start_consuming()



#######################
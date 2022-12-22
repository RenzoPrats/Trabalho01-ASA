import pika

class MetaClass(type):
    _instance = {}
    def __call__(cls, *args, **kwars):
        if cls not in cls._instance:
            cls._instance[cls] = super(MetaClass, cls).__call__(*args, **kwars)
            return cls._instance[cls]


class RabbitMq(metaclass=MetaClass):
    def __init__(self, queue='hello'):
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
        self.channel = self.connection.channel()
        self.queue = queue
        self.channel.queue_declare(queue=self.queue)
    
    
    def publish(self, payload={}):
        self.channel.basic_publish(exchange='', 
                      routing_key='alunos', 
                      body=str(payload))
        print("Published Message")
    
    def close(self):
        self.connection.close()
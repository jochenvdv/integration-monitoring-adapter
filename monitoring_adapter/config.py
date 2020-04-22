from decouple import config


AMQP_URI = config('AMQP_URI', default='amqp://monitoring_user:monitoring_pwd@10.3.50.9:5672')
QUEUE_NAME = config('QUEUE_NAME', default='monitoring.queue')

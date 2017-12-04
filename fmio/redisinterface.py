import os
from redis import StrictRedis
import urlparse

redis_url = os.getenv('REDIS_URL')

urlparse.uses_netloc.append('redis')
url = urlparse.urlparse(redis_url)
conn = StrictRedis(host=url.hostname, port=url.port, db=0, password=url.password)

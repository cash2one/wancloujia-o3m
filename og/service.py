import redis

from django.utils import simplejson

_r = redis.StrictRedis()

def notify(user, password):
	_r.rpush('users', simplejson.dumps({
        'realname': user.realname, 
        'username': user.username, 
        'email': user.email,
        'password': password, 
        "link": "suning.wandoujia.com"
    }))

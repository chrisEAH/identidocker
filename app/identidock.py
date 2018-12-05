from flask import Flask, Response, request
import requests
import hashlib
import redis

app = Flask(__name__)
salt="UNIQUE_SALT"

default_name='chris'

cache=redis.StrictRedis(host='redis', port=6379, db=0)

@app.route('/', methods=['GET', 'POST'])
def mainpage():
	name=default_name
	
	if request.method == 'POST':
		name = request.form['name']
		
	salted_name=salt+name
	name_hash=hashlib.sha256(salted_name.encode()).hexdigest()
	
	
	header='<html><head><title>Identidock</title></head><body>'
	body='''<form method="Post">
		hallo <input type="text" name="name" value"{0}">
		<input type="submit" value="abschicken">
		</form>
		<p>Du siehtst aus wie ein:
		<img src="/monster/{1}" />
		'''.format(name, name_hash)
	footer='</body></html>'
	return header + body + footer
	
@app.route('/monster/<name>')
def get_identicon(name):
	image=cache.get(name)
	if image is None:
		print("chache miss", flush=True);
		r=requests.get('http://dnmonster:8080/monster/' + name + '?size=80')
		image=r.content
		cache.set(name, image)	
	return Response(image, mimetype='image/png')


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
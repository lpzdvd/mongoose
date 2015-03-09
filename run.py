#!env/bin/python
from app import app

app.run(debug = True, use_debugger = True, 
	use_reloader = True, host = '127.0.0.1', port = 5000)
mkdir uploads
gunicorn -b -w 4 5.9.107.99:5000 server:app
mkdir uploads
gunicorn  -w 4 -b 5.9.107.99:5000 server:app
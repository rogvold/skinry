mkdir uploads
gunicorn -b 5.9.107.99:5000 server:app
#! /home/ubuntu/miniconda/bin/python

from app import app
import flask_excel as excel

if __name__ == '__main__':
  excel.init_excel(app)
  app.run(host='0.0.0.0', debug=True, port=8069)

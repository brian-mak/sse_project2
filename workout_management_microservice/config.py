import os
import urllib

class Config:
    params = urllib.parse.quote_plus(os.getenv('AZURE_SQL_CONNECTIONSTRING'))
    SQLALCHEMY_DATABASE_URI = "mssql+pyodbc:///?odbc_connect=%s" % params
    SQLALCHEMY_TRACK_MODIFICATIONS = False
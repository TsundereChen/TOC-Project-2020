import os
from sys import exit
from yaml import load, dump
try:
    from yaml import CLoader as Loader, CDumper as Dumper
except ImportError:
    from yaml import Loader, Dumper

try:
    f = open(os.path.dirname(os.path.realpath(__file__)) + "/config.yml", "r")
except IOError:
    print("Error while opening file, please check if config.yml exists.")
    exit(1)

configRaw = f.read()
configYaml = load(configRaw, Loader=Loader)
channel_secret = configYaml["line"]["channel_secret"]
channel_access_token = configYaml["line"]["channel_access_token"]
influxdb_host = configYaml["influxdb"]["address"]
influxdb_port = configYaml["influxdb"]["port"]
influxdb_username = configYaml["influxdb"]["username"]
influxdb_password = configYaml["influxdb"]["password"]

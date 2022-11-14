import json
def get(key):
    conf = open("config.json")
    data = json.load(conf)
    conf.close()
    try:
        return data[key]
    except:
        print("Config missing value error: Key '"+str(key)+"' does not exist.")
        return ""

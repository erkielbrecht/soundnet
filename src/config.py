import toml


def get(cat, key):
    conf = open("config.toml")
    data = toml.load(conf, _dict=dict)
    conf.close()
    try:
        return data[cat][key]
    except:
        print("Config missing value error: Key '" + str(key) + "' does not exist.")
        return ""


def get_cat(cat):
    conf = open("config.toml")
    data = toml.load(conf, _dict=dict)
    conf.close()
    try:
        return data[cat]
    except:
        print("Config missing value error: Category '" + str(cat) + "' does not exist.")
        return ""

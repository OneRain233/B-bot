import requests
import json
def get_data(s):
    try:
        magic_api = "http://122.112.151.101:13000/magic"
        bake_api = "http://122.112.151.101:13000/bake"
    except Exception as e:
        return False
    data = {
        "input": s
    }
    res = requests.post(magic_api, json=data)
    j = res.json()
    print(j['value'])
    values = j['value']
    ret = []
    for value in values:
        r = ["{} {}".format(i['op'], i['args']) for i in value['recipe']]
        new_data = {
            "input": s,
            "recipe": value['recipe']
        }
        print(json.dumps(new_data))
        new_res = requests.post(bake_api, json=new_data)
        new_j = new_res.json()
        new_value = new_j['value']
        new_type = new_j['type']
        
        if new_type == "byteArray":
            # to string
            ss = ""
            for i in new_value:
                ss += chr(i)
        
            new_value = ss
                
        
        ret.append(
            "Value: \n" + str(new_value) + "\nRecipe: \n" + " -> ".join(r) + "\nType:" + str(new_type)
        )
    return ret

    
    
if __name__ == "__main__":
    data = get_data("MTIzMTIzMjEzMjEz")
    print("\n\n".join(data))
from bitcoinlib.keys import Address
from bitcoinlib.keys import Key
from bitcoinlib.keys import HDKey
from btc_brainwallet import BrainWallet
import openai
import argparse
import requests
import dirtyjson
import time
from requests.exceptions import HTTPError
from hashlib import sha256
# Initialize the argument parser
parser = argparse.ArgumentParser()
parser.add_argument('--api_key', required=True, help='Your OpenAI API Key')

# Parse the command-line arguments
args = parser.parse_args()

# Set the OpenAI API key from the command-line argument
api_key = args.api_key
openai.api_key = api_key

logf = open("success.txt", "a")
print("Logging to success.txt")

# Define a prompt for the model
root_prompt = "Act as literature expert"
prompt = "Give me a json object containing 10 random lines from different books without author just phrase try to not repeat yourself. Format json as line:[Output]"



digits58 = '123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz'

def decode_base58(bc, length):
    n = 0
    for char in bc:
        n = n * 58 + digits58.index(char)
    return n.to_bytes(length, 'big')
def check_bc(bc):
    try:
        bcbytes = decode_base58(bc, 25)
        if bcbytes[-4:] == sha256(sha256(bcbytes[:-4]).digest()).digest()[:4]:
            return bc
    except Exception:
        return ""



def btc_pass_to_address(passphrase, delimiter = '|'):
    wallet = BrainWallet()
    private_key, address = wallet.generate_address_from_passphrase(passphrase)
    hd_key = HDKey(private_key)
    uncompressed_key = Key(hd_key.public_hex) 
    all_addresses = [check_bc(hd_key.address()), check_bc(uncompressed_key.address_uncompressed()), check_bc(hd_key.address(script_type = 'p2sh'))]
    
    return {delimiter.join(all_addresses):private_key}


def explorer_checker(query):
    try:
        explorer_response = requests.get('https://blockchain.info/multiaddr?active=' + query)
        explorer_response.raise_for_status()
        jsonResponse = explorer_response.json()
        for every_address in jsonResponse['addresses']:
            if every_address['n_tx'] > 0: # Checking number of txes 
                print(every_address['address'])
                logf.write('%s\n' % every_address['address']) 
                for key, value in addresses_to_check.items(): 
                    logf.write('%s\n' %  value)        
    except HTTPError as http_err:
        print(f'HTTP error occurred: {http_err}')
    except Exception as err:
        print(f'Other error occurred: {err}')


try:
    # Context creation
    response = openai.Completion.create(
        engine="gpt-3.5-turbo-instruct",
        prompt=root_prompt,
        max_tokens=100
    )
except:
    print("Limit reached")

while True:
    try:
        try:
            response = openai.Completion.create(
            engine="gpt-3.5-turbo-instruct",
            prompt=prompt,
            max_tokens=500  # Adjust the number of tokens as needed
            )
        except:
            defaultjson='''
                    {
                    "passphrase1": "2b0rN0t2b$ecure!",
                    "passphrase2": "4llUneedIsL0v3#Sec",
                    "passphrase3": "Liv3&LetLiV3#Safe",
                    "passphrase4": "3v3ryCloud$ilv3rLin1n9!",
                    "passphrase5": "3arlyBirdCatc3sW0rm#",
                    "passphrase6": "4ct!0ns$peakL0ud3r",
                    "passphrase7": "AP3nny4Y0urTh0ught$",
                    "passphrase8": "B3@uty1sEyeOfTh3B3holdr#",
                    "passphrase9": "4n@pp1eAD@yK33psD0ct0rAw@y!",
                    "passphrase10": "Wh3n!nRom3D0@5Rom@n5D0#"
                    }
            '''
            if 'response' in locals():
                defaultjson = response.choices[0].text
            gptresponse_object = dirtyjson.loads(defaultjson)

            addresses_to_check = {}       
            for eachline in gptresponse_object:
                password = gptresponse_object[eachline].strip()
                addresses_to_check.update(btc_pass_to_address(password))
                print(f'passphrase: {password}')
        
            build_query = ""
            for key, value in addresses_to_check.items():  
                build_query += key + "|"
            build_query=build_query.rstrip(build_query[-1]) # Deleting last character
            print(build_query)
            explorer_checker(build_query)
    except:
        print("Error occured, sleeping...\n")
        time.sleep(10)
logf.close()



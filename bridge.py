import serial
import time
import json
from web3 import Web3
ARDUINO_PORT = 'COM5'  #arduino port 
GANACHE_URL = "http://127.0.0.1:7545"  
CONTRACT_ADDR = "0xaf4bcA440F540e41Fd9c9eB2f15723A52894e160" 
PRIVATE_KEY = "0xe47448cbcd31a23bfc4d34944f38e99267556064398b68774411e09f4cf323df"
ABI_JSON = """ 
[
	{
		"anonymous": false,
		"inputs": [
			{
				"indexed": false,
				"internalType": "uint256",
				"name": "value",
				"type": "uint256"
			},
			{
				"indexed": false,
				"internalType": "string",
				"name": "sensor",
				"type": "string"
			},
			{
				"indexed": false,
				"internalType": "uint256",
				"name": "timestamp",
				"type": "uint256"
			}
		],
		"name": "DataStored",
		"type": "event"
	},
	{
		"inputs": [
			{
				"internalType": "uint256",
				"name": "_value",
				"type": "uint256"
			},
			{
				"internalType": "string",
				"name": "_sensor",
				"type": "string"
			}
		],
		"name": "logData",
		"outputs": [],
		"stateMutability": "nonpayable",
		"type": "function"
	}
]
""" 

def main():
    print("--- STARTING IOT BLOCKCHAIN BRIDGE ---")
    
    # 1. Connect to Blockchain
    try:
        w3 = Web3(Web3.HTTPProvider(GANACHE_URL))
        if w3.is_connected():
            print(f" [SUCCESS] Connected to Blockchain at {GANACHE_URL}")
        else:
            print(" [ERROR] Could not connect to Ganache. Is it running?")
            return
            
        # Prepare the Contract
        contract = w3.eth.contract(address=CONTRACT_ADDR, abi=json.loads(ABI_JSON))
        account = w3.eth.account.from_key(PRIVATE_KEY)
        print(f" [INFO] Using Account: {account.address}")

    except Exception as e:
        print(f" [ERROR] Blockchain Setup Failed: {e}")
        return

    # 2. Connect to Arduino
    try:
        print(f" [INFO] Connecting to Arduino on {ARDUINO_PORT}...")
        ser = serial.Serial(ARDUINO_PORT, 9600, timeout=1)
        time.sleep(2) # Give connection time to settle
        print(" [SUCCESS] Arduino Connected!")
    except Exception as e:
        print(f" [ERROR] Arduino Connection Failed: {e}")
        print(" Suggestion: Is the Serial Monitor open in Arduino IDE? Close it!")
        return

    print("\n--- WAITING FOR DATA ---\n")

    # 3. Main Loop
    while True:
        try:
            if ser.in_waiting > 0:
                # Read line from Arduino
                line = ser.readline().decode('utf-8').strip()
                
                if line.isdigit(): # Ensure it's a clean number
                    temp_value = int(line)
                    print(f" [IOT] Received Sensor Data: {temp_value}°C")
                    
                    # Send to Blockchain
                    print(" [CHAIN] Sending transaction...")
                    
                    # Build Transaction
                    tx = contract.functions.logData(temp_value, "Arduino_Sensor").build_transaction({
                        'from': account.address,
                        'nonce': w3.eth.get_transaction_count(account.address),
                        'gas': 3000000,
                        'gasPrice': w3.to_wei('20', 'gwei')
                    })
                    
                    # Sign & Send
                    signed_tx = w3.eth.account.sign_transaction(tx, PRIVATE_KEY)
                    tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)
                    
                    print(f" [SUCCESS] Data stored on Blockchain!")
                    print(f"          Tx Hash: {w3.to_hex(tx_hash)}")
                    print("-" * 40)
                    
        except Exception as e:
            print(f"Error: {e}")
            break

if __name__ == "__main__":
    main()
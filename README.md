Integration of IoT Sensors with Ethereum Blockchain

STEP – 1 : Take Hardware let us say Arduino Uno R3 and Connect it to your Computer using Arduino IDE using Arduino cable. 
 
And take the Arduino demo program as random temperature values from 20 to 30. the code is : 
void setup() {
  Serial.begin(9600); // Start serial communication
}

void loop() {
  // Simulate a temperature between 20 and 30 degrees
  int sensorValue = random(20, 30);
  
  // Send ONLY the number. This makes it easy for Python to read.
  Serial.println(sensorValue);
  
  delay(3000); // Send data every 3 seconds
}

STEP – 2 : Download and install Ganache from the Truffle Suite website https://archive.trufflesuite.com/ganache/ then   Open Ganache and click "Quickstart" and Note the RPC Server URL (usually HTTP://127.0.0.1:7545).Copy the Private Key of the first account (Click the "Key" icon on the right).
 
STEP – 3 : Open Remix IDE (http://remix.ethereum.org) in a browser and Create a new file DataLogger.sol and paste the Solidity code.
Solidity code: 
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract DataLogger {
    // This event writes the data to the permanent blockchain log
    event DataStored(uint256 value, string sensor, uint256 timestamp);

    function logData(uint256 _value, string memory _sensor) public {
        emit DataStored(_value, _sensor, block.timestamp);
    }
}

Go to the Solidity Compiler tab and in "Advanced Configurations," set EVM Version to "Paris" (to ensure compatibility with Ganache) and Click Compile.
Now Go to the Deploy tab and Set Environment to "External Http Provider" and Enter the Ganache URL: http://127.0.0.1:7545 then Click Deploy. Now Copy the Contract Address and the ABI (from the Compiler tab).
 
 

STEP – 4 : Install python libraries in command prompt as : 
pip install web3 pyserial
Create a file named bridge.py and Update the ARDUINO_PORT, CONTRACT_ADDRESS, and PRIVATE_KEY in the script .

Bridge.py code : 
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

STEP – 5 : Go to command prompt and the folder the python file reside in and type python bridge.py 
The data is stored in the immutable ledger called Ganache . 
 
 

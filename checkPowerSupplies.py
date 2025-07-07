from cloudvision.Connector.grpc_client import GRPCClient, create_query
from concurrent.futures import ThreadPoolExecutor, as_completed
from pprint import pprint
import argparse
import time
import sys

# Generic function to run queries
def grpcQuery(args, dataset, pathElts):
    results = {}
    query = [
       create_query([(pathElts, [])], dataset)
   ]

    with GRPCClient(args.apiserver, certs=args.certFile, key=args.keyFile,
            ca=args.caFile, token=args.tokenFile) as client:
        for batch in client.get(query):
            for notif in batch["notifications"]:
                for key, value in notif["updates"].items():
                    results[key] = value
    return results

# Function to get power supply status. Broken out as a separate function to work better with multithreading.
def getPowerSupplyStatus(args, device):
    dataset = device
    results = {}
    # Query to figure out how many power supplies are present in the device.
    pathElts = [
        "Sysdb",
        "environment",
        "archer",
        "power",
        "status",
        "powerManager",
        "powerSupplies",
    ]
    powerQuery = grpcQuery(args, dataset, pathElts)
    
    for powerSupply in powerQuery.keys():
        # Query to get the status of each power supply.
        pathElts = [
            "Sysdb",
            "environment",
            "archer",
            "power",
            "status",
            "powerManager",
            "powerSupplies",
            powerSupply
        ]
        PowerSupplyQuery = grpcQuery(args, dataset, pathElts)
        # Format results with useful information 
        results[powerSupply] = {
            'name': PowerSupplyQuery['name'],
            'state': PowerSupplyQuery['state']['Name'],
            'capacity': PowerSupplyQuery['capacity']['value'],
            'outputPower': PowerSupplyQuery['outputPower']['value']
        }
    return results

# Function to handle command line arguments.
def parse_args():
    parser = argparse.ArgumentParser(description="Query DatasetInfo from CVaaS")
    parser.add_argument('--apiserver', required=True, help='API server (e.g., api.arista.io:443)')
    parser.add_argument('--tokenFile', help='Path to token file')
    parser.add_argument('--certFile', help='Client certificate (optional)')
    parser.add_argument('--keyFile', help='Private key (optional)')
    parser.add_argument('--caFile', help='CA cert (optional)')
    return parser.parse_args()

def main(args):
    # Dictionary to hold final results.
    results = {}    

    # Query to get list of devices in CVaaS to check power supply status.
    pathElts = [
        "DatasetInfo",
        "Devices"    
    ]
    dataset = "analytics"   
    deviceQuery = grpcQuery(args, dataset, pathElts)

    # Dictionary comprehension to filter physical devices
    devices_to_check = {
        device: deviceInfo
        for device, deviceInfo in deviceQuery.items()
        if deviceInfo['deviceType'] == 'EOS' and ('CCS' in deviceInfo['modelName'] or 'DCS' in deviceInfo['modelName'])
    }

    # Use ThreadPoolExecutor to run getPowerSupplyStatus in parallel
    # You can adjust max_workers based on the server running the script and the number of switches you are checking.
    with ThreadPoolExecutor(max_workers=10) as executor:
        future_to_device = {
            executor.submit(getPowerSupplyStatus, args, device): (device, info)
            for device, info in devices_to_check.items()
        }
        # Process results as they are completed
        for future in as_completed(future_to_device):
            device, info = future_to_device[future]
            try:
                power_status = future.result()
                results[device] = {
                    'hostname': info['hostname'],
                    'powerSupplies': power_status
                }
            # Handles errors so an error with one device won't stop the script.
            except Exception as e:
                results[device] = {
                    'hostname': info['hostname'],
                    'error': str(e)
                }
    # Data is ready to be viewed or sent to any other platforms as needed.
    pprint(results)
    return 0
 
 
if __name__ == "__main__":
    args = parse_args()
    start = time.time()
    exit_code = main(args)
    duration = time.time() - start
    print(f"\nCompleted in {round(duration, 2)} seconds")
    sys.exit(exit_code)
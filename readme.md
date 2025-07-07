# CVaaS Power Supply Status Checker

This Python script queries Arista CloudVision-as-a-Service (CVaaS) via gRPC to retrieve power supply status for physical EOS devices. It uses multithreading to improve performance and filters for devices with `CCS` or `DCS` in their model name.

---

## 🔧 Features

- Connects to CloudVision using gRPC.
- Filters for physical EOS devices.
- Retrieves detailed power supply status (name, state, capacity, and output power).
- Uses a thread pool for parallel queries.
- Gracefully handles per-device query errors.

---

## 📦 Requirements

- Python 3.9.6+
- Arista CloudVision gRPC client (`cloudvision` Python package)
- Access to CVaaS API credentials (token or cert/key)

---

## 🧪 Set Up a Virtual Environment (Recommended)

To avoid dependency conflicts, use a Python virtual environment:

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows use: venv\Scripts\activate
pip install cloudvision
```

---

## 🚀 Usage

```bash
python checkPowerSupplies.py --apiserver <API_SERVER> [--tokenFile <TOKEN_FILE>] [--certFile <CERT_FILE> --keyFile <KEY_FILE>] [--caFile <CA_FILE>]
```

### Required arguments:
- `--apiserver` – CVaaS gRPC endpoint, e.g. `www.cv-prod-na-northeast1-b.arista.io` (Login to CVaaS and look at the url, it will have this info for your tenant.)

### Optional arguments:
- `--tokenFile` – Path to token file for authentication (Setup in CVaaS under Settings->Serivce Accounts->Service Account Tokens)
- `--certFile` – Path to client certificate
- `--keyFile` – Path to private key
- `--caFile` – Path to CA certificate

> You must provide **either** a `--tokenFile` or a `--certFile`/`--keyFile` pair.

---

## 📤 Output

Results are printed in a structured dictionary format:

```python
{
  "<device_id>": {
    "hostname": "<device_hostname>",
    "powerSupplies": {
      "PowerSupply<#>": {
        "name": "<name>",
        "state": "<state>",
        "capacity": <"capacity">,
        "outputPower": <"outputPower">
      },
    }
  },
}
```

If a device query fails:

```python
"<device_id>": {
  "hostname": "<device_hostname>",
  "error": "<exception message>"
}
```

---

## 🧠 How It Works

1. Queries the list of devices from the `analytics` dataset.
2. Filters for EOS devices with model names containing `CCS` or `DCS`.
3. Runs a gRPC query in parallel for each device to retrieve power supply info.
4. Formats and prints the results.

---

## ⚙️ Configuration Tips

- Tune `max_workers` in `ThreadPoolExecutor` based on the number of devices and your local machine’s/server's resources.

---

## ✍️ Author

Written by [Steven Hazard](https://github.com/hazardsg)
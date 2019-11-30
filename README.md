# Workers: Asynchronous Generic Nano-modules with Entity Registry (WAGNER)

A python Flask API designed to trigger various events on a Raspberry Pi.

## Requirements

Idk

## Usage

Send a POST request to the `/trigger` endpoint with a JSON body organized as such:

```
{
    "workers": [
        {
            "type": "WORKER_ID",
            "args": {
                "key": "value"
            }
        },
        {
            "type": "WORKER_ID",
            "args": {
                "key": "value"
            }
        },
    ],
    "schedule": {
        "mode": "delay",
        "seconds": "30"
    }
}
```

The API's scheduler provides three trigger modes:
* instant
* delay
* alarm


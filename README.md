### Optimus 🤖

#### Installation:

1. Clone the repository and cd into it
2. Run `pip install . `


####  How to run ?

```
usage: Optimus [-h] [-r] [-p PORT] [-t THREADS]

A toy DNS server made for fun :)

optional arguments:
  -h, --help  show this help message and exit
  -r          Run DNS server
  -p PORT     Port to run the server on (defaults to 53)
  -t THREADS  Number of worker threads to spin up for handling requests (defaults to 10)
```

#### Note:
You may not be able to run Optimus on Port 53 as your OS already is likely to be running it's own resolver.

To workaround this, you may

1. Either, disable your existing resolver and run Optimus on port 53 (which might also require root privileges)[1].
2. Or, Simply run the Optimus server on another port.


#### [1] Running Optimus with Root privileges:
1. Grant executable permission to script `run` by running `chmod +x run`.
2. Execute `./run` to stop systemd resolver daemon and point your system to use optimus

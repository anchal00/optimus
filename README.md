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

(There might be better ways to do this, but this is the temporary solution available at the moment)

Once the existing resolver is disabled and Port 53 is freed up

1. Copy the script `INIT` to `/usr/local/bin`
2. Rename `INIT` to `optimus_server`
3. Make `optimus_server` executable using `chmod +x /usr/local/bin/optimus_server`
4. Now you can invoke Optimus using this executable from your terminal simply by running `optimus_server`


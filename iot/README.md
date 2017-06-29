# Setting up the IoT Connection

Establishing a secure (SSL) connection between an IoT device (Raspberry Pi 3) and a server (Windows 10).

## Build SSL Certificates

[Install openssl on windows](https://sivatechworld.wordpress.com/2015/06/11/step-by-step-installing-and-configuring-mosquitto-with-windows-7/ ). Be sure to get openssl version 1.0.2L, **NOT** version 1.1.

## Set up the secure certificates

* Open a Git bash and switch shells: `winpty bash`

* Create a directory to contain the certificates: `\c\Users\<username>\Documents\certs`

Follow instructions from here: https://developer.artik.io/documentation/advanced-concepts/secure/secure-intro.html

1. Go to the directory 
`cd \c\Users\<username>\Documents\certs`

2. Generate a new private key for the server, in RSA encryption format.
`openssl genrsa -des3 -out m2mqtt_srv.key 2048`

3. Using that private key, generate a server "certificate signing request" (CSR) file.
`openssl req -key m2mqtt_srv.key -out m2mqtt_srv.csr -new`

4. Acting as your own "mini" X.509 Certificate Authority (CA), create your own CA private key file and CA certificate.
`openssl req -new -x509 -days 3650 -keyout ca.key -out ca.crt`

5. "Sign" the CSR, using your newly-minted CA credentials, to create your server certificate.
`openssl x509 -req -in m2mqtt_srv.csr -CA ca.crt -CAkey ca.key -CAcreateserial -out m2mqtt_srv.crt -days 3650`

6. Disable pass phrase question: first copy the key file
`cp m2mqtt_srv.key m2mqtt_srv.key.old`

7. Then re-run the rsa to strip the passphrase
`openssl rsa -in m2mqtt_srv.key.org -out m2mqtt_srv.key`

# Install Mosquitto

[Download and install mosquitto](http://www.eclipse.org/downloads/download.php?file=/mosquitto/binary/win32/mosquitto-1.4.12-install-win32.exe&mirror_id=1135)

[Download the dependencies (dlls) needed](http://www.mirrorservice.org/sites/sources.redhat.com/pub/pthreads-win32/ )

Be sure to copy the dlls to the approprate directories following the instructions.

# Configure Mosquitto

Open the `mosquitto.conf` file in a text editor to modify it. The following lines need to be changed:
1. `#port` to `port 8883`
2. `#cafile` to `cafile C:\Users\<username>\Documents\certs\ca.crt`
3. `#certfile` to `certfile C:\Users\<username>\Documents\certs\m2mqtt_srv.crt`
4. `#keyfile` to `keyfile C:\Users\<username>\Documents\certs\m2mqtt_srv.key`
5. `#tls_version` to `tls_version tlsv1`

# Start the Mosquitto broker

The mosquitto broker can now be started using the configuration file. Open a `Git Bash` in the mosquitto program files folder that has `mosquitto.exe`. Then execute: `./mosquitto.exe -c mosquitto.conf`

# Configure node-red

Now configure the node-red module to listen to the mosquitto broker. Using the `mqtt in` node, set it up with a new server:

* `server: localhost`
* `port: 8883`
* `Enable secure (SSL/TLS) connection` checked

Create a new TLS Configuration by clicking the pencil next to the drop-down box.

* `Certificate: C:\Users\<username>\Documents\certs\m2mqtt_srv.crt`
* `Private Key: C:\Users\<username>\Documents\certs\m2mqtt_srv.key`
* `CA Certificate: C:\Users\<username>\Documents\certs\ca.crt`

Uncheck `Verify server certificate`

Set the topic on the `mqtt in` node to `test` and use `QoS: 2`.

After deploying the flow, the `mqtt in` node should show the green box and read `connected`. Connect the output to the debug node displaying the `msg.payload`.

# Configure the Raspbery Pi

## Set up IP query
The Pi should be updated and upgraded to the latest version of everything: `sudo apt-get update` and `sudo apt-get upgrade`. I also installed a mechanism to email myself the Pi's IP address on start so that I don't need to connect a monitor or keyboard (in case the IP address changes). Following [this] (http://elinux.org/RPi_Email_IP_On_Boot_Debian)), I had to modify the startup script to `startup_mailer.py` and I needed to add the `sleep 30` line to the `/etc/rc.local` file in order to get the email.

I also set up a second user on the pi: `iot` to house and work with the iot data (and not have everything with the main pi user).

## Set up certificate

Copy the CA Certificate from `C:\Users\<username>\Documents\certs\ca.crt` to the `/home/iot` directory on the Pi.

## Node-red

Log into the pi as the `iot` user. Run the node-red service `node-red`. It will prompt for the `[sudo]` password, but it doesn't need it to succeed. Connect to the node-red server from the remote machine (port `1880` from a browser). Build a simple flow that connects a string injector to an `mqtt out` node.

Configure the `mqtt out` node:
* Add a new mqtt broker
    * Server: `<ip address of server>`
    * Port: `8883`
    * Enable secure (SSL/TLS) connection: `checked`
    * Configure a new TLS:
        * CA Certificate: `/home/iot/ca.crt`
        * Verify server certificate: `unchecked`

* Topic: `test`
* QoS: `2`

Everything else I left default.

Deploy the flow. If configured correctly, the `mqtt out` node should have the green box and read `connected`.

 I created a string injector that sends a string through the secure mqtt channel to the waiting windows server.

 
# Direct Ethernet Connection

In order to connect the Pi directly to the windows laptop:

1. Connect the Pi directly to the windows machine via an ethernet cable
2. Bridge the connection between the ethernet network interface and the wifi network interface on the windows machine
    * Control-Left-click on both interfaces to select both 
    * Right-click on one - select "Bridge Connections" (or something like that...)
    * This will create a bridge between the two, allowing the Pi to access the WiFi through the windows machine
3. Boot the Pi. It should send an email with its new IP address through the ethernet port (10.10.12.152)
4. Disable the WiFi connection on the Pi (as to not confuse things... )
    * Edit the configuration file: `sudo nano /etc/wpa_supplicant/wpa_supplicant.conf`
    * Change the WIFI name of the current connection to something incorrect (I added a `1` to the end of the name)
    * Save
5. Get the windows IP address. From a windows Git Bash: `ipconfig -all`. Look for the "Ethernet adapter Network Bridge". Look for the `IPv4 Address` (10.10.12.126). 
6. Run `node-red` on the Pi and connect to the UI from the windows machine. Change the `mqtt out` node server IP address to the windows machine address. That seems to do the trick - the connection box goes green.













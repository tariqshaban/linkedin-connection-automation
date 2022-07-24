Automating LinkedIn's Connection Procedure
==============================
This is a project that automates LinkedIn connection requests, written in Python.


Getting Started
------------
Clone the project from GitHub

`$ git clone https://github.com/tariqshaban/linkedin-connection-automation.git`

Install the required Python dependencies by running the following command `pip install -r requirements.txt`.

Adjust the following critical parameters in `config.json`:

| Key                  | Description                                                                             |
|----------------------|-----------------------------------------------------------------------------------------|
| `webDriver`          | Specify the desired webdriver                                                           |
| `maximumConnections` | Specify the threshold of processed connections before stopping, set to -1 for unlimited |
| `profileNames`       | Specify the profile name(s) to iterate                                                  |

Supported web drivers:

* Internet Explorer `internet explorer`
* Microsoft Edge `edge`
* Mozilla Firefox `firefox`
* Opera `opera`
* Google Chrome `chrome`

The website structure may change in time, modify the following values in `config.json` if it caused breaking changes:

| Key                                                    | Description                                |
|--------------------------------------------------------|--------------------------------------------|
| `endpoints`&#10132;`longin`&#10132;`url`               | Specify the login URL                      |
| `endpoints`&#10132;`longin`&#10132;`usernameElementId` | Specify the username HTML input element ID |
| `endpoints`&#10132;`longin`&#10132;`passwordElementId` | Specify the password HTML input element ID |

Usage
------------

Navigate to `main.py` and invoke the desired methods

``` python
# Requests a username/password combination in the console stream
AuthenticationHandler.login() # ==> Must be invoked first

# Redirects to 'https://www.linkedin.com/mynetwork/' and connects to all profiles under the 'More suggestions for you' section
ConnectionHandler.connect_to_suggestion()

# Fetches a specified profile(s) by their name(s) in the URL and connects to all of their connections
ConnectionHandler.connect_to_all_profile_connections(profile_name: str)

# Fetches a specified profile(s) by their name(s) in the URL and retrieves all of their connections
ConnectionHandler.get_profile_connections(profile_name: str)
```

Note that the `profile_name` argument is not the real profile name at the webpage, but rather the **user's denoted URL
profile name**

Disclaimer
------------

The program requires a valid username/password combination in order to function; such credentials will **NEVER** be
disclosed, stored, processed, or sent to any server/third-party provider. You can inspect the code to verify its
confidentiality level in handling such sensitive data.

--------
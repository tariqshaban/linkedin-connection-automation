Automating LinkedIn's Connection Procedure
==============================
This is a project that automates LinkedIn connection requests, written in Python.


Getting Started
------------
Clone the project from GitHub

`$ git clone https://github.com/tariqshaban/linkedin-connection-automation.git`

Install the required Python dependencies by running the following command `pip install -r requirements.txt`.

Adjust the following critical parameters in `config.json`:

| Key                                           | Description                                                                                                                                                 |
|-----------------------------------------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `webDriver`                                   | Specify the desired webdriver                                                                                                                               |
| `maximumConnections`                          | Specify the threshold of processed connections before stopping (for each method), set to -1 for unlimited                                                   |
| `securityVerificationDelay`                   | Set the time in seconds necessary to manually solve the security verification question upon login                                                           |
| `webLoadDelay`                                | Specify the number of seconds to wait till a website is loaded successfully (compensates for slow internet connections), throws an exception when times out |
| `companyNames`                                | Specify the company name(s) to iterate                                                                                                                      |
| `profileNames`                                | Specify the profile name(s) to iterate                                                                                                                      |
| `endpoints`&#10132;`longin`&#10132;`username` | Specify the username. *Optional*, useful since the username will not be required every runtime, **insecure** since credentials are saved in a raw file.     |
| `endpoints`&#10132;`longin`&#10132;`password` | Specify the password. *Optional*, useful since the password will not be required every runtime, **insecure** since credentials are saved in a raw file.     |

Supported web drivers:

* Internet Explorer `internet explorer`
* Microsoft Edge `edge`
* Mozilla Firefox `firefox`
* Opera `opera`
* Google Chrome `chrome`

The website structure may change in time, modify the values in `config.json` accordingly if it caused breaking changes.

Usage
------------

Navigate to `main.py` and invoke the desired methods

``` python
# Requests a username/password combination in the console stream
AuthenticationHandler.login() # ==> Must be invoked first

# Redirects to 'https://www.linkedin.com/mynetwork/' and connects to all profiles under the 'More suggestions for you' section
ConnectionHandler.handle_suggestions(connect: bool = False)

# Fetches a specified profile(s) by their name(s) in the URL and recursively connect to all of their connections
ConnectionHandler.handle_profile_connections(connect: bool = False, depth=1)

# Retrieves all of the specified company's/companies' people, and connects to them
ConnectionHandler.handle_company_people(connect: bool = False)

# Accepts/ignores all incoming connection requests
ConnectionHandler.handle_received_invitations(accept: bool = False, ignore: bool = False)

# Withdraws all outgoing connection requests
ConnectionHandler.handle_sent_invitations(withdraw: bool = False) # ==> Warning, LinkedIn will not permit reconnecting to the same profile for three weeks
```

To specify either the company name or the profile name, `companyNames` and `profileNames` keys in `config.json` must be
modified. Note that the values should not be the actual company/profile name on the webpage itself; but rather the 
**denoted string value from the URL**.

For precautionary reasons, the default behaviour of the methods is **passive**; that is, they only generate CSV files
without taking action; to override such behaviour, set the boolean flag to the respected method's argument to true.

Disclaimer
------------

The program requires a valid username/password combination in order to function; such credentials will **NEVER** be
disclosed, stored, processed, or sent to any server/third-party provider. You can inspect the code to verify its
confidentiality level in handling such sensitive data.

LinkedIn will temporarily restrict your account if too many requests were issued in a small timeframe.

--------
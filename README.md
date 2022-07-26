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
ConnectionHandler.connect_to_suggestion()

# Similar to connect_to_suggestion(), however, returns a CSV file concerning the people's information instead of connecting
ConnectionHandler.get_suggestions()

# Fetches a specified profile(s) by their name(s) in the URL and connects to all of their connections
ConnectionHandler.connect_to_profile_connections(profile_name: Union[str, list[str]], depth=1)

# Similar to connect_to_profile_connections(), however, returns a CSV file concerning the people's information instead of connecting
ConnectionHandler.get_profile_connections(profile_name: Union[str, list[str]], depth=1)

# Retrieves all of the specified company's/companies' people, and connects to them
ConnectionHandler.connect_to_company_people(company_name: Union[str, list[str]])

# Similar to connect_to_company_people(), however, returns a CSV file concerning the people's information instead of connecting
ConnectionHandler.get_company_people(company_name: Union[str, list[str]])

# Accepts all incoming connection requests
ConnectionHandler.accept_received_invitations()

# Ignores all incoming connection requests
ConnectionHandler.ignore_received_invitations()

# Similar to accept_received_invitations() and ignore_received_invitations(), however, returns a CSV file concerning the people's information instead of accepting/ignoring
ConnectionHandler.get_received_invitations()

# Withdraws all outgoing connection requests
ConnectionHandler.withdraw_sent_invitations() # ==> Warning, LinkedIn will not permit reconnecting to the same profile for three weeks

# Similar to withdraw_sent_invitations(), however, returns a CSV file concerning the people's information instead of withdrawing
ConnectionHandler.get_sent_invitations()
```

Note that the `profile_name` argument is not the real profile name at the webpage, but rather the **user's denoted URL
profile name**, similar concept applies to `company_name`.

Disclaimer
------------

The program requires a valid username/password combination in order to function; such credentials will **NEVER** be
disclosed, stored, processed, or sent to any server/third-party provider. You can inspect the code to verify its
confidentiality level in handling such sensitive data.

LinkedIn will temporarily restrict your account if too many requests were issued in a small timeframe.

--------
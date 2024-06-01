# GroupMe Query Tool
This is a tool which will allow a user to query GroupMe messages with various search filters.

## Setup
To make use of this tool, it is necessary to first set up an API token on the [GroupMe Developer page](dev.groupme.com)

### Logging into the developer page
Log in to the page using the "Log In" button in the top right corner, and entering your email
and password for your GroupMe account.

### A note if you use a third-party app to sign in to GroupMe
If you use Facebook, Apple, Microsoft, or another login service to access your
GroupMe account, you may need to first set up a password for your account. The only way I know to do this is using
GroupMe's "Forgot password" feature. Visit the [forgot password](https://web.groupme.com/forgot_password) page, and
enter the email address associated with your account (you can find this by clicking on your profile picture in the
bottom right corner of GroupMe in the web browser, and selecting "Profile" from the resulting menu).

### Getting your API token
Once you have entered your email and password on the developer page, you may also be prompted to enter a code sent to your
SMS or email to verify your identity. Once you are successfully logged in, select "Access Token" in the top right (next to
your account name), and you will be presented with a pop-up containing a long string of characters. Copy these, and save
them somewhere secure. This is your token which grants you access to the GroupMe API. Tokens allow you to sign in to a web service,
fulfilling the role of a combined username and password. As such, they should be treated with the same security level as passwords.
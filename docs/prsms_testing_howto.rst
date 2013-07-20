===========================================================
How to test BulkSMS integration in the EMAS payment process
===========================================================

One of the payment options when ordering services or goods from Everything Maths
or Science is Premium Rated SMS (PRSMS). This howto describes the process for
testing on the quality assurance servers.


Important info
==============

    BulkSMS web admin console address
    - http://bulksms.2way.co.za/

    Username and password
    - Please contanct me for these.
    - upfronttest/ upfr0nt
    
    BulkSMS premium number
    - 08200722929001
    - Remember you cannot type this number in and send an SMS to it. You will 
    have to reply to an existing SMS sent form the BulkSMS admin console.

    BulkSMS username
    - upfront

    BulkSMS send password
    - upfronts7st3ms!

    BulkSMS sending destination URL
    - http://bulksms.2way.co.za:5567/eapi/submission/send_sms/2/2.0

    BulkSMS receive password
    - upfr0nt

    QA EMAS Siyavula username and password
    - Please contanct me for these.
   

Server configuration
====================

Configure BulkSMS test account
------------------------------
Go to http://bulksms.2way.co.za/
Login with the testing username and password
Go to "Your profile"
Check the following:
* Security answer = upfr0nt
* MO relay URL = http://qa.emas.siyavula.com/@@smspaymentapproved?password=upfr0nt
NB: PLEASE DO NOT CHANGE ANYTHING ELSE!
Make sure there are credits availble

Configures EMAS test server
---------------------------
Login to http://qa.emas.siyavula.com
Go to the control panel ("Site Setup" in the drop down)
Click on the link 'EMAS settings'
Configure the following:
* BulkSMS premium number = 08200722929001
* BulkSMS username = upfronttest
* BulkSMS send password = upfr0nt
* BulkSMS sending destination URL = http://bulksms.2way.co.za:5567/eapi/submission/send_sms/2/2.0
* BulkSMS receive password = upfr0nt


Testing steps
=============
Go to:
m.qa.everythingscience.co.za
Login
Click on 'Order'
Choose:
'Maths'
'Grade 10 (CAPS)'
'Intelligent Practice one month subscription'
'Premium SMS'
Click 'Submit'
Make a note of the order number and the verification code (normally 5 digits).

Go to: 
http://bulksms.2way.co.za/
Login with the testing username and password
Send an SMS from: https://bulksms.2way.co.za/home/compose/individual/index.mc
Reply to the SMS with the verification code

Go to:
qa.emas.siyavula.com/orders
Search for the new order by order number
Verify that this order is now in the 'Paid' state

Go to:
m.qa.everythingscience.co.za
Verify that you have access to the Grade 10 Science Intelligent Practice service

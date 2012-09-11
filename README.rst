Introduction
============

This product provides the following new content types:

Product
-------
* represents a physical product, like a textbook, sold through the
  website
* has a price attribute
* can be added in the "Products and Services" folder

Service
-------
* an online service provided through the EMAS website.
* extends Product with attributes for service type, subscription period,
  amount of credits, grade and subject.
* can be credit or subscription based.
* a credit based service specifies the amount of credits a user will
  receive when purchasing the service.
* a subscription based service specifies the period a user will access
  to the service once they purchase the service.
* can be added in the "Products and Services" folder.

MemberService
-------------
* represents the service a member has purchased.
* automatically created inside the "Member Services" folder when an
  order transitions to "paid".

Order
-----
* represents a collection of products and/or services that a user has
  ordered.
* used to create invoice and notification emails as well as settlement
  requests to Virtual Card Services.
* when an order is marked as 'paid' the relevant MemberServices are
  automatically created.
* Automatically created in the toplevel "Orders" folder when a user
  places an order.

OrderItem
---------
* a product or service a user has ordered

How to create a product
-----------------------
Log-in as a user with administrative rights.

Navigte to 'Products and Services'.

From the 'Add new' drop-down, select 'Product'.

Complete all the relevant fields and click on 'Save'.

Publish the new product by selecting 'Publish' from the 'State' drop-down.

Now navigate to '/@@purchase'.

The new product will be on the list.

How to create a serivce
-----------------------

Log-in as a user with administrative rights.

Navigte to 'Products and Services'.

From the 'Add new' drop-down, select 'Service'.

Complete all the relevant fields and click on 'Save'.

Publish the new product by selecting 'Publish' from the 'State' drop-down.

Now navigate to '/@@purchase'.

The new service will be on the list.


How it all works
----------------

Products and services are created in the special 'Products and Services' folder.

A user indicates which of these products and services he wants to purchase.

The system creates an order with orderitems for each of the selected
products and services inside the top level "Orders" folder.

Emails are sent to both the info account and the user to inform them of
the order.

If the user chooses to settle online, the order details are sent to VCS.

VCS in turn prompts the user for the relevant credit card details.

The transaction is settled by VCS and control is returned to EMAS.

If the transaction was successful the relevant MemberServices are created in
the 'Member Services' folder.

If the transaction is declined, the user is informed and nothing more happens.

The user might choose to settle via EFT. In this case the admin is responsible
for verifying that payment was made by the user and proof of payment submitted.
An admin user can then search for the order in the "Orders" folder and
transition the order to "paid" via the Plone user interface. 

The system determines access to services and products by looking at the subject
and grade of the page the user is requesting. This information is used to find
all the user's memberservices for the given page. Credit and subscription
services are treated differently. For credit based services the system allows
access if the user has credits for the service. Access to subscription based
services is controlled by the expiry date. If the system can find a
memberservice for the given subject-grade combination with an expiry
date in the future it will give the user access to the associated
service.

Example
-------

John registers as a user on everythingmaths.co.za. He purchases access
to the intelligent practice service for a month and he also purchases 20
credits for the Questions-and-Answers service. He pays by credit card
via the VCS system. After successful completion of the transaction he
browses to:
grade-10/01-algebraic-expressions/01-algebraic-expressions-01.cnxmlplus
The system computes that this is a request for a maths grade 10 page. It
uses this information to check if John has any memberservices for maths
grade 10. Upon finding 2 services, QA and Intelligent Practice, it
displays the links in the premium services area.


Installing version 1.0
----------------------

After rebuilding your instance, remove the order.js from portal_javascripts.
Then run the setup steps for the emas.app.

After installation *MAKE SURE* that the vcs_user_id is set to that of a user
with the permission to transition the order and create memberservices.

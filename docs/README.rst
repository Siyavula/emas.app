EMAS app
========

We introduced the following new content types:

Service
- a purchasable service
- can be credit or subscription based
- a credit based service allows a user access to a specific service for a set amount of times. The question-and-answer service is a credit based service.
- a subscription based service allows a users access for a set period. It has an expiry date. After this date the user no longer has access to the service. The intelligent practice service is a subscription based service.

Product
- a purchasable product

MemberService
- this represents a service (or product) that a member has purchased.
- used to determine access to products and services

Order
- represents a collection of products and/ or services that a user has ordered
- used to create invoice and notification emails as well as settlement requests to Virtual Card Services
- when an order is marked as 'payed' the relevant MemberServices are automatically created

OrderItem
- a unique product or service a user has ordered

These types of objects are contained in the following special folders:
orders
- Order (which in turn contains OrderItems)

memberservices
- MemberService

products_and_services
- Product
- Service

How to create a product
~~~~~~~~~~~~~~~~~~~~~~~

Log-in as a user with administrative rights.

Navigte to 'Products and Services'.

From the 'Add new' drop-down, select 'Product'.

Complete all the relevant fields and click on 'Save'.

Publish the new product by selecting 'Publish' from the 'State' drop-down.

Now navigate to '/@@purchase'.

The new product will be on the list.

How to create a serivce
~~~~~~~~~~~~~~~~~~~~~~~

Log-in as a user with administrative rights.

Navigte to 'Products and Services'.

From the 'Add new' drop-down, select 'Service'.

Complete all the relevant fields and click on 'Save'.

Publish the new product by selecting 'Publish' from the 'State' drop-down.

Now navigate to '/@@purchase'.

The new service will be on the list.



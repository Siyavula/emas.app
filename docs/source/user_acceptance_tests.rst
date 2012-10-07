Contents:

.. toctree::
   :maxdepth: 2

********************************
User acceptance tests: emas. app
********************************

##################
Pay by premium SMS
##################

Prerequisites
=============

Steps
-----

#. Browse to [instance]/@@order.

#. Select "Maths", "Grade 10 (CAPS)", "Intelligent Practice and a textbook."

#. Select 'Pay via Premium SMS'.

#. Click on 'submit'.

#. Verify that the you are shown a confirmation page with:
   
   the order number.

   intelligent practice for grade 10.

   textbook for maths grade 10.

#. Verify that you receive and SMS with the following details:

   the newly created order number.

   a payment verification code.

   instructions on how to proceed.

#. Reply to the SMS with the payment verification code.

#. Verify that you receive a second SMS acknowledging the payment.

#. Log in to the test instance.

#. Go to the practice service.

#. Verify that you now have access to the grade 10 practice service.

#. Navigate to [instance]/orders in the admin interface (plain, unskinned plone).

#. Validate that your newly created order has the relevant order items.


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

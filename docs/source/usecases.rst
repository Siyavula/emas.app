Contents:

.. toctree::
   :maxdepth: 2

********************
Use cases: emas. app
********************

#####################################
Order services and pay by premium SMS
#####################################

Preconditions
=============

#. The user is authenticated.

Steps
=====

#. The user browses to [instance]/@@order.

#. The system displays the current offerings.

#. The user selects the required offerings.

#. The user indicates that he wants to pay by premium SMS.

#. The user submits the form to the system.

#. The system creates a new order and fills it with the supplied details.

#. The system computes a unique 'payment verification code' for this order.

   this includes the order number and the BulkSMS password set in the registry.

#. The system instructs BulkSMS to send a verification SMS including:

   the order number.

   the payment verification code.

   instructions on how to proceed.

#. The system informs the user that a verification SMS was sent.

############################################
Handle payment approved message from BulkSMS
############################################

Preconditions
=============

#. The system has an unpaid order with the supplied order number and this order
   is has and annotation with the payment verification code.

Steps
=====

#. The system validates the password sent by BulkSMS against the one set in the
   registry.

#. The system finds the order by querying for it with the supplied order number.
   
   BulkSMS must return this as one of the GET parameters.

#. The system checks that the supplied payment verification code matches that
   sent by BulkSMS by comparing it to the one on the order annotations.
    
#. The system triggers a workflow transition to 'paid' on this order.

#. The system sends an SMS notification to the user, informing them that the
   service is now available.


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`


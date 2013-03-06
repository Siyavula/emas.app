How to update pricing information
=================================

1. First, edit the prices of the inputs on the order form
(emas/app/browser/templates/order.pt). Let's say you want to modify the
price for Intelligent Practice, search for the input matching the
service and modify the "price" attribute and the text shown to the user.
The tag looks like this::

    <input name="prod_practice_book" 
        checked=""
        tal:attributes="checked python:view.prod_practice_book_selected('Practice', selected)"
        class="no-textbook" 
        value="Practice" 
        type="radio" 
        price="150"> Intelligent Practice only (no textbook) [per subject: one year subscription <strong>R150</strong>]

2. Next, you need to update the prices on individual products and
services. Go to "Products and Services" in Plone and update the price
for the relevant services.

3. There are a few "special" services that also need to be updated that
deal with discount on orders. For example, when a client orders both a
textbook and intelligent practice for grade 10 maths, the service titled
"Maths Grade 10 Discount" will be added to the order. If no discount
should be added the order, simply change the price of discount services
to 0.

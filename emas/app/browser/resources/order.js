// local functions
function ordertotal() {
    var totalcost = 0;
    var multiplier_selector = 'input[name="subjects"]:checked';
    var multiplier = parseInt($(multiplier_selector).attr("multiplier"));
    if (isNaN(multiplier)) {
        multiplier = 1;
    }

    var price_selector = 'input[name="prod_practice_book"]:checked';
    var price = parseInt($(price_selector).attr("price"));
    if (isNaN(price)) {
        price = 0;
    }

    if (price != 0) {
        $('#totalcost').html("R"+ (multiplier * price));
    }
    else {
        $('#totalcost').html("R0");
    }
}

function hideForms() 
{
    $("#formtabs li").each(function(i){
        $(this).removeClass("formactive");
    });
    $("div.selectpackage").each(function(i){
        $(this).hide();
    });
    return false;
}

function update_action() {
    action = $('form#individual-orderform').attr('base_action');
    params = '';

    subject_selector = 'input[name="subjects"]:checked';
    subjects = $(subject_selector);
    if (subjects.length > 0) {
        params = params + 'subjects=' + subjects.val();
    }

    grade_selector = 'input[name="grade"]:checked';
    grade = $(grade_selector);
    if (grade.length > 0) {
        params = params + '&grade=' + grade.val();
    }

    prod_practice_book_selector = 'input[name="prod_practice_book"]:checked';
    prod_practice_book = $(prod_practice_book_selector);
    if (prod_practice_book.length > 0) {
        params = params + '&prod_practice_book=' + prod_practice_book.val();
    }

    prod_payment_selector = 'input[name="prod_payment"]:checked';
    prod_payment = $(prod_payment_selector);
    if (prod_payment.length > 0) {
        params = params + '&prod_payment=' + prod_payment.val();
    }

    fullname_selector = 'input[name="fullname"]';
    fullname = $(fullname_selector).val();
    if (fullname.length > 0) {
        params = params + '&fullname=' + fullname;
    }

    phone_selector = 'input[name="phone"]';
    phone = $(phone_selector).val();
    if (phone.length > 0) {
        params = params + '&phone=' + phone;
    }

    address_selector = 'textarea[name="shipping_address"]';
    address = $(address_selector).val();
    if (address.length > 0) {
        params = params + '&shipping_address=' + address;
    }

    action = action + '?' + params;
    $('form#individual-orderform').attr('action', action);
}

function checkAddressDetails() {
    result = false;
    name = ($('input[name="fullname"]').val()).length;
    phone = ($('input[name="phone"]').val()).length;
    address = ($('textarea[name="shipping_address"]').val()).length;

    if (name > 0 && phone > 0 && address > 0) {
        result = true;
    }

    return result;
}

// runs when the page is loaded
$(function($) {
    ordertotal();

    $(".selectpackage input[type='radio']").change(ordertotal);
    $(".selectpackage button[type='submit']").click(validate);

    $("#school-order-form-link").click(function() {
        hideForms();
        $(this).addClass("formactive");
        $("div#school-order-form").show();
        return false;
    });

    $("input.add-textbook").click(function (event) {
        $("div#bookonly").show(); 
    });

    $("input.no-textbook").click(function (event) {
        $("div#bookonly").hide(); 
    });

    // login form
    $('#login-links a[href$="/login"]').prepOverlay(
        {
            subtype: 'ajax',
            filter: common_content_filter,
            formselector: 'form#login_form',
            noform: function () {
                return 'redirect';
            },
            redirect: function () {
                var href = location.href;
                if (href.search(/pwreset_finish$/) >= 0) {
                    return href.slice(0, href.length-14) + 'logged_in';
                } else {
                    var form = $('form#individual-orderform');
                    $(form).unbind();
                    return $(form).attr('action');
                }
            }
        }
    );

    // registration
    $('#login-links a[href$="/@@register-from-orderform"]').prepOverlay(
        {
            subtype: 'ajax',
            filter: common_content_filter,
            formselector: 'form.kssattr-formname-register-from-orderform, form.loginform',
            noform: function () {
                return 'redirect';
            },
            redirect: function () {
                var form = $('form#individual-orderform');
                $(form).unbind();
                return $(form).attr('action');
            }
        }
    );

    var isAnon = $('input[name="isAnon"]').val();
    if (isAnon == "True") {
        $("form.update-action input[type='radio']").change(update_action);
        $("form.update-action input[type='text']").blur(update_action);
        $("form.update-action textarea").blur(update_action);
    } else {
        $("form.update-action input[type='radio']").unbind('click', update_action);
        $("form.update-action input[type='text']").unbind('blur', update_action);
        $("form.update-action textarea").unbind('blur', update_action);
    }

    book_selectors = 'input.add-textbook:checked';
    if ($(book_selectors).length > 0) {
        $('div#bookonly').show();
    }
    
    $('input[name="prod_payment"]').click(function () {
        togglePayment();
    });
    togglePayment();

});

function validate() {
    var result = true;
    var subjects = $('input[name="subjects"]:checked').val();
    var grade = $('input[name="grade"]:checked').val();
    var add_textbook = $('input.add-textbook:checked').val();
    var address_details = checkAddressDetails();
    var payment_method = $('input[name="prod_payment"]:checked').val();

    if (subjects != undefined && grade == undefined) {
        alert('You have to select a grade before you can continue');
        result = false;
    }
    if (subjects == undefined && grade != undefined) {
        alert('You have to specify which subjects you would like to subscribe to before you can continue');
        result = false;
    }
    if (subjects == undefined && grade == undefined) {
        alert('You have to select a grade and subject.');
        result = false;
    }
    if (add_textbook && grade == undefined && subjects == undefined ) {
        alert('You have to specify which subjects and which grade you would like to subscribe to before you can continue');
        result = false;
    }
    if (result == true && add_textbook != undefined && address_details == false) {
        alert('You have to supply address details.');
        result = false;
    }
    if (result == true && payment_method == undefined) {
        alert('You have to select a payment method.');
        result = false;
    }

    if (result == true && $('#totalcost').html() == "R0") {
        alert('You have to order something before you can continue');
        result = false;
    }

    if (result == true) {
        isAnon = $('input[name="isAnon"]').val();
        if (isAnon == "True") {
            alert('You have to login before you continue.');
            result = false;
        }
    }

    return result;
}

function togglePayment() {
    payment = $('input[name="prod_payment"]:checked').val();
    button_selector = 'button#confirmsubmit';
    button = $(button_selector);
    if (payment == 'creditcard') {
        $(button).show();
        $('div#bankdetails').hide();
    }
    if (payment == 'eft') {
        $(button).hide();
        $('div#bankdetails').show();
    }
}

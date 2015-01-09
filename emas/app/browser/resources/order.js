// local functions
function ordertotal() {
    var totalcost = 0;

    var price_selector = 'input[name="subjects"]:checked';
    var price = parseInt($(price_selector).attr("price"));
    if (isNaN(price)) {
        price = 0;
    }

    if (price != 0) {
        $('#totalcost').html("R"+ (price));
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

    prod_payment_selector = 'input[name="prod_payment"]:checked';
    prod_payment = $(prod_payment_selector);
    if (prod_payment.length > 0) {
        params = params + '&prod_payment=' + prod_payment.val();
    }

    action = action + '?' + params;
    $('form#individual-orderform').attr('action', action);
}

// runs when the page is loaded
$(function($) {
    ordertotal();

    $("#selectpackage input[type='radio']").change(ordertotal);
    $("#selectpackage button[name='submitorder']").click(validate);

    $("#school-order-form-link").click(function() {
        hideForms();
        $(this).addClass("formactive");
        $("div#school-order-form").show();
        return false;
    });

    // login form
    $('.login-links a[href$="/login"]').prepOverlay(
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
    $('.login-links a[href$="/@@register-from-orderform"]').prepOverlay(
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

});

function validate() {
    var result = true;
    var subjects = $('input[name="subjects"]:checked').val();
    var payment_method = $('input[name="prod_payment"]:checked').val();

    if (subjects == undefined) {
        alert('You have to specify which subjects you would like to subscribe to before you can continue');
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


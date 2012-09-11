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

// runs when the page is loaded
$(function($) {
    ordertotal();
    $("form.update-action input[type='radio']").change(update_action);
    $("form.update-action input[type='text']").blur(update_action);
    $("form.update-action textarea").blur(update_action);

    $(".selectpackage input[type='radio']").change(ordertotal);
    $(".selectpackage button[type='submit']").click(function () {
        // check if the user is logged in before we worry about anything else.
        var isAnon = $('input[name="isAnon"]').val();
        if (isAnon == "True") {
            alert('You have to login before you continue.');
            return false;
        }
        
        // user is logged in; now we check the required fields.
        result = true;
        var subjects = $('input[name="subjects"]:checked').val();
        var grade = $('input[name="grade"]:checked').val();
        var include_textbook = $('input[name="include_textbook"]:checked').val() == 'yes';
        var include_expert_answers = $('input[name="include_expert_answers"]:checked').val() == 'yes';
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
        if (include_textbook && grade == undefined && subjects == undefined ) {
            alert('You have to specify which subjects and which grade you would like to subscribe to before you can continue');
            result = false;
        }
        if (result == true && $('#totalcost').html() == "R0") {
            alert('You have to order something before you can continue');
            result = false;
        }

        return result;
    });

    $("table tr:even").css("background-color", "#ccccff");

    $("#individual-order-form-link").click(function() {
        hideForms();
        $(this).addClass( "formactive" );
        $("div#individual-order-form").show();
        return false;
    });

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
    $('#login-links a[href$="/@@register"]').prepOverlay(
        {
            subtype: 'ajax',
            filter: common_content_filter,
            formselector: 'form.kssattr-formname-register'
        }
    );

    var isAnon = $('input[name="isAnon"]').val();
    if (isAnon == "True") {
        $("form.update-action input[type='radio']").change(update_action);
    }

    $('input[name="prod_payment"]').click(function(event) {
        // show the EFT details
        if ($(this).val() == 'eft') {
            $('div#bankdetails').show();
        } else {
            $('div#bankdetails').hide();
        }
    });

    book_selectors = 'input.add-textbook:checked';
    if ($(book_selectors).length > 0) {
        $('div#bookonly').show();
    }
});

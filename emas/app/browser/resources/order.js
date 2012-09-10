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

// runs when the page is loaded
$(function($) {
    ordertotal();
    $(".selectpackage input[type='radio']").change(ordertotal);
    $(".selectpackage button[type='submit']").click(function () {
        var isAnon = $('input[name="isAnon"]').val() == 'True' && false || true;
        if (isAnon == true) {
            alert('You have to login before you continue.');
            return false;
        }

        result = true;
        var subjects = $('input[name="subjects"]:checked').val();
        var grade = $('input[name="grade"]:checked').val();
        var include_textbook = $('input[name="include_textbook"]:checked').val() == 'yes';
        var include_expert_answers = $('input[name="include_expert_answers"]:checked').val() == 'yes';
        result = true;
        if (subjects != undefined && grade == undefined) {
            alert('You have to select a grade before you can continue');
            result = false;
        }
        if (subjects == undefined && grade != undefined) {
            alert('You have to specify which subjects you would like to subscribe to before you can continue');
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
                    $(form).submit();
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

});

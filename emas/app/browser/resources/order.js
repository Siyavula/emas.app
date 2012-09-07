// local functions
function ordertotal() {
    var totalcost = 0;
    var multiplier_selector = 'input[name="practice_subjects"]:checked';
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

        var practice_subjects = $('input[name="practice_subjects"]:checked').val();
        var practice_grade = $('input[name="practice_grade"]:checked').val();
        var include_textbook = $('input[name="include_textbook"]:checked').val() == 'yes';
        var include_expert_answers = $('input[name="include_expert_answers"]:checked').val() == 'yes';
        result = true;
        if (practice_subjects != undefined && practice_grade == undefined) {
            alert('You have to select a grade before you can continue');
            result = false;
        }
        if (practice_subjects == undefined && practice_grade != undefined) {
            alert('You have to specify which subjects you would like to subscribe to before you can continue');
            result = false;
        }
        if (include_textbook && practice_grade == undefined &&
                                practice_subjects == undefined ) {
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

});

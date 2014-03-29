$(function() {
    jQuery.fn.exists = function(){return this.length>0;};
    setTimeout("next_slide()", 5000);
});

function next_slide() {
    var active = $('#iphone-overlay img.active');
    if (active.length === 0)
        active = $('#iphone-overlay img:last');
    var next = active.next().length ? active.next() : $('#iphone-overlay img:first');
    active.addClass('last-active');
    next.css({opacity: 0.0}).addClass('active').animate({opacity: 1.0}, 1500, function() {
        active.removeClass('active last-active');
    });
    setTimeout("next_slide()", 5000);
}

function loaded() {
    var lang = getParameterValue("lang");
    if (lang === "ru" || (lang === "" && String.locale === "ru")) {
        String.locale = "ru";

        $('.needBeLocal').each(function() {
            $(this).html(_($.trim($(this).text())));
        });
    }
}

var _ = function(string) {
    return string.toLocaleString();
};

function getParameterValue(parameter) {
    parameter = parameter.replace(/[\[]/, "\\\[").replace(/[\]]/, "\\\]");
    var regexS = "[\\?&]" + parameter + "=([^&#]*)";
    var regex = new RegExp(regexS);
    var results = regex.exec(window.location.href);
    if (results === null)
        return "";
    else
        return results[1];
}

function androidClick() {
    yaCounter24132985.reachGoal('google');
    $('#soon').show();
    $('#storesButtons').hide();
    $('.tab-content').css('padding-bottom', '50px');
    $('#wishes').focus();
}
function appleClick() {
    yaCounter24132985.reachGoal('apple');
    $('#soon').show();
    $('#storesButtons').hide();
    $('.tab-content').css('padding-bottom', '50px');
    $('#wishes').focus();
}

function init() {
    initSubscriptionForm();
}

function prepareTextAfterSubmition() {
    var html = '<h3 style="text-align: center;"> Спасибо за отзыв. <br/> Нам очень важно ваше мнение. <br/> Вы будете одним из первых, <br/> кто узнает о приложении.</h3>';
    $('#soon').html(html);
}

function initSubscriptionForm() {
    var applicationId = "BiixOUv8TBRRCc9PnScmyF2XMHRZhx2LfmvdqtvA";
    var javaScriptKey = "Sj5Vw02dRs3zI59caHeMQCEB9EXrNcsKPe0xkczc";
    Parse.initialize(applicationId, javaScriptKey);
    $('#submitButton').click(function() {
        subscribe();
    });
}

function validateEmail(email) {
    var re = /^(([^<>()[\]\\.,;:\s@\"]+(\.[^<>()[\]\\.,;:\s@\"]+)*)|(\".+\"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$/;
    return re.test(email);
}

function subscribe() {
    yaCounter24132985.reachGoal('submit');
    $('#submitButton').hide();
    var email = $('#email').val().trim();
    var message = $('#wishes').val().trim();
    if ((email === undefined || email === '') || (!validateEmail(email))) {
        //  alert('Email is invalid. Please try again.');
        alert('Неправильно введен адрес. Пожалуйста, попробуйте еще раз.');
        return;
    }
    var FeedbackMessage = Parse.Object.extend("FeedbackMessage");
    var feedback = new FeedbackMessage();
    feedback.set("email", email);
    feedback.set("wishes", message);
    feedback.save().then(function() {
        prepareTextAfterSubmition();
    });
}

$(function() {
    init();
});
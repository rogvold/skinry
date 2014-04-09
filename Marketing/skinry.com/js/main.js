var store;

$(function() {
    initSubscriptionForm();
    setTimeout("next_slide()", 5000);
});

function initSubscriptionForm() {
    var applicationId = "BiixOUv8TBRRCc9PnScmyF2XMHRZhx2LfmvdqtvA";
    var javaScriptKey = "Sj5Vw02dRs3zI59caHeMQCEB9EXrNcsKPe0xkczc";
    Parse.initialize(applicationId, javaScriptKey);
    $('#submitButton').click(function() {
        subscribe();
    });
}

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

function androidClick() {
    yaCounter24132985.reachGoal('google');
    store = "google";
    toSubscribe();
}

function appleClick() {
    yaCounter24132985.reachGoal('apple');
    store = "apple";
    toSubscribe();
}

function gformClick() {
    yaCounter24132985.reachGoal('googleForm');
    document.location.href = 'https://docs.google.com/forms/d/1GIetHrprmc6CQkOxr7hNtMJXNUz3GVBmbkks5mokk-w';
};

function toSubscribe() {
    $('#badges').hide();
    $('#soon').show();
    $('.tab-content').css('padding-bottom', '50px');
    $('#wishes').focus();
}

function subscribe() {
    var email = $('#email').val().trim();
    var message = $('#wishes').val().trim();
    if ((email === undefined || email === '') || (!validateEmail(email))) {
        emailAlert();
        return;
    }
    yaCounter24132985.reachGoal('submit');
    $('#soon').hide();
    var FeedbackMessage = Parse.Object.extend("FeedbackMessage");
    var feedback = new FeedbackMessage();
    feedback.set("email", email);
    feedback.set("wishes", message);
    feedback.set("store", store);
    feedback.save().then(function() {
        toThankYou();
    });
}

function validateEmail(email) {
    var re = /^(([^<>()[\]\\.,;:\s@\"]+(\.[^<>()[\]\\.,;:\s@\"]+)*)|(\".+\"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$/;
    return re.test(email);
}

function toThankYou() {
    $('#soon').hide();
    $('#thankyou').show();
}
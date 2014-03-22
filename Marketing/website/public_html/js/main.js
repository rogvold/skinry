$(function() {
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

$(function() {
    var myStream;
    var dataURL;
    
    $("#tryModal").on('shown.bs.modal', function() {
        var streaming = false,
                video = document.querySelector('#video'),
                canvas = document.querySelector('#canvas'),
                shotbutton = document.querySelector('#shotbutton'),
                retakebutton = document.querySelector('#retakebutton'),
                savebutton = document.querySelector('#savebutton'),
                width = $("#modal-try-body").width(),
                height = 0;

        navigator.getMedia = (navigator.getUserMedia ||
                navigator.webkitGetUserMedia ||
                navigator.mozGetUserMedia ||
                navigator.msGetUserMedia);

        navigator.getMedia({
            video: true,
            audio: false
        },
        function(stream) {
            if (navigator.mozGetUserMedia) {
                video.mozSrcObject = stream;
            } else {
                var vendorURL = window.URL || window.webkitURL;
                video.src = vendorURL.createObjectURL(stream);
            }
            video.play();
            myStream = stream;
        },
                function(err) {
                    console.log("An error occured! " + err);
                });

        video.addEventListener('canplay', function(ev) {
            if (!streaming) {
                height = video.videoHeight / (video.videoWidth / width);
                video.setAttribute('width', width);
                video.setAttribute('height', height);
                canvas.setAttribute('width', width);
                canvas.setAttribute('height', height);
                streaming = true;
            }
        }, false);

        function takepicture() {
            canvas.width = width;
            canvas.height = height;
            canvas.getContext('2d').drawImage(video, 0, 0, width, height);
            dataURL = canvas.toDataURL("image/png");
            dataURL.replace(/^data:image\/(png|jpg);base64,/, "");
        }

        shotbutton.addEventListener('click', function(ev) {
            takepicture();
            $("#video-group").hide();
            $("#canvas-group").show();
            ev.preventDefault();
        }, false);

        retakebutton.addEventListener('click', function(ev) {
            $("#canvas-group").hide();
            $("#video-group").show();
            ev.preventDefault();
        }, false);

        savebutton.addEventListener('click', function(ev) {
            var imgData = "{'img': '" + dataURL + "'}";
            $.ajax({
                url: 'http://5.9.107.99:5000/api/v1/',
                dataType: 'json',
                data: imgData,
                contentType : 'application/json',
                type: 'POST',
                success: function(data) {
                    console.log(data);
                }
            });
            ev.preventDefault();
        });
    });

    $("#tryModal").on('hide.bs.modal', function() {
        myStream.stop();
    });
});

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
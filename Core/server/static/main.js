var myStream, dataURL, width = 1024, height = 0;
var streaming = false;
var s_name, p_name;

$(function () {
    var applicationId = "BiixOUv8TBRRCc9PnScmyF2XMHRZhx2LfmvdqtvA";
    var javaScriptKey = "Sj5Vw02dRs3zI59caHeMQCEB9EXrNcsKPe0xkczc";
    Parse.initialize(applicationId, javaScriptKey);
    $('#submitButton').click(function () {
        sendComment();
    });
});

function runWebCam() {
    if (!streaming) {
        navigator.getMedia = (navigator.getUserMedia ||
            navigator.webkitGetUserMedia ||
            navigator.mozGetUserMedia ||
            navigator.msGetUserMedia);
        if (navigator.getMedia != undefined) {
            navigator.getMedia({
                video: true,
                audio: false
            }, function (stream) {
                if (navigator.mozGetUserMedia) {
                    video.mozSrcObject = stream;
                } else {
                    var vendorURL = window.URL || window.webkitURL;
                    video.src = vendorURL.createObjectURL(stream);
                }
                video.play();
                myStream = stream;
                $("#errormessage").hide();
                $("#video").show();
                $("#shotButton").show();
            }, function () {
                $("#video").hide();
                $("#shotButton").hide();
                $("#errormessage").show();
            });

            video.addEventListener('canplay', function () {
                if (!streaming) {
                    if (video.videoHeight != 0) {
                        height = video.videoHeight / (video.videoWidth / width);
                        video.setAttribute('width', width);
                        video.setAttribute('height', height);
                        canvas.setAttribute('width', width);
                        canvas.setAttribute('height', height);
                        console.log(width + "x" + height);
                    } else {
                        canvas.setAttribute('width', video.getAttribute('width'));
                        canvas.setAttribute('height', video.getAttribute('height'));
                        console.log("video resolution is undefined");
                    }
                    streaming = true;
                    iframeExt.update();
                    setTimeout(function () {
                        iframeExt.update();
                    }, 500);
                }
            }, false);
        } else {
            $("#video").hide();
            $("#shotButton").hide();
            $("#errormessage").show();
        }
    } else {
        video.play();
    }
}

function stopWebCam() {
    video.pause();
}

$("#imgInput").change(function () {
    readURL(this);
});

function readURL(input) {
    if (input.files && input.files[0]) {
        var reader = new FileReader();
        reader.onload = function (e) {
            uploadData = e.target.result;
            $('#preview').attr('src', uploadData);
        };
        reader.readAsDataURL(input.files[0]);
        $('#preview').show();
        $('#uploadButton').removeAttr("disabled");
    } else {
        $('#preview').hide();
        $('#uploadButton').attr("disabled", "disabled");
    }
    iframeExt.update();
}

function shotClick() {
    video.pause();
    $("#shotButtons").hide();
    $("#sendButtons").show();
    canvas.getContext('2d').drawImage(video, 0, 0, width, height);
}

function shotAgainClick() {
    video.play();
    $("#sendButtons").hide();
    $("#shotButtons").show();
}

function sendClick() {
    $('#sendButton').attr("disabled", "disabled");
    dataURL = canvas.toDataURL("image/jpeg");
    send(dataURL);
}

function uploadClick() {
    $('#uploadButton').attr("disabled", "disabled");
    send(uploadData);
}

function toUpload() {
    if ($("#preview").is(":visible")) {
        $('#uploadButton').removeAttr("disabled");
    } else {
        $('#uploadButton').attr("disabled", "disabled");
    }

    $('#resultTab').hide();
    $('#shotTab').hide();
    $("#errorTab").hide();
    $('#uploadTab').show();
    iframeExt.update();

    stopWebCam();
    $('#thankYouPanel').hide();
    $('#commentPanel').show();
    $('#email').val('');
    $('#comment').val('');
}

function toShot() {
    runWebCam();
    $("#sendButtons").hide();
    $("#shotButtons").show();

    $('#uploadTab').hide();
    $('#resultTab').hide();
    $("#errorTab").hide();
    $('#shotTab').show();
    iframeExt.update();
}

function send(imageURL) {
    var base64img = imageURL.substr(23);
    var imgData = '{"img": "\'' + base64img + '\'"}';
    $.ajax({
        url: 'api/v1/',
        dataType: 'json',
        data: imgData,
        contentType: 'application/json',
        type: 'POST',
        success: function (data) {
            console.log(data);
            showResult(data.p_name);
            s_name = data.s_name;
            p_name = data.p_name;
        },
        error: function (jqXHR) {
            showError($.parseJSON(jqXHR.responseText).error);
        }
    });
}

function showResult(imgURL) {
    $.ajax({
        url: 'api/v1/proc/' + imgURL,
        dataType: 'json',
        contentType: 'application/json',
        type: 'GET',
        success: function (data) {
            $("#result").attr('src', 'data:image/jpeg;base64,' + data.img);
            $("#pts").text(data.pts);

            $("#shotTab").hide();
            $("#uploadTab").hide();
            $("#errorTab").hide();
            $("#resultTab").show();
            iframeExt.update();

            $('#shotButton').removeAttr("disabled");
            $('#uploadButton').removeAttr("disabled");
        }
    });
}

function showError(errorText) {
    $("#shotTab").hide();
    $("#uploadTab").hide();
    $("#resultTab").hide();
    $("#errorTab").show();

    $('#shotButton').removeAttr("disabled");
    $('#uploadButton').removeAttr("disabled");
    $("#errorMsg").text(errorText);
    iframeExt.update();
}

function sendComment() {
    var email = $('#email').val().trim();
    var message = $('#comment').val().trim();
    var stars = $('.rating-input:checked ~ .rating-star').length;

    var SitePromoComment = Parse.Object.extend("SitePromoComment");
    var feedback = new SitePromoComment();
    feedback.set("email", email);
    feedback.set("comment", message);
    feedback.set("stars", stars);
    feedback.set("s_name", s_name);
    feedback.set("p_name", p_name);
    feedback.save().then(function () {
        thankYou();
    });
}

function thankYou() {
    $('#commentPanel').hide();
    $('#thankYouPanel').show();
    iframeExt.update();
}
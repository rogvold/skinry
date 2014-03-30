var iframeExt = $.iframeHeightExternal();
$("#video").resize(function() {
    iframeExt.update();
});

if (navigator.platform === 'iPad') {
    window.onorientationchange = function() {
        iframeExt.update();
    };
}

var myStream, dataURL, width = 400, height = 0;
var video = document.querySelector('#video');
var canvas = document.querySelector('#canvas');
var streaming = false;

function runWebCam() {
    if (!streaming) {
        navigator.getMedia = (navigator.getUserMedia ||
                navigator.webkitGetUserMedia ||
                navigator.mozGetUserMedia ||
                navigator.msGetUserMedia);
        navigator.getMedia({
            video: true,
            audio: false
        }, function(stream) {
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
        }, function() {
            $("#video").hide();
            $("#shotButton").hide();
            $("#errormessage").show();
        });

        video.addEventListener('canplay', function() {
            if (!streaming) {
                height = video.videoHeight / (video.videoWidth / width);
                video.setAttribute('width', width);
                video.setAttribute('height', height);
                canvas.setAttribute('width', width);
                canvas.setAttribute('height', height);
                streaming = true;
                console.log(width + "x" + height);
            }
        }, false);
    }
}

function stopWebCam() {
    video.pause();
}

$("#imgInput").change(function() {
    readURL(this);
});

function readURL(input) {
    if (input.files && input.files[0]) {
        var reader = new FileReader();
        reader.onload = function(e) {
            uploadData = e.target.result;
            $('#preview').attr('src', uploadData);
        };
        reader.readAsDataURL(input.files[0]);
        $('#preview').show();
        $('#uploadButton').removeAttr("disabled");
        iframeExt.update();
    } else {
        $('#preview').hide();
        iframeExt.update();
        $('#uploadButton').attr("disabled", "disabled");
    }
}

function shotClick() {
    video.pause();
    $("#shotButtons").hide();
    $("#sendButtons").show();
    canvas.getContext('2d').drawImage(video, 0, 0, width, height);
    ev.preventDefault();
}

function shotAgainClick() {
    video.play();
    $("#sendButtons").hide();
    $("#shotButtons").show();
    ev.preventDefault();
}

function sendClick() {
    dataURL = canvas.toDataURL("image/jpeg");
    send(dataURL);
    $('#sendButton').attr("disabled", "disabled");
    ev.preventDefault();
}

function uploadClick() {
    send(uploadData);
    $('#uploadButton').attr("disabled", "disabled");
}

function toUpload() {
    stopWebCam();
    $('#resultTab').hide();
    $('#shotTab').hide();
    $("#errorTab").hide();
    $('#uploadTab').show();
    iframeExt.update();
}

function toShot() {
    runWebCam();
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
        success: function(data) {
            console.log(data);
            showResult(data.p_name);
        },
        error: function(jqXHR) {
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
        success: function(data) {
            $("#shotTab").hide();
            $("#uploadTab").hide();
            $("#errorTab").hide();
            $("#resultTab").show();
            $('#shotButton').removeAttr("disabled");
            $('#uploadButton').removeAttr("disabled");
            $("#result").attr('src', 'data:image/jpeg;base64,' + data.img);
            $("#pts").text('Your score:' + data.pts);
            iframeExt.update();
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
var email;

$(function () {
    var applicationId = "BiixOUv8TBRRCc9PnScmyF2XMHRZhx2LfmvdqtvA";
    var javaScriptKey = "Sj5Vw02dRs3zI59caHeMQCEB9EXrNcsKPe0xkczc";
    Parse.initialize(applicationId, javaScriptKey);

    /* variables */
    var preview = $('#upl-img');
    var status = $('#upl-status');
    var percent = $('#upl-percent');
    var bar = $('#upl-bar');

    /* only for image preview */
    $("#image").change(function(){
        preview.fadeOut();
        /* html FileRender Api */
        var oFReader = new FileReader();
        oFReader.readAsDataURL(document.getElementById("image").files[0]);
        oFReader.onload = function (oFREvent) {
            preview.attr('src', oFREvent.target.result).fadeIn();
        };
    });

    /* submit form with ajax request */
    $('#image-upload-form').ajaxForm({
        /* set data type json */
        dataType: 'json',
        /* reset before submitting */
        beforeSend: function() {
            status.fadeOut();
            bar.width('0%');
            percent.html('0%');
        },
        /* progress bar call back*/
        uploadProgress: function(event, position, total, percentComplete) {
            var pVel = percentComplete + '%';
            bar.width(pVel);
            percent.html(pVel);
        },
        /* complete call back */
        complete: function(data) {
            preview.fadeOut(800);
            status.html(data.responseJSON.status).fadeIn();
        }
    });
});

function getParameterByName(name) {
    name = name.replace(/[\[]/, "\\[").replace(/[\]]/, "\\]");
    var regex = new RegExp("[\\?&]" + name + "=([^&#]*)"),
        results = regex.exec(location.search);
    return results == null ? "" : decodeURIComponent(results[1].replace(/\+/g, " "));
}

function collectShort() {
    return {
        name : $("#short-name").val(),
        email : $("#short-email").val(),
        sex : $("#short-sex").val(),
        age : $("#short-age").val(),
        complaint : $("#short-complaint").val(),
        allergy : $("#short-allergy").val(),
        previous : $("#short-previous").val()
    };
}

function collectFull() {
    return {
        name : $("#full-name").val(),
        email : $("#full-email").val(),
        sex : $("#full-sex").val(),
        day : $("#full-day").val(),
        month : $("#full-month").val(),
        year : $("#full-year").val(),
        starttime : $("#full-starttime").val(),
        cause : $("#full-cause").val(),
        drugs : $("#full-drugs").val(),
        whatworks : $("#full-whatworks").val(),
        allergy : $("#full-allergy").val(),
        illness : $("#full-illness").val(),
        illnessdrugs : $("#full-illnessdrugs").val(),
        legacy : $("#full-legacy").val()
    };
}

function submit(type, questionary) {
    var Dermatologist = Parse.Object.extend("Dermatologist");
    var query = new Parse.Query(Dermatologist);
    query.equalTo("email", questionary.email);
    query.find({
        success: function(results) {
            if (results.length == 0)
                send(type, questionary);
            else
                $('#not-unique-modal').modal("show");
        },
        error: function(error) {
            alert("Error: " + error.code + " " + error.message);
        }
    });
}

function send(type, questionary) {
    var Dermatologist = Parse.Object.extend("Dermatologist");
    var item = new Dermatologist();
    item.set("email", questionary.email);
    item.set("type", type);
    item.set("questionary", JSON.stringify(questionary));
    item.save().then(function () {
        window.location.replace("./success.html?email=" + questionary.email);
    });
}

function sendVK() {
    var Dermatologist = Parse.Object.extend("Dermatologist");
    var query = new Parse.Query(Dermatologist);
    query.equalTo("email", email);
    query.find({
        success: function(results) {
            if (results.length > 0) {
                results[0].set("vk", $("#vkid").val());
                results[0].save().then(function () {
                    $("#vk-form").html("<h4>Спасибо!</h4>");
                });
            } else
                alert("Такой email не найден");
        },
        error: function(error) {
            alert("Error: " + error.code + " " + error.message);
        }
    });
}
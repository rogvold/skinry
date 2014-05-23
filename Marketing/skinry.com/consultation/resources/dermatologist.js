var email;

$(function () {
    var applicationId = "BiixOUv8TBRRCc9PnScmyF2XMHRZhx2LfmvdqtvA";
    var javaScriptKey = "Sj5Vw02dRs3zI59caHeMQCEB9EXrNcsKPe0xkczc";
    Parse.initialize(applicationId, javaScriptKey);

    $('#short-form').submit(function (event) {
        event.preventDefault();
        submit("short", collectShort());
        return false;
    });

    $('#full-form').submit(function (event) {
        event.preventDefault();
        submit("full", collectFull());
        return false;
    });

    $('#sendButton').click(function () {
        var id = $("#qtype").children(".active").children().attr("id");

        if (id == "qshort") {
            $('#short-form').find('.sendBtn').click();
        } else if (id == "qfull") {
            $('#full-form').find('.sendBtn').click();
        }
    })
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

function collectPhotos() {
    var photos = [];

    $("#photolist").find("tbody").children().each(function() {
        var element = $(this).children()[1];
        var current = {
            path : $(element).children(".upl-hidden").text(),
            description : $(element).children(".upl-description").val()
        };
        photos.push(current);
    });

    return photos;
}

function submit(type, questionary) {
    var Dermatologist = Parse.Object.extend("Dermatologist");
    var query = new Parse.Query(Dermatologist);
    query.equalTo("email", questionary.email);
    query.find({
        success: function(results) {
            if (results.length == 0) {
                questionary.photos = collectPhotos();
                console.log(questionary);
                send(type, questionary);
            } else {
                $('#not-unique-modal').modal("show");
            }
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

function addrow() {
    var $photolist = $("#photolist");

    $photolist.append('<tr><td style="width: 130px"><div style="height: 120px; width: 120px; background-color: #eee"><img class="upl-preview" style="max-height: 120px; max-width: 120px"></td>' +
        '<td><div class="upl-progress progress active" style="margin-top: 15px">' +
        '<div class="upl-bar progress-bar" role="progressbar" aria-valuenow="45" aria-valuemin="0" aria-valuemax="100" style="width: 0; text-align: center">' +
        '0%</div></div><div class="upl-status" style="margin-top: 0; margin-bottom: 0"></div><div class="upl-hidden" style="display: none">' +
        '</div><textarea class="upl-description form-control" style="margin-top: 7px" placeholder="Описание фото">' +
        '</textarea></td><td style="width: 25px"><a href="#">x</a><form class="upl-form" action="upload.php" enctype="multipart/form-data" method="post">' +
        '<input class="upl-image" type="file" name="image" style="display: none"></form></td></tr>');

    $(".upl-image:last").change(function () {
        if (this.files && this.files[0]) {
            var oFReader = new FileReader();
            oFReader.readAsDataURL(this.files[0]);
            oFReader.onload = function (oFREvent) {
                $(".upl-preview:last").attr('src', oFREvent.target.result);
            };
            $(".upl-form:last").submit();

            $(".panel-footer a").text("Приложить еще фото");
        }
    });

    $photolist.find("a:last").click(function() {
        $(this).closest("tr").remove();
        return false;
    });

    /* variables */
    var status = $('.upl-status:last');
    var bar = $('.upl-bar:last');

    /* submit form with ajax request */
    $('.upl-form:last').ajaxForm({
        /* set data type json */
        dataType: 'json',
        /* reset before submitting */
        beforeSend: function() {
            status.fadeOut();
            bar.width('0%');
            bar.text('0%');
        },
        /* progress bar call back*/
        uploadProgress: function(event, position, total, percentComplete) {
            var pVel = percentComplete + '%';
            bar.width(pVel);
            bar.text(pVel);
        },
        /* complete call back */
        complete: function(data) {
            $(".upl-progress:last").hide();
            if (data.responseJSON.type == "SUCCESS") {
                $(".upl-hidden:last").text(data.responseJSON.path);
                status.addClass("bs-callout bs-callout-info");
                setTimeout(function() {
                    status.fadeOut();
                }, 2000);
            } else {
                status.addClass("bs-callout bs-callout-danger");
                $(".upl-description:last").hide();

            }
            status.html(data.responseJSON.status).fadeIn();
        }
    });

    $('.upl-image:last').click();
}
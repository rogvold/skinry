/**
 * Created by sabir on 09.06.14.
 */


SkinryAdminPanel = function () {
    var self = this;
    this.applicationId = "BiixOUv8TBRRCc9PnScmyF2XMHRZhx2LfmvdqtvA";
    this.javaScriptKey = "Sj5Vw02dRs3zI59caHeMQCEB9EXrNcsKPe0xkczc";
    this.usersList = [];
    this.currentUser = undefined;

    this.init = function () {
        self.adminChecking();
        moment.lang('ru');
        self.initParse();

        if (self.isAdmin()){
            self.prepareAdminPanel();
        }
    }


    this.adminChecking = function () {
        if (window.location.href.indexOf('user.html') > 0) {
            return;
        }
        var adminVal = getCookie('admin');
        var p = undefined;
        if (adminVal == undefined) {
            p = prompt('password:');
            if (p == undefined) {
                alert('empty password');
                window.location.href = window.location.href;
                return;
            } else {
                if (p == '203') {
                    setCookie('admin', '1');
                    return;
                }
                else {
                    alert('incorrect password');
                    window.location.href = window.location.href;
                    return;
                }
            }
        }
    }

    this.prepareAdminPanel = function(){
        $('#adminPanel').show();
    }

    this.isAdmin = function () {
        if (getCookie('admin') == undefined) {
            return false;
        }
        return true;
    }

    self.initParse = function () {
        Parse.initialize(self.applicationId, self.javaScriptKey);
    }

    this.loadUsers = function () {
        var Dermatologist = Parse.Object.extend("Dermatologist");
        var query = new Parse.Query(Dermatologist);
        query.limit(1000);
        query.descending("createdAt");
        self.usersList = [];
        query.find(function (results) {
            for (var i in results) {
                var u = new SkinryUser(results[i].id, results[i].get("email"));
                u.vk = results[i].get("vk");
                u.questionary = u.parseQuestionary(results[i].get("questionary"));
                u.lastNotificationTimestamp = results[i].get("lastNotificationTimestamp");
                u.createdAt = new Date(results[i].createdAt).getTime();
                u.status = results[i].get("status");
                self.usersList.push(u);
                u.printInfo();
            }
            self.createUsersTable();

        });
    }

    this.loadCurrentUser = function () {
        self.currentUser = new SkinryUser();
        self.currentUser.loadCurrentUser();
        self.initChangeStatusButton();
        self.initNotifyUserButton();
    }

    this.createUsersTable = function () {
        var s = '';
        for (var i in self.usersList) {
            s += self.usersList[i].getTableRow(self.usersList.length - i*1);
        }
        $('#usersTable').html(s);
        Cackle.bootstrap(true);
        self.initDeleteUserButton();

    }

    this.initDeleteUserButton = function () {
        $('.deleteButton').bind('click', function () {
            var userId = $(this).attr('data-id');
            if (confirm('Вы действительно хотите удалить пользователя?')) {
                self.deleteUser(userId);
            }
        });
    }

    this.initChangeStatusButton = function(){
        $('#changeStatusButton').bind('click', function(){
            var userId = gup('id');
            var newStatus = $('#statusSelect').val();
            console.log("newStatus = " + newStatus);
            self.changeStatusOfUser(userId, newStatus);
        });
    }

    this.deleteUser = function (userId) {
        if (userId == undefined) {
            alert('userId is not specified');
            return;
        }
        var Dermatologist = Parse.Object.extend("Dermatologist");
        var query = new Parse.Query(Dermatologist);
        query.limit(1);
        query.equalTo("objectId", userId);
        query.find(function (results) {
            if (results.length == 0) {
                alert('user with specified id is not found');
                return;
            }
            results[0].destroy().then(function () {
                alert('пользователь удален');
                window.location.href = window.location.href;
            });
        });
    }

    this.changeStatusOfUser = function(userId, status){
        if (status == undefined || status == ''){
            alert('new status is empty');
            return;
        }
        var Dermatologist = Parse.Object.extend("Dermatologist");
        var query = new Parse.Query(Dermatologist);
        query.limit(1);
        query.equalTo("objectId", userId);
        query.find(function (results) {
            if (results.length == 0) {
                alert('user with specified id is not found');
                return;
            }
            results[0].set("status", status);
            results[0].save().then(function(){
                alert('статус пользователя был успешно изменен');
                window.location.href = window.location.href;
            });
        });
    }

    this.initNotifyUserButton = function(){
        $('#notifyUserButton').bind('click', function(){
            var userId = gup('id');
            console.log('userId = ' + userId)
            if (userId == undefined){
                return;
            }
            var message = 'Здравствуйте! <br/>Отличная новость!<br/><br/>Дерматолог оставил Вам сообщение. Консультация доступна по этой <a href="http://skinry.com/consultation/user.html?id=' + userId + '" >ссылке</a>.';
            message+= '<br/><br/>C уважением,<br/>';
            message+= 'команда Skinry';
            self.notifyUser(userId, message);
        });
    }

    this.notifyUser = function(userId, messageHtml){
        var data = {
            userId: userId,
            messageHTML: messageHtml
        }
        Parse.Cloud.run('notifyUser', data, undefined).then(function(data){
            console.log(data);
            alert('пользователю успешно отправлено уведомление на почту');
            window.location.href = window.location.href;
        }, function(error){
            alert(error.message);
            window.location.href = window.location.href;
        });
    }


}

SkinryUser = function (id, email) {
    var self = this;
    this.id = id;
    this.email = email;
    this.vk = undefined;
    this.questionary = undefined;
    this.createdAt = undefined;
    this.status = undefined;
    this.lastNotificationTimestamp = undefined;

    this.getTableRow = function (number) {
        var name = '?';
        if (self.questionary != undefined) {
            if (self.questionary.name != undefined) {
                name = self.questionary.name;
            }
        }
        var s = '<tr>' +
            '<td>' + number + '</td>' +
            '<td><a href="user.html?id=' + self.id +'"  style="color: #3f729b; font-weight: bold;">' + name + '</a></td>' +
            '<td>' + moment(self.createdAt).format('LLL') + '</td>' +
            '<td>' + self.email + '</td>' +
            '<td>' + self.vk + '</td>' +
            '<td>' + self.status + '</td>' +
            '<td><a target="_blank" href="user.html?id=' + self.id + '" >ссылка</a></td>' +
            '<td><a style="cursor: default; text-decoration: none; color: #333; font-weight: bold; " href="user.html?id=' + self.id + '#mc-container" >link</a></td>' +
            '<td><button data-id="' + self.id + '" type="button" class="btn btn-default btn-xs btn-danger deleteButton">-</button></td>' +
            ' </tr>';
        return s;
    }


    this.parseQuestionary = function (json) {
        if (json == undefined) {
            return undefined;
        }
        return JSON.parse(json);
    }

    this.generateImagesHtml = function () {
        var s = "<table>";
        for (var i in self.questionary.photos) {
            s += '<tr><td>' + self.questionary.photos[i].description + '</td><td><a target="_blank" href="http://skinry.com/consultation/' + self.questionary.photos[i].path + '" ><img style="max-width: 600px;" src="http://skinry.com/consultation/' + self.questionary.photos[i].path + '" /></a></td></tr>'
        }
        s += '</table>';
        s = '<tr><td>фотографии</td><td>' + s + '</td></tr>';
        return s;
    }

    this.loadCurrentUser = function () {
        self.id = gup('id');
        if (self.id == undefined) {
            alert('userId is undefined');
            return;
        }

        var Dermatologist = Parse.Object.extend("Dermatologist");
        var query = new Parse.Query(Dermatologist);
        query.limit(1);
        query.equalTo("objectId", self.id);

        self.usersList = [];
        query.find(function (results) {
            if (results.length == 0) {
                alert('user with specified id is not found');
                return;
            }
            self.email = results[0].get("email");
            self.vk = results[0].get("vk");
            self.status = results[0].get("status");
            self.questionary = self.parseQuestionary(results[0].get("questionary"));
            self.lastNotificationTimestamp = results[0].get("lastNotificationTimestamp");
            self.prepareQuestionaryHtml();
            console.log(self);
        });

    }

    this.prepareQuestionaryHtml = function () {
        if (self.questionary == undefined) {
            return;
        }
        var s = '<table class="table table-bordered" >';
        s += self.generateQuestionaryFieldHtml("Ф.И.О", self.questionary.name);
        s += self.generateQuestionaryFieldHtml("email", self.questionary.email);
        s += self.generateQuestionaryFieldHtml("vk.com", self.vk);
        s += self.generateQuestionaryFieldHtml("пол", self.questionary.sex);
        s += self.generateQuestionaryFieldHtml("Время начала заболеваний", self.questionary.starttime);
        s += self.generateQuestionaryFieldHtml("Связываете ли вы с чем-нибудь появление высыпаний?", self.questionary.cause);
        s += self.generateQuestionaryFieldHtml("Какими средствами уже пользовались/пользуетесь?", self.questionary.drugs);
        s += self.generateQuestionaryFieldHtml("Что из средств помогало/помогает (если пользуетесь чем-либо самостоятельно)?", self.questionary.whatworks);
        s += self.generateQuestionaryFieldHtml("Есть ли у вас аллергия (если есть, то на что и как проявляется. ЭТО ВАЖНО!)?", self.questionary.allergy);
        s += self.generateQuestionaryFieldHtml("Есть ли у Вас еще какие-нибудь заболевания (проблемы с желудком, кишечником, сахарный диабет и так далее. Если сами точно не знаете - спросите у родителей. ЭТО ВАЖНО!)?", self.questionary.illness);
        s += self.generateQuestionaryFieldHtml("Принимаете ли вы какие-нибудь препараты по сопутствующим заболеваниям (ЭТО ВАЖНО!)?", self.questionary.illnessdrugs);
        s += self.generateQuestionaryFieldHtml("Были ли у ваших родителей такие высыпания на лице в молодости?", self.questionary.legacy);
        s += self.generateImagesHtml();
        s += '</table>';
        $('#questionaryBlock').html(s);
        if (self.lastNotificationTimestamp!=undefined){
            $('#lastNotificationDate').text(moment(self.lastNotificationTimestamp).format('LLL'));
        }

        setSelectOption('statusSelect', self.status);
    }

    this.generateQuestionaryFieldHtml = function (name, value) {
        if (value == undefined) {
            value = '<small>не указано</small>';
        }

        var s = '<tr><td>' + name + '</td><td>' + value + '</td></tr>';
        return s;
    }

    this.printInfo = function () {
        console.log(self);
    }


}

function gup(name) {
    name = name.replace(/[\[]/, "\\\[").replace(/[\]]/, "\\\]");
    var regexS = "[\\?&]" + name + "=([^&#]*)";
    var regex = new RegExp(regexS);
    var results = regex.exec(window.location.href);
    if (results == null)    return "";
    else    return results[1];
}

function isFunction(functionToCheck) {
    var getType = {};
    return functionToCheck && getType.toString.call(functionToCheck) === '[object Function]';
}


function setSelectOption(selectId, value){
    $('#' + selectId).val(value);
}
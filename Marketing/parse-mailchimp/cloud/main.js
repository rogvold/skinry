Parse.Cloud.afterSave('FeedbackMessage', function(request) {
	var api_key = "beef95fba78590a4994cb80e9b18c715-us3";

	// use https and last verison
	var options = {secure: true, version: "1.3"};

	var module_path = "cloud/libs/mailchimp/";

	var MailChimpAPI = require(module_path+"MailChimpAPI.js");
	var myChimp = new MailChimpAPI(api_key, options, module_path); 

	myChimp.listSubscribe({
		id : "863ab13bb2",
		email_address : request.object.get("email"),
		double_optin : false,
		send_welcome : false
	}, {
		success: function(httpResponse) 
		{
			console.log('Pusher Success!!');
			console.log(request.object.get("email"));


			console.log(httpResponse.text);
		},
		error: function(httpResponse) 
		{
			console.log('Pusher Error!');

			console.error('Request failed with response code ' + httpResponse.status);
			console.log(httpResponse.text);
		}
	});
});


Parse.Cloud.define("list", function(request, response) {
	var query = new Parse.Query("FeedbackMessage");
	query.limit(200);
	query.find({
		success: function(results) {    
			response.success(results);   
		},
		error: function(){
			response.error("failed to get a respose");
		}   
	});
});

Parse.Cloud.define("addItem", function(request, response) {
	var api_key = "beef95fba78590a4994cb80e9b18c715-us3";

	// use https and last verison
	var options = {secure: true, version: "1.3"};

	var module_path = "cloud/libs/mailchimp/";

	var MailChimpAPI = require(module_path+"MailChimpAPI.js");
	var myChimp = new MailChimpAPI(api_key, options, module_path); 

	var query = new Parse.Query("FeedbackMessage");
	query.equalTo("email", request.params.email);
	query.find({
		success: function(results) {    
			var count = 0;

			for(var i = 0; i < results.length; i++) {
				myChimp.listSubscribe({
					id : "863ab13bb2",
					email_address : results[i].get("email"),
					double_optin : false,
					send_welcome : false,
					update_existing : true
				}, {
					success: function(httpResponse) {
						console.log("success: " + results[i].get("email") + " " + httpResponse.text);
					},
					error: function(httpResponse) {
						console.log("error: " + results[i].get("email") + " " + httpResponse.text);
					}
				});
				count += 1;
			}     
			response.success(count);   
		},
		error: function(){
			response.error("failed to get a respose");
		}   
	});
});

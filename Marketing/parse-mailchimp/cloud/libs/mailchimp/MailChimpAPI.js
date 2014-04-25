/**
 * Inspired from https://github.com/gomfunkel/node-mailchimp
 * Added compatibility for Parse Request by vfloz
 * For icangowithout	
 */
 var _execute = function (method, availableParams, givenParams, callback) {

 	var finalParams = { apikey : this.apiKey };
 	var currentParam;

 	for (var i = 0; i < availableParams.length; i++) {
 		currentParam = availableParams[i];
 		if (typeof givenParams[currentParam] !== 'undefined')
 			finalParams[currentParam] = givenParams[currentParam];
 	}

 	var ops = {
 		url : this.httpUri+'/'+this.version+'/',
 		method: 'POST',
 		params:  { method : method },
 		headers : { 'User-Agent' : 'Parse Cloud HttpRequest parse-mailchimp/1.0', 'Content-Type':'application/json'},
 		body : finalParams
 	};

 	if (typeof callback === 'function') {
 		var _callback = function(httpResponse){
 			if (httpResponse.error) {
 				callback(error);
 			}else{
 				var response = httpResponse.response;
 				if (!response) {
 					response = httpResponse.text;
 				}
 				callback(null, response);
 			}
 		};
 		ops.success = _callback;
 		ops.error = _callback;
 	}else if(typeof callback === 'object'){
 		ops.success = callback.success;
 		ops.error = callback.error;
 	}

 	Parse.Cloud.httpRequest(ops);

 };

/**
 * Returns a MailChimp API wrapper object of the specified version. All API 
 * versions available at the time of writing (1.1, 1.2 and 1.3) are supported.
 * 
 * Available options are:
 *  - version   The API version to use (1.1, 1.2 or 1.3). Defaults to 1.3.
 *  - secure    Whether or not to use secure connections over HTTPS 
 *              (true/false). Defaults to false.
 * 
 * @param apiKey The API key to access the MailChimp API with
 * @param options Configuration options as described above
 * @return Instance of the MailChimp API in the specified version
 */
 function MailChimpAPI (apiKey, options, modulePath) {

 	if (!options){
 		options = {};
 	}

 	if (!apiKey){
 		throw new Error('You have to provide an API key for this to work.');
 	}

 	if(!modulePath){
 		modulePath = 'cloud/libs/mailchimp/';
 	}

 	if (modulePath.charAt(modulePath.length-1) !== '/') {
 		modulePath = modulePath+"/";
 	}

 	var apiFile;
 	if (!options.version || options.version == '1.3')
 		apiFile = 'MailChimpAPI_v1_3.js';
 	else if (options.version == '1.2')
 		apiFile = 'MailChimpAPI_v1_2.js';
 	else if (options.version == '1.1')
 		apiFile = 'MailChimpAPI_v1_1.js';
 	else
 		throw new Error('Version ' + options.version + ' of the MailChimp API is currently not supported.');


 	var _MailChimpAPI = require(modulePath+'lib/'+apiFile);
 	_MailChimpAPI.prototype.execute = _execute;

 	return new _MailChimpAPI(apiKey, options);
 }

 module.exports = MailChimpAPI;





//alert("connection lib loaded!");
define(
	function()
{
	function sendAjax(requestData, func, errorFunc)
	{
		requestData['timeout'] = 5000;
		var jAjaxRequest = $.ajax(requestData);
		jAjaxRequest.fail(function(request, errorstate, errormsg){
			console.log("error:"+errormsg);
			if(errorFunc!=null)
				errorFunc(errormsg);
		});
		jAjaxRequest.done(func);
	}

	getMessagesFromUser = function(userID, offset, func, errorFunc)
	{
		var theurl = "/messages/author/"+userID;

		if(offset==null)
			offset = 0;
		var serverdata = {offset:offset};

		sendAjax({
			url:theurl, 
			data:serverdata,
			type:'POST'
		}, func, errorFunc);
	}

	getMessagesForUser = function(userID, offset, func, errorFunc)
	{
		var theurl = "/messages/"+userID;

		if(offset==null)
			offset = 0;
		var serverdata = {offset:offset};

		sendAjax({
			url:theurl, 
			data:serverdata,
			type:'POST'
		}, func, errorFunc);
	}

	followUser = function(userID, func, errorFunc)
	{
		var theurl = "/account/follow/"+userID;
		var serverdata = {};

		sendAjax({
			url:theurl, 
			data:serverdata
		}, func, errorFunc);
	}

	getMessageWithId = function(msgID, offset, func, errorFunc)
	{
		var theurl = "/messages/"+msgID;

		if(offset==null)
			offset = 0;
		var serverdata = {offset:offset};

		sendAjax({
			url:theurl, 
			data:serverdata,
			type:'POST'
		}, func, errorFunc);
	}

	getAnswersTo = function(msgID, offset, func, errorFunc)
	{
		var theurl = "/messages/answers/"+msgID;

		if(offset==null)
			offset = 0;
		var serverdata = {offset:offset};

		sendAjax({
			url:theurl, 
			data:serverdata,
			type:'POST'
		}, func, errorFunc);
	}

	getAnswerForm = function(formdata, func, errorFunc)
	{
		request = {
			url:"/answer/"
		};
		if(null!=formdata)
		{
			request['data'] = formdata;
			request['type'] = "POST";
		}
		sendAjax(request, func, errorFunc);
	}

	deleteMessageWithId = function(msgID, func, errorFunc)
	{
		var theurl = "/messages/delete/"+msgID;
		var serverdata = {};

		sendAjax({
			url:theurl, 
			data:serverdata
		}, func, errorFunc);
	}

	getEvaluationImage = function(msgID, func, errorFunc)
	{
		sendAjax({
			url:"/media/eval/"+msgID, 
			data:{}
		}, func, errorFunc);
	}

	sendEvaluation = function(msgID, evalList, func, errorFunc)
	{
		sendAjax({
			url:"/messages/evaluate/"+msgID,
			data:evalList,
			type:'POST'
		}, func, errorFunc);
	}

	getNotificationCount = function(func)
	{
		sendAjax({
			url:"/notifications/json/",
		}, func, errorFunc);
	}

	return this;
});
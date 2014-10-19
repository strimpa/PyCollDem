
//alert("connection lib loaded!");
define(
	function()
{
	function sendAjax(requestData, func)
	{
		var jAjaxRequest = $.ajax(requestData);
		jAjaxRequest.fail(function(request, errorstate, errormsg){
			console.log("error:"+errormsg);
		});
		jAjaxRequest.done(func);
	}

	getMessagesFromUser = function(userID, func)
	{
		var theurl = "/messages/author/"+userID;
		var serverdata = {};

		sendAjax({
			url:theurl, 
			data:serverdata
		}, func);
	}

	getMessagesForUser = function(userID, func)
	{
		var theurl = "/messages/"+userID;
		var serverdata = {};

		sendAjax({
			url:theurl, 
			data:serverdata
		}, func);
	}

	followUser = function(userID, func)
	{
		var theurl = "/account/follow/"+userID;
		var serverdata = {};

		sendAjax({
			url:theurl, 
			data:serverdata
		}, func);
	}

	getMessageWithId = function(msgID, func)
	{
		var theurl = "/messages/"+msgID;
		var serverdata = {};

		sendAjax({
			url:theurl, 
			data:serverdata
		}, func);
	}

	getAnswerTo = function(msgID, func)
	{
		var theurl = "/messages/answer/"+msgID;
		var serverdata = {};

		sendAjax({
			url:theurl, 
			data:serverdata
		}, func);
	}

	getAnswerForm = function(func, formdata)
	{
		request = {
			url:"/answer/"
		};
		if(null!=formdata)
		{
			request['data'] = formdata;
			request['type'] = "POST";
		}
		sendAjax(request, func);
	}

	deleteMessageWithId = function(msgID, func)
	{
		var theurl = "/messages/delete/"+msgID;
		var serverdata = {};

		sendAjax({
			url:theurl, 
			data:serverdata
		}, func);
	}

	getEvaluationImage = function(msgID, func)
	{
		sendAjax({
			url:"/media/eval/"+msgID, 
			data:{}
		}, func);
	}

	sendEvaluation = function(msgID, evalList, func)
	{
		sendAjax({
			url:"/messages/evaluate/"+msgID,
			data:evalList,
			type:'POST'
		}, func);
	}

	return this;
});
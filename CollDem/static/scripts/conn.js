
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

	getMessagesFromUser = function(userID, offset, func)
	{
		var theurl = "/messages/author/"+userID;

		if(offset==null)
			offset = 0;
		var serverdata = {offset:offset};

		sendAjax({
			url:theurl, 
			data:serverdata,
			type:'POST'
		}, func);
	}

	getMessagesForUser = function(userID, offset, func)
	{
		var theurl = "/messages/"+userID;

		if(offset==null)
			offset = 0;
		var serverdata = {offset:offset};

		sendAjax({
			url:theurl, 
			data:serverdata,
			type:'POST'
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

	getMessageWithId = function(msgID, offset, func)
	{
		var theurl = "/messages/"+msgID;

		if(offset==null)
			offset = 0;
		var serverdata = {offset:offset};

		sendAjax({
			url:theurl, 
			data:serverdata,
			type:'POST'
		}, func);
	}

	getAnswersTo = function(msgID, offset, func)
	{
		var theurl = "/messages/answers/"+msgID;

		if(offset==null)
			offset = 0;
		var serverdata = {offset:offset};

		sendAjax({
			url:theurl, 
			data:serverdata,
			type:'POST'
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


require.config({
	baseUrl: '/static/scripts/',
	paths: {
		jquery: 'lib/jquery-2.1.1',
		jqueryui: 'lib/jquery-ui.min',
		snap:'lib/snap.svg-min',
		sylvester:'lib/sylvester',
		jCookie:'lib/jquery.cookie',
		underscore:'lib/underscore-min'
	}
});

$ = require(
	['jquery', 'conn', 'ui', 'jqueryui'], function($, conn, ui)
{
	///////////////////////////////////////////////////////////////////////
	// globals
	///////////////////////////////////////////////////////////////////////
	// constants
	var max_depth = 1;
	var csrftoken = $.cookie('csrftoken');
	// jquery extensions
	$.exists = function(selector){return ($(selector).length > 0);}


	function renderAnswers(msgID, answerHolder, depth)
	{
		var listID = "answers_"+msgID;
		if($.exists("#"+listID))
		{
			$("#"+listID).animate({height:"0px"}, 500, function(){
				$("#"+listID).remove();
			});
		}
		else
		{
			var answerListHolder = ui.div(answerHolder, {renderBorder:false, id:listID });
			function endFunc(datalength)
			{
				ui.insertAnswerCount(msgID, datalength);
			}
			renderMsgCB(conn.getAnswersTo, msgID, endFunc, answerListHolder, depth+1);
		}
	}

	function renderAnswerForm(msgID, answerHolder)
	{
		var replyID = "replyForm_"+msgID;
		if($.exists("#"+replyID))
		{
			$("#"+replyID).animate({height:"0px"}, 500, function(){
				$("#"+replyID).remove();
			});
		}
		else
		{
			var answerReplyHolder = ui.div(answerHolder, {renderBorder:false, id:replyID, prepend:true });
			conn.getAnswerForm(function(result)
			{
				var answerForm = ui.renderAnswerForm(answerReplyHolder, result);
				answerForm.find("input[value=submit]").click(function(result){
					answerSubmitCB(result, this, msgID);
				});
			});
		}
	}

	function renderMsg(parent, msg, depth)
	{
		var heightBeforeFill = parent.css("height");

		var msgID = msg['id'];
		var msgHolder = ui.div(parent, {renderBorder:true, id:"msgHolder"});
		var msgDiv = ui.renderMessage(msgHolder, msg);//, depth>0);
		var answerHolder = ui.div(msgHolder, {renderBorder:false, boxDisplay:true, id:"answerHolder"});

		if(depth<max_depth)
		{
			renderAnswers(msgID, answerHolder, depth);
		}
		else
		{
			var offset = 0;
			conn.getAnswersTo(msgID, offset, function(result){
				ui.insertAnswerCount(msgID, result.length);
			});
		}

		msgDiv.find("#expand").click(function(result){
			renderAnswers(msgID, answerHolder, depth);
		});
		msgDiv.find("#reply").click(function(result){
			renderAnswerForm(msgID, answerHolder);
		});
		msgDiv.find("#delete").click(function(result){
			ui.querybox("You sure?", function(){
				var parentAnswerCount = 0;
				var parentAnswerBox = parent.parents(".answerBox").first();
				var parentMsgId = parentAnswerBox.prev().attr("message_id");
				console.log("parent msg id:"+parentMsgId);
				conn.deleteMessageWithId(msgID, function(result){
					renderAnswers(parentMsgId, parentAnswerBox, depth-1, parentAnswerCount);
				})
			});
		});
		msgDiv.find("#evaluation").each(function(){
			var msgEvalDiv = $(this);
			//conn.getEvaluationImage(msgID, function(result){
				ui.renderEvaluationImage(msgEvalDiv, msg['evaluation'], msgID, conn);
			//})
		});
	}

	///////////////////////////////////////////////////////////////////////
	// callbacks
	///////////////////////////////////////////////////////////////////////

	function answerSubmitCB(result, button, msgID)
	{
		var form = $(button).parent();
		var textVal = $(form).find("#id_text").val();
		var visVal = $(form).find("#id_visibility").val();
		var csrfVal = $(form).find("input[name=csrfmiddlewaretoken]").val();
		formData = {
			'msgID'					: msgID,
			'text'					: textVal,
			'visibility'			: visVal,
			'csrfmiddlewaretoken'	: csrfVal
		};

		var answerDiv = form.parents(".answerBox").first();

		conn.getAnswerForm(function(result)
		{
			answerDiv.empty();
			renderAnswers(msgID, answerDiv, 1);
		}, formData);
	}

	function renderMsgCB(querySetFunc, param, endFunc, parent, depth, currentLimit)
	{
		if(depth==null)
			depth = 0

		if(null==currentLimit)
			currentLimit= 0;

		var completeDataLength = 0;

		querySetFunc(param, currentLimit, function(result){

			for(msgIndex in result)
			{
				var msg = result[msgIndex];
				if('completeDataLength' in msg)
				{ 
					completeDataLength = parseInt(msg['completeDataLength'])
				}
				renderMsg(parent, msg, depth);
			}

			if(endFunc != null)
				endFunc(completeDataLength);

			var newOffset = currentLimit+result.length;
			if(completeDataLength>newOffset)
			{
				var loadButton = ui.renderLoadButton(parent, newOffset);
				loadButton.click(function(result){
					renderMsgCB(querySetFunc, param, endFunc, parent, depth, newOffset);
					loadButton.remove();
				});
			}
		});
	}

	///////////////////////////////////////////////////////////////////////
	// startup triggers
	///////////////////////////////////////////////////////////////////////
	function csrfSafeMethod(method) {
		// these HTTP methods do not require CSRF protection
		return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
	}
	$.ajaxSetup({
		beforeSend: function(xhr, settings) {
			if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
				xhr.setRequestHeader("X-CSRFToken", csrftoken);
			}
		}
	});

	var messages = $("#messages");
	if(messages.length)
	{
		console.log("messages:"+messages);
		var querySetFunc = conn.getMessagesForUser;
		var param = userID;
		var depth = 0;
		if(undefined!=urlMsgId && ""!=urlMsgId)
		{
			querySetFunc = conn.getMessageWithId;
			param = urlMsgId;
		}
		renderMsgCB(querySetFunc, param, null, messages);
	}

	//Control event handler setups

	$("#followButton").each(function(){
		button = $(this);
		console.log("found a button!"+button);
		button.click(function(){
			clicked_button = $(this);
			clicked_button.val("please wait...");
			clicked_button.attr("enabled", "false");

			var userToFollow = clicked_button.attr("userid");
			conn.followUser(userToFollow, function(result){
				clicked_button.val("Unfollow");
				clicked_button.attr("enabled", "true");
			});
		});
	});

	$("#notificationCount").each(function(){
		var noteDiv = $(this);
		conn.getNotificationCount(function(result){
			console.log(result);
			if(result!="user not authenticated")
			{
				var newNotifications = 0;
				for (var i = result.length - 1; i >= 0; i--) {
					if('new' in result[i])
						newNotifications++;
				};
				if(newNotifications>0)
					renderUpdateCircle(noteDiv, newNotifications);
			}
		});
	});

	$(function(){
		var messageDrawerState = true;
		$("#createMessage").css("height", "0px");
		$("#createMessageExpand").click(function(){
			if(messageDrawerState)
				$("#createMessage").animate({height: "200px"}, 300);
			else
				$("#createMessage").animate({height: "0px"}, 300);
			messageDrawerState = !messageDrawerState;
		});
	})

	$.assocArraySize = function(obj) {
	    // http://stackoverflow.com/a/6700/11236
	    var size = 0, key;
	    for (key in obj) {
	        if (obj.hasOwnProperty(key)) size++;
	    }
	    return size;
	};

	return $;
});
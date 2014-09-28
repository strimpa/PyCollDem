

require.config({
	baseUrl: '/static/scripts/',
	paths: {
		jquery: 'lib/jquery-2.1.1',
		jqueryui: 'lib/jquery-ui.min',
		snap:'lib/snap.svg'
	}
});

$ = require(
	['jquery', 'conn', 'ui'], function($, conn, ui)
{
	///////////////////////////////////////////////////////////////////////
	// globals
	///////////////////////////////////////////////////////////////////////
	// constants
	var max_depth = 2;
	// jquery extensions
	$.exists = function(selector){return ($(selector).length > 0);}


	function renderAnswers(msgID, answerHolder, depth, myAnswerCount)
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
			conn.getAnswerTo(msgID, function(result){
				renderMsgCB(result, answerListHolder, depth+1, myAnswerCount);
				ui.insertAnswerCount(msgID, myAnswerCount.local);
			});
		}
	}

	function renderAnswerForm(msgID, answerHolder)
	{
		var replyID = "replyForm_"+msgID;
		if($.exists("#"+replyID))
		{
			$("#"+replyID).remove();
		}
		else
		{
			var answerReplyHolder = ui.div(answerHolder, {renderBorder:false, id:replyID });
			conn.getAnswerForm(function(result)
			{
				var answerForm = ui.renderAnswerForm(answerReplyHolder, result);
				answerForm.find("input[value=submit]").click(function(result){
					answerSubmitCB(result, this, msgID);
				});
			});
		}
	}

	function countAnswers(result, answerCount)
	{
		var myAnswerCount = {'local':0, 'global':0};
		answerCount.local = 0;
		for(msgIndex in result)
		{
			var msg = result[msgIndex];
			var msgID = msg['id'];
			conn.getAnswerTo(msgID, function(result){
				countAnswers(result, myAnswerCount);
				if(undefined!=answerCount)
					answerCount.global += myAnswerCount.local;
			});
			answerCount.local++;
		}
	}

	function renderMsg(parent, msg, depth, myAnswerCount)
	{
		var msgID = msg['id'];
		var msgHolder = ui.div(parent, {renderBorder:false, id:"msgHolder"});
		var msgDiv = ui.renderMessage(msgHolder, msg, depth>0);
		var answerHolder = ui.div(msgHolder, {renderBorder:false, boxDisplay:true, id:"answerHolder"});

		if(depth<max_depth)
		{
			renderAnswers(msgID, answerHolder, depth, myAnswerCount);
		}
		else
		{
			var answerCB = function(result){
				countAnswers(result, myAnswerCount);
				ui.insertAnswerCount(msgID, myAnswerCount.local);
			};
			conn.getAnswerTo(msgID, answerCB);
		}

		msgDiv.find("#expand").click(function(result){
			renderAnswers(msgID, answerHolder, depth, myAnswerCount);
		});
		msgDiv.find("#reply").click(function(result){
			renderAnswerForm(msgID, answerHolder);
		});
		msgDiv.find("#delete").click(function(result){
			ui.querybox("You sure?", function(){
				var parentAnswerCount = {'local':0, 'global':0};
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
				ui.renderEvaluationImage(msgEvalDiv, msg['evaluation']);
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

		var myAnswerCount = {'local':0, 'global':0};
		var answerDiv = form.parents(".answerBox").first();

		conn.getAnswerForm(function(result)
		{
			answerDiv.empty();
			renderAnswers(msgID, answerDiv, 1, myAnswerCount);
		}, formData);
	}

	function renderMsgCB(result, parent, depth=0, answerCount=undefined)
	{
		var myAnswerCount = {'local':0, 'global':0};

		if(result.length<=0)
			parent.append("No answers.");

		if(undefined!=answerCount)
			answerCount.local = 0;

		for(msgIndex in result)
		{
			var msg = result[msgIndex];
			renderMsg(parent, msg, depth, myAnswerCount);
			if(undefined!=answerCount)
				answerCount.local ++;
		}

		if(undefined!=answerCount)
			answerCount.global += myAnswerCount.global;
	}

	///////////////////////////////////////////////////////////////////////
	// startup triggers
	///////////////////////////////////////////////////////////////////////

	var messages = $("#messages");
	if(messages.length)
	{
		console.log("messages:"+messages);
		if(undefined!=urlMsgId && ""!=urlMsgId)
		{
			conn.getMessageWithId(urlMsgId, function(result){
				renderMsgCB(result, messages);
			});
		}
		else
		{
			conn.getMessagesForUser(userID, function(result){
				renderMsgCB(result, messages);
			});
		}
	}

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

	return $;
});
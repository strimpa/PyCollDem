define(
	['jqueryui', 'jCookie', 'EvaluationSvg'], function(jui, jCookie, evalImage)
{
	// helpers


	// public functions 
	renderMessage = function(parentNode, msg, isAnswer)
	{
		var messageDiv = div(parentNode, {id:("message_"+msg['id'])});
		messageDiv.attr("message_id", msg['id']);

		// right aligned things
		messageDiv.append("<div class='msgUserInfoGroup innerContentBorder'><img class='msgPic' src="+msg.avatar+" /> <br /><a href='/profile/"+msg.author+"'>"+msg.author+"</a></div>");
		messageDiv.append("<div class='evaluationGroup innerContentBorder'><span id='evaluation' /><div id='evalLabel_"+msg['id']+"'></div>");
		
		// message content
		var table = $("<table/>");
		table.append("<tr><td><strong><a href='/"+msg['id']+"'>"+msg.header+"</a></strong></td></tr>");
		table.append("<tr><td>"+msg.text+"</td></tr>");
		var answerActions = $("<p id='answerActions'><a id='expand'><span id='msgAnswerCountDiv'/> answers</a> | <a id='reply'>Reply</a>");
		if(msg['can_delete'])
			answerActions.append(" | <a id='delete'>Delete</a></p>");

		table.append($("<tr/>").append($("<td/>").append(answerActions)));

		messageDiv.append(table);

		// style things
		var classString = "messageDimensions innerContentBorder";
		if(isAnswer==true)
			classString += " answerDiv ";
		messageDiv.attr("class", classString);
		messageDiv.append("<p style='clear:both;'/>");

		// getting height, setting to 0 and then expandding and deleting.
		var height = messageDiv.css("height");
		messageDiv.css("height", "0px");
		messageDiv.animate({height:height}, 300, "swing", function(){
			messageDiv.css("height", "auto")
		});			

		return messageDiv;
	}

	renderAnswerForm = function(parentNode, answerHtml)
	{
		var formDiv = $(answerHtml);
		parentNode.append(formDiv);
		return formDiv;
	}

	insertAnswerCount = function(msgID, answerCount)
	{
		var msgHeaderDiv = $("#message_"+msgID+" #msgAnswerCountDiv");
		msgHeaderDiv.text(answerCount);
	}

	div = function(parentNode, params)
	{
		var theDiv = $("<div />");
		if(parentNode!=null)
			if(true==params.prepend)
				parentNode.prepend(theDiv);
			else
				parentNode.append(theDiv);
		var classString = "messageDimensions";
		if(null!=params)
		{
			if(undefined!=params.id)
				theDiv.attr("id", params.id);
			if(true==params.renderBorder && !answerLine)
				classString += " innerContentBorder";
			if(true==params.boxDisplay)
				classString += " answerBox";
			if(true==params.answerLine)
				classString += " answerDiv";
		}
		theDiv.attr("class", classString);
		return theDiv;
	}

	br = function(parentNode, clearFloat)
	{
		var br = $("<br />");
		parentNode.append(br);
		if(clearFloat==true)
			br.css("clear", "both");
	}

	querybox = function(question, confirmFunc)
	{
		var dialogDiv = $("#dialogDummy");
		dialogDiv.text(question);
		dialogDiv.dialog({
//			dialogClass: "no-close",
			buttons:
			{
				"OK": function(res){confirmFunc(this);$(this).dialog("close");},
				Cancel:function(res){$(this).dialog("close");}
			}
		})
	}

	renderEvaluationImage = function(parent, evalObj, msgID, conn)
	{
		var image = evalImage.CreateEvaluationImage(evalObj, msgID, conn);
		parent.append(image.node);
	}

	return this;
});
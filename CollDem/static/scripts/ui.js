define(
	['jqueryui', 'jCookie', 'EvaluationSvg', 'snap'], function(jui, jCookie, evalImage, snap)
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
		messageDiv.append("<p><strong><a href='/"+msg['id']+"'>"+msg.header+"</a></strong></p>");
		messageDiv.append("<p>"+msg.text+"</p>");
		
		var answerActions = $("<p id='answerActions'><a id='expand'><span id='msgAnswerCountDiv'/> answers</a> | <a id='reply'>Reply</a>");
		if(msg['can_delete'])
			answerActions.append(" | <a id='delete'>Delete</a></p>");

		messageDiv.append(answerActions);

		// style things
		var classString = "messageDimensions";
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

	renderLoadButton = function(parentNode, offset)
	{
		var button = $("<input type='button' id='loadbutton' value='Load more messages >>' />");
		parentNode.append(button);
		return button;
	}

	renderAnswerForm = function(parentNode, answerHtml)
	{
		var formDiv = $(answerHtml);
		parentNode.append(formDiv);

		// getting height, setting to 0 and then expandding and deleting.
		var height = formDiv.css("height");
		formDiv.css("height", "0px");
		formDiv.animate({height:height}, 300, "swing", function(){
			formDiv.css("height", "auto")
		});			

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
			if(true==params.renderBorder)
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

	renderUpdateCircle = function(parent, numberUpdates)
	{
		var canvas = Snap(15,15);
		var circle = canvas.circle(7,7,7);
		circle.attr({
			    fill: "#d00",
			    stroke: "none",
			    strokeWidth: 0
			});
		var text = canvas.text(2,10,numberUpdates);
		parent.append(canvas.node);
	}

	return this;
});
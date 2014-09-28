define(
	['jqueryui', 'snap'], function(jui, snap)
{
	renderMessage = function(parentNode, msg, isAnswer=false)
	{
		var messageDiv = div(parentNode, {id:("message_"+msg['id'])});
		messageDiv.attr("message_id", msg['id']);
		messageDiv.append("<div class='msgUserInfo'><img class='msgPic' src="+msg.avatar+" /> <strong><a href='/profile/"+msg.author+"'>"+msg.author+"</a></strong><br /><span id='evaluation' /></div>");
		messageDiv.append("<p><strong><a href='/"+msg['id']+"'>"+msg.header+"</a></strong></p>");
		messageDiv.append("<p>"+msg.text+"</p>");
		var answerActions = $("<p id='answerActions'><a id='expand'><span id='msgAnswerCountDiv'/> answers</a> | <a id='reply'>Reply</a>");
		if(msg['can_delete'])
			answerActions.append(" | <a id='delete'>Delete</a></p>");
		messageDiv.append(answerActions);
		var classString = "contentField messageDimensions";
		if(isAnswer)
			classString += " answerDiv";
		else
			classString += " innerContentBorder";
		messageDiv.attr("class", classString);
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

	div = function(parentNode=undefined, params=undefined)
	{
		var theDiv = $("<div />");
		if(parentNode!=undefined)
			parentNode.append(theDiv);
		var classString = "contentField messageDimensions";
		if(undefined!=params)
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

	br = function(parentNode, clearFloat=false)
	{
		var br = $("<br />");
		parentNode.append(br);
		if(clearFloat)
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

	renderEvaluationImage = function(parent, evalObj)
	{
		parent.empty();
		var totalWidth = 50;
		var halfWidth = 25;
		var s = Snap(totalWidth, totalWidth);
		var numEvaluations = evalObj.length>3 ? evalObj.length : 3;
		var innerRadius = 3;
		var outerRadius = 25;
		var step = (2 * Math.PI) / numEvaluations;
		var innerpolys = [];
		var outerpolys = [];
		for (var i=0;i<numEvaluations;i++) {
			var x = Math.sin(i * step);
			var y = Math.cos(i * step);
			innerpolys.push(halfWidth + x *innerRadius);
			innerpolys.push(halfWidth - y *innerRadius);
			outerpolys.push(halfWidth + x *outerRadius);
			outerpolys.push(halfWidth - y *outerRadius);
		};
		console.log("outerpolys:"+outerpolys);
		var lowerRange = s.polygon(innerpolys);
		lowerRange.attr({
		    fill: "#666",
		    stroke: "none",
		    strokeWidth: 5
		});
		var highRange = s.polygon(outerpolys);
		highRange.attr({
		    fill: "none",
		    stroke: "#666",
		    strokeWidth: 2
		});
		parent.append(s.node);
	}

	renderEvaluationTool = function(parent, evalObj)
	{
		
	}

	return this;
});
define(
	['jqueryui', 'jCookie', 'EvaluationSvg', 'snap', 'tagit'], function(jui, jCookie, evalImage, snap, tagit)
{
	// helpers


	// public functions 
	renderMessage = function(parentNode, msg, isAnswer)
	{
		var messageDiv = div(parentNode, {id:("message_"+msg['id'])});
		messageDiv.attr("message_id", msg['id']);

		// right aligned things
		messageDiv.append("<div class='msgUserInfoGroup innerContentBorder'><img class='msgPic' src="+msg.avatar+" /> <br /><a href='/profile/"+msg.author+"'>"+msg.author+"</a></div>");
		var evalGroup = $("<div class='evaluationGroup innerContentBorder' />");
		messageDiv.append(evalGroup);
		
		// message content
		messageDiv.append("<p><strong><a href='/"+msg['id']+"'>"+msg.header+"</a></strong></p>");
		if('twitter_id' in msg)
		{
			console.log("adding "+msg['twitter_id']+".");
			if(	window['twttr'] != undefined && 
				twttr.widgets!=null)
			{
				var tweetWrapID = ("tweetWrap_"+msg['id']);
				var tweetWrap = div(messageDiv, {id:tweetWrapID});
				promise = twttr.widgets.createTweet(
						msg['twitter_id'],
						document.getElementById(tweetWrapID)
					);
				promise.then(function(){
					console.log("tweet "+msg['twitter_id']+" added!");
				});
				promise.catch(function(reason){
					alert("error:"+reason);
				});
			}
			else
			{
				messageDiv.append("<p class='errorMsg'>Error loading twitter widgets!</p>");
			}
		}
		else
		{			
			messageDiv.append("<p>"+msg.text+"</p>");
		}		
		var answerActions = $("<p id='answerActions'><a id='expand'><span id='msgAnswerCountDiv'/> answers</a> | <a id='reply'>Reply</a>");
		if(msg['is_author'])
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

	renderEvaluation = function(parent, msg, conn)
	{
		var evalObj = msg['evaluation'];
		var msgID = msg['id']
		parent.empty();

		var msgEvalDiv = $("<span id='evaluation' />");
		var image = evalImage.CreateEvaluationImage(evalObj, msgID, conn);
		msgEvalDiv.append(image.node);
		parent.append(msgEvalDiv);

		// evaluation controls
		var isAuthor = msg['is_author']
		if(isAuthor)
		{
			var button = $("<input type='button' id='evalAdjust' value='keywords' />");
			parent.append(button);
			button.click(function(){
				var dialogDiv = $("#dialogDummy");
				var keyWorkString = evalObj['keywords'].join();
				var tagField = $("<input type='text' id='keytags' value='"+keyWorkString+"' />");
				dialogDiv.html(tagField);
				tagField.tagit();
				dialogDiv.dialog({
					buttons:
					{
						"OK": function(res){
							var assignedTags = tagField.tagit("assignedTags");
							console.log(this.evalDiv);
							var data = {};
							for(t in assignedTags)
								data[assignedTags[t]] = 10.0;
							conn.setMsgKeywords(msgID, data, function(result){
								renderEvaluation(parent, result, conn);
							});
							$(this).dialog("close");
						},
						Cancel:function(res){$(this).dialog("close");}
					}
				});
			});
		}
		else
			parent.append("<div id='evalLabel_"+msgID+"' />");
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
		if(numberUpdates>9)
		{
			canvas.image("static/images/full.gif", 3,4,8,8);
		}
		else
		{
			var text = canvas.text(6,11,numberUpdates);
			text.attr({
	//		  fontFamily: 'Source Sans Pro',
			  fontSize: 9,
			  textAnchor: 'middle'
			});
		}
		parent.append(canvas.node);
	}

	return this;
});
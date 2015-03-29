define(["snap", 'sylvester', 'underscore'], function(snap)
{
	// constants
	//const evalLabels = ['HELPFUL', 'FUNNY', 'INSPIRATIONAL'];

	//types

	function EvaluationSvg(evalObj, msgID, conn)
	{
		//////////////////////////////////////////////////
		// definitions
		var totalWidth = 50;
		var halfWidth = 25;
		var minRadius = 5;
		var neutralRadius = 15;
		var outerRadius = 25;

		var handleRadius = 3;
		var handleDiameter = 10;

		var toolLineAttr = {
			    fill: "none",
			    stroke: "#9B7",
			    strokeWidth: 1
			};
		var toolHandleSensorAttrs = {
				    fill: "#000",
				    "fill-opacity": 0,
				    stroke: "none",
				    strokeWidth: 1
				};
		var toolHandleAttrs = {
				    fill: "#FFF",
				    stroke: "#765",
				    strokeWidth: 1
				};

		/////////////////////////////////////////////////////
		// instance vars

		var directions = [];
		var handles = [];
		var evalList = {};
		var canvas = Snap(totalWidth, totalWidth);
		var summaryGroup = canvas.group();
		var lineGroup = canvas.group();
		var gripGroup = canvas.group();
		var keywords = [];
		var currEvalObj = null;

		var thisCallbackTarget = this;

		// private heelpers 

		var calcDirections = function()
		{
			directions = [];
			var numSteps = keywords.length;
			var step = (2 * Math.PI) / numSteps;
			var i=0;
			for (key in keywords) {
				var x =  Math.sin(i * step);
				var y = - Math.cos(i * step);
				directions.push($V([x,y]).toUnitVector());
				i++;
			}
		}

		function renderPolygon(radius, group, attrs, useOffsets, useUserOffsets)
		{
			var vertices = [];
			var returnArray = [];
			var step = (2 * Math.PI) / directions.length;
			for(var i=0;i<keywords.length;i++) {
				var keyword = keywords[i];
				var userOffset = 0;
				if(useOffsets!=false)
				{
					if(useUserOffsets==true)
					{
						if(keyword in evalObj['activeUserEvaluation'])
							userOffset = evalObj['activeUserEvaluation'][keyword];
					}
					else
					{
						if(keyword in currEvalObj)
							userOffset = currEvalObj[keyword];
					}
				}
				var factor = userOffset + radius;
				var x = halfWidth + factor * directions[i].elements[0];
				var y = halfWidth + factor * directions[i].elements[1];
				vertices.push(x);
				vertices.push(y);
				returnArray.push({'x':x, 'y':y, 'offset':userOffset});
			};
			var poly = canvas.polygon(vertices);
			poly.attr(attrs);
			if(null!=group)
			{
				group.add(poly);
			}
			return returnArray;
		}


		// event callbacks
		var updateLines = function(result)
		{
			var newVertices = [];
			for (var i = 0; i < handles.length; i++) {
				var handle = handles[i];
				var vert = handle.node.getBBox();
				var trans = handle.node.getCTM();
				var new_x = vert.x + vert.width/2 + trans.e;
				var new_y = vert.y + vert.height/2 + trans.f;
				//console.log("new_x:"+new_x+", new_y:"+new_y);
				newVertices.push(new_x);
				newVertices.push(new_y);
			};
			$(lineGroup.node).empty();
			var poly = canvas.polygon(newVertices);
			poly.attr(toolLineAttr);
			lineGroup.add(poly);
		}

		// constructor 

		var updateSummaryGroup = function()
		{
			$(summaryGroup.node).empty();
			renderPolygon(neutralRadius, summaryGroup, {
			    fill: "#999",
			    stroke: "#666",
			    strokeWidth: 1
			});
			var maxverts = renderPolygon(outerRadius, summaryGroup, {
			    fill: "none",
			    stroke: "#000",
			    strokeWidth: 0.5
			}, false);
			var minverts = renderPolygon(minRadius, summaryGroup, {
			    fill: "#000",
			    stroke: "none",
			}, false);
			for(vi in maxverts)
			{
				var line = canvas.line(minverts[vi].x, minverts[vi].y, maxverts[vi].x, maxverts[vi].y);
				line.attr({
				    fill: "none",
				    stroke: "#666",
				    strokeWidth: 0.2
				});
				summaryGroup.add(line);
			}
		}

		updateToolGroup = function(canEvaluate)
		{
			var vertices = renderPolygon(neutralRadius, lineGroup, toolLineAttr, true, true);
			var userEvaluation = evalObj['activeUserEvaluation'];
			for (var i = 0; i < directions.length; i++) {
				var handleGroup = canvas.group();
				handleGroup.myDir = directions[i];
				handleGroup.label = keywords[i];
				handleGroup.lastPos = vertices[i].offset;
				handleGroup.myTool = thisCallbackTarget;

				var handleSensor = canvas.circle(vertices[i].x, vertices[i].y, 6);
				handleSensor.attr(toolHandleSensorAttrs);
				if(canEvaluate)
				{				
					var handle = canvas.circle(vertices[i].x, vertices[i].y, 0);
					handle.attr(toolHandleAttrs);
					handleGroup.add(handle);
					handles.push(handle);
				}				
				handleGroup.add(handleSensor);

				var handleID = msgID+"_"+handleGroup.label;
				$(handle).attr("id", handleID);

				var labelField = $("<div>"+handleGroup.label+"</div>");
				$("body").append(labelField);
				labelField.attr("class", "evalLabel");
				//handleGroup.add(canvas.text(vertices[i].x+5, vertices[i].y, handleGroup.label));

				gripGroup.add(handleGroup);

				moveFn = function(dx, dy, x, y){
					var userDir = $V([dx, dy]);
					this.scalar = userDir.dot(this.myDir);
					var globalPos= this.lastPos + this.scalar;
					if(globalPos < -10)
						this.scalar  -= (globalPos + 10);
					if(globalPos > 5)
						this.scalar  -= (globalPos - 5);

					var offsetString = (this.origTransform ? "T" : "t") + (this.myDir.x(this.scalar)).elements;
					this.attr({
						transform: this.origTransform + offsetString
					});
					updateLines();
				};
				startFn = function(x, y, e){
					this.origTransform = this.transform().local;
				};
				endFn = function(e)
				{
					this.lastPos = evalList[this.label] = this.lastPos + this.scalar;
					var handleTool = thisCallbackTarget;
					conn.sendEvaluation(msgID, evalList, this.myTool.reset);
				};
				handleGroup.drag(moveFn, startFn, endFn);
				handleSensor.label = labelField;
				handleSensor.hover(
					function(){
//						console.log(this);
						var theHandle = $(this.node);
						var pos = theHandle.position();
						this.label.css("top", pos.top);
						this.label.css("left", pos.left+handleDiameter);
						this.label.css("width", "auto");
						var actualWidth = this.label.css("width");
						this.label.css("width", "0px");
						this.label.css("visibility", "visible");
						this.label.animate({"width": actualWidth}, 300);
					},
					function(){
						//var myLabel = $("#evalLabel_"+msgID);
						//myLabel.animate({"color": "rgba(0,0,0,0)"}, 1000);
						console.log("deleted label");
						this.label.animate({"width": "0px"}, 300, function(){$(this).css("visibility", "hidden");});
						//myLabel.text("");
					}
				);
			};
		}

		this.reset = function(evalObj)
		{
			currEvalObj = evalObj['summary'];
			keywords = evalObj['keywords'];
			calcDirections();
			updateSummaryGroup();
		}

		/////////////////////////////////////////

		this.reset(evalObj);

		var canEvaluate = 'can_evaluate' in evalObj && evalObj['can_evaluate'];
		updateToolGroup(canEvaluate);

		canvas.hover(
			function(){
				for (var i = 0; i < handles.length; i++) {
					if(!handles[i].inAnim().anim)
						handles[i].animate({
							r:handleRadius,
							opacity:1
						}, 1000, mina.elastic);
				}
			},
			function(){
				for (var i = 0; i < handles.length; i++) {
					if(!handles[i].inAnim().anim)
						handles[i].animate({
							r:0,
							opacity:0
						}, 1000, mina.linear);
				}
			}
		);	

		return canvas;
	}

	/////////////////////////////////////////////////////////////////
	// public interface	
	CreateEvaluationImage = function(evalObj, msgID, conn){
		return new EvaluationSvg(evalObj, msgID, conn);
	};

	return this;
})
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

		var toolLineAttr = {
			    fill: "none",
			    stroke: "#9B7",
			    strokeWidth: 1
			};
		var toolHandleAttrs = {
				    fill: "#FFF",
				    stroke: "#9B7",
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
			    fill: "#666",
			    stroke: "none",
			    strokeWidth: 5
			});
			renderPolygon(outerRadius, summaryGroup, {
			    fill: "none",
			    stroke: "#000",
			    strokeWidth: 0.5
			}, false);
			renderPolygon(minRadius, summaryGroup, {
			    fill: "#000",
			    stroke: "none",
			}, false);
		}

		updateToolGroup = function()
		{
			var vertices = renderPolygon(neutralRadius, lineGroup, toolLineAttr, true, true);
			var userEvaluation = evalObj['activeUserEvaluation'];
			for (var i = 0; i < directions.length; i++) {
				var handleGroup = canvas.group();
				var handle = canvas.circle(vertices[i].x, vertices[i].y, 0);
				handle.attr(toolHandleAttrs);
				handle.myDir = directions[i];
				handle.label = keywords[i];
				handle.lastPos = vertices[i].offset;
				handle.myTool = thisCallbackTarget;
//				handleGroup.add(handle);
//				handleGroup.add(canvas.text(x+5, y, handle.label));
				gripGroup.add(handle);
				handles.push(handle);

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
				handle.drag(moveFn, startFn, endFn);
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

		if('can_evaluate' in evalObj && evalObj['can_evaluate'])
			updateToolGroup();

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
function convertToDate(timeStamp) {
		var ts = String(timeStamp);
		// Format: YYYY-MM-DD HH:MM:SS
		var string_split = ts.split(" ");
		var date_part = string_split[0].split("-");
		var time_part = string_split[1].split(":");
		return new Date(date_part[0], date_part[1], date_part[2], time_part[0], time_part[1], time_part[2]);
}

function drawLine(chartJSONData, gameShortName, valueString) {
		console.log("Drawing a chart with data:")
		console.log(chartJSONData);

		google.charts.load('current', {packages: ['corechart', 'line'], 'callback': function() {
				var data = new google.visualization.DataTable();

				convertedData = [];
				$.each(chartJSONData, function( index, value ) {
						convertedData.push([convertToDate(value[0]), value[1]]);
				});
				console.log(convertedData);

				data.addColumn('date', 'timestamps');
				data.addColumn('number', 'viewers');
				data.addRows(convertedData);
				data.sort([{column: 0}, {column: 1}]);

				chartContainerWidth = $('#' + gameShortName + '-average-viewers-graph').width();

				var options = {
						title: valueString + ' over time',
						width: chartContainerWidth - 20,
						height: 400,
		        legend: {
		            position: 'bottom'
		        },
					  hAxis: {
					     title: 'Stream Times'
					  },
					  vAxis: {
					      title: valueString
					  }
				};

				var chart = new google.visualization.LineChart(document.getElementById(gameShortName + '-average-viewers-graph'));

				chart.draw(data, options);
		}});
}

function drawCharts(streamerName) {
		console.log("Drawing charts");
		$.ajax({
        url: "/api/v1/streamer/" + streamerName,
        success: function(receivedData) {
            jsonData = JSON.parse(receivedData);
            drawLine(jsonData['ED']['viewers_average'], 'ED', 'Average Viewers');
			  }
    });
}


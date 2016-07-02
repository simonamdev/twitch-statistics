function convertToDate(timeStamp) {
		var ts = String(timeStamp);
		// Format: YYYY-MM-DD HH:MM:SS
		var string_split = ts.split(" ");
		var date_part = string_split[0].split("-");
		var time_part = string_split[1].split(":");
		return new Date(date_part[0], date_part[1], date_part[2], time_part[0], time_part[1], time_part[2]);
}

function drawViewersChart(rowData, gameShortName) {
		console.log("Drawing viewers chart for: " + gameShortName);
		// Create the data table
		var data = new google.visualization.DataTable();
		data.addColumn('string', 'name');
		data.addColumn('number', 'viewers');
		data.addRows(rowData);
		var columnWidth = $('#' + gameShortName + '-followers-graph').width();
		// Set options
		var options = {
				title: 'Average Viewers over time',
				width: columnWidth,
				height: 400
		};

		// Instantiate and draw the chart
		var chart = new google.visualization.LineChart(document.getElementById(gameShortName + '-average-viewers-graph'));
		chart.draw(data, options);
}

function drawFollowersChart(rowData, gameShortName) {
		console.log("Drawing followers chart for: " + gameShortName);
		// Create the data table
		var data = new google.visualization.DataTable();
		data.addColumn('string', 'Topping');
		data.addColumn('number', 'Slices');
		data.addRows(rowData);
		var columnWidth = $('#' + gameShortName + '-followers-graph').width();
		// Set options
			var options = {
					title: 'Followers over time',
					width: columnWidth,
					height: 400
			};

		// Instantiate and draw the chart
		var chart = new google.visualization.LineChart(document.getElementById(gameShortName + '-followers-graph'));
		chart.draw(data, options);
}

// Draw all the charts
function drawCharts(streamer_name) {
		// Make an AJAX call to get the data from the API
		$.ajax({
				url: "/api/v1/streamer/" + streamer_name,
				success: function(data) {
						jsonData = JSON.parse(data);
						console.log("Data received from API:");
						console.log(jsonData);
						for (var key in jsonData) {
								if (key == 'streamer_name') {
										continue;
								}
								if (!$.isEmptyObject(jsonData[key])) {
										drawViewersChart(jsonData[key]['viewers_average'], key);
										drawFollowersChart(jsonData[key]['followers'], key);
								}
						}
				}
		});
}

function loadCharts(streamer_name) {
		// Load packages required
		google.charts.load('current', {'packages':['corechart', 'line']});
		// Set Callbacks
		google.charts.setOnLoadCallback(function() {
				drawCharts(streamer_name);
		});
}

function convertToDate(timeStamp) {
		var ts = String(timeStamp);
		// Format: YYYY-MM-DD HH:MM:SS
		var string_split = ts.split(" ");
		var date_part = string_split[0].split("-");
		var time_part = string_split[1].split(":");
		return new Date(date_part[0], date_part[1], date_part[2], time_part[0], time_part[1], time_part[2]);
}

function drawViewersChart() {
		// Create the data table
		var data = new google.visualization.DataTable();
		data.addColumn('string', 'name');
		data.addColumn('number', 'viewers');
		data.addRows([
		  ['Mushrooms', 1],
		  ['Onions', 1],
		  ['Olives', 2],
		  ['Zucchini', 2],
		  ['Pepperoni', 1]
		]);

		// Set options
		var options = {
				title: 'Average Viewers over time',
				width: 400,
				height: 300
		};

		// Instantiate and draw the chart
		var chart = new google.visualization.LineChart(document.getElementById('ED-average-viewers-graph'));
		chart.draw(data, options);
}

function drawFollowersChart() {
  // Create the data table
  var data = new google.visualization.DataTable();
  data.addColumn('string', 'Topping');
  data.addColumn('number', 'Slices');
  data.addRows([
    ['Mushrooms', 2],
    ['Onions', 2],
    ['Olives', 2],
    ['Zucchini', 0],
    ['Pepperoni', 3]
  ]);

  // Set options
		var options = {
				title: 'Followers over time',
				width: 400,
				height: 300
		};

  // Instantiate and draw the chart
  var chart = new google.visualization.LineChart(document.getElementById('ED-followers-graph'));
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
						drawViewersChart();
						drawFollowersChart();
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

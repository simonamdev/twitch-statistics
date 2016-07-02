function convertToDate(timeStamp) {
		var ts = String(timeStamp);
		// Format: YYYY-MM-DD HH:MM:SS
		var string_split = ts.split(" ");
		var date_part = string_split[0].split("-");
		var time_part = string_split[1].split(":");
		return new Date(date_part[0], date_part[1], date_part[2], time_part[0], time_part[1], time_part[2]);
}

// Load packages required
google.charts.load('current', {'packages':['corechart', 'line']});

// Set Callbacks
google.charts.setOnLoadCallback(drawViewersChart);
google.charts.setOnLoadCallback(drawFollowersChart);

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

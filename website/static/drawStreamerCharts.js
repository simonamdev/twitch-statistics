function convertToDate(timeStamp) {
		var ts = String(timeStamp);
		// Format: YYYY-MM-DD HH:MM:SS
		var string_split = ts.split(" ");
		var date_part = string_split[0].split("-");
		var time_part = string_split[1].split(":");
		return new Date(date_part[0], date_part[1], date_part[2], time_part[0], time_part[1], time_part[2]);
}

// Load Charts and the corechart package.
google.charts.load('current', {'packages':['corechart', 'line']});

// Draw the pie chart for Sarah's pizza when Charts is loaded.
google.charts.setOnLoadCallback(drawSarahChart);

// Draw the pie chart for the Anthony's pizza when Charts is loaded.
google.charts.setOnLoadCallback(drawAnthonyChart);

// Callback that draws the pie chart for Sarah's pizza.
function drawSarahChart() {

  // Create the data table for Sarah's pizza.
  var data = new google.visualization.DataTable();
  data.addColumn('string', 'Topping');
  data.addColumn('number', 'Slices');
  data.addRows([
    ['Mushrooms', 1],
    ['Onions', 1],
    ['Olives', 2],
    ['Zucchini', 2],
    ['Pepperoni', 1]
  ]);

  // Set options for Sarah's pie chart.
  var options = {title:'How Much Pizza Sarah Ate Last Night',
                 width:400,
                 height:300};

  // Instantiate and draw the chart for Sarah's pizza.
  var chart = new google.visualization.PieChart(document.getElementById('Sarah_chart_div'));
  chart.draw(data, options);
}

// Callback that draws the pie chart for Anthony's pizza.
function drawAnthonyChart() {

  // Create the data table for Anthony's pizza.
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

  // Set options for Anthony's pie chart.
  var options = {title:'How Much Pizza Anthony Ate Last Night',
                 width:400,
                 height:300};

  // Instantiate and draw the chart for Anthony's pizza.
  var chart = new google.visualization.PieChart(document.getElementById('Anthony_chart_div'));
  chart.draw(data, options);
}

// profitability.js
// Copyright (c) 2019 Nicholas Saparoff, Phenome Project / MinerMedic
//
// Profitability processing functions for MinerMedic


// -----------------------------------------------------
// VARS needed for the profitability page

var query_data_columns = 'power_used+power_used_cost+coin+coin_cost+coin_mined+coin_purchase_cost+profitability+profitable+algo';

// hardcoded for this MinerMedic
var datamodel_name = 'CRYPTO_MINER';

var columns_costs = ["power_used_cost","coin_purchase_cost"];
var columns_profitability  = ["profitability"];
var selection_type = 0;
var series_data_columns  = columns_costs;

// -----------------------------------------------------

// currency SYMBOL
var currency_symb = "$"

// 3 == RAW Data - Last Hour
var period_type = 6;
var period_text = "Month";

// chosen from dropdowns
var series_index_columns = "NONE";

// chosen from dropdowns
var series_groupby_text = "Miner";

// the color list
var bar_colors = ["#98abc5", "#8a89a6"]; // , "#7b6888", "#6b486b", "#a05d56", "#d0743c", "#ff8c00"]

// init some vars for later use
var json_data = null;
var keys = null;
var indices = null;
var chart_objs = null;


function build_plot_title() {
	
	if (selection_type == 0) {
		selection_txt = "Cost";
	} else {
		selection_txt = "Profitability";
	}
	
	plot_title = series_groupby_text + " - " + selection_txt + " Per " + period_text;
}

function changed_data_type(selection) {

	selection_type = selection;

	if (selection==0) {
		// costs
		series_data_columns  = columns_costs;
	} else {
		// profits
		series_data_columns  = columns_profitability;
	}

	build_plot_title();
	reload_data();
	
}

function changed_period_type(period) {

	period_type = period;
	
	if (period==2) {
		period_text="Minute";
	} else if (period==3) {
		period_text="Hour";
	} else if (period==4) {
		period_text="Day";
	} else if (period==5) {
		period_text="Week";
	} else if (period==6) {
		period_text="Month";
	}
	
	build_plot_title();
	reload_data();

}

function changed_groupby_columns(groupby_text, columns) {

	series_index_columns = columns;
	series_groupby_text = groupby_text;
	
	build_plot_title();
	reload_data();	

}

function reload_data() {

	// build the URL
	var url = '/api/v1/get_datamodel_aggregated_data/'
			+ datamodel_name + '/'
			+ period_type + '/'
			+ series_index_columns + '/'
			+ encodeURIComponent(query_data_columns);

	// remove any previous chart
	svg = d3.select("svg")
	if (svg != null) {
		svg.selectAll("*").remove();
		svg.remove();
	}

	// remove any previous "VIS" html
	var chartDiv = document.getElementById("vis");
	chartDiv.innerHTML = ""
	
	// now call the URL again and build the chart
		
	d3.json(url, function(json) {

		if (json!=null) {
		
			result_count = json['data'][0]['info']['result_count'];
			keys = json['data'][0]['keys'];

			if (keys == undefined) {
				key_count = 0;
			} else {
				key_count = Object.keys(keys).length;
			}
			
			if (key_count>0) {
			
				// there are multiple "keys" to display
				// must do it with barchart or grid
				build_barchart(json);
				
			} else if (result_count > 0) {
			
				// there is only a non-indexed aggregated result
				build_status(json);

			} else {
				// not sure what else would be here
			}
			
		} else {
			
			if (series_index_columns == 'NONE') {
				build_no_result('', true);
			} else {
				build_no_result('There are no results for the selection.', false);
			}
			
		}

	}); // end of d3.json(...)

}

function build_status(json) {

	json_data = json['data'][0]['results']
	estimated = json['data'][0]['info']['estimated']
	
	if (estimated) {
		var profitability = Math.round(( ((json_data['profitability']['mean'])-1) *100));
		var power_spend = json_data['power_used_cost']['sum'];
		var savings = json_data['coin_purchase_cost']['sum'] - power_spend;
	} else {
		var profitability = Math.round(( ((json_data['profitability'])-1) *100));
		var power_spend = json_data['power_used_cost'];
		var savings = json_data['coin_purchase_cost'] - power_spend;
	}
	
	power_spend = Math.round(power_spend * 100) / 100;
	savings = Math.round(savings * 100) / 100;
	
	var result = "<table id='infotable' class='infotable text-muted'>";

	explain_period = "<div style='margin-top:-5px; font-size:14px;'>Per " + period_text + "</div>"
	result = result + "<tr><td>TOTAL COST</td><td><h3><span class='badge badge-info'>$" + power_spend + "</span></h3>" + explain_period + "</td></tr>"

	if (profitability>0) {
		result = result + "<tr><td>TOTAL SAVINGS</td><td><h3><span class='badge badge-success'>$" + savings + "</span></h3>" + explain_period + "</td></tr>"
		explain = "<div style='margin-top:-5px; font-size:14px;'>" + profitability + "% better than buying crypto-currency alone</div>"
		result = result + "<tr><td>PROFITABILITY</td><td><h3><span class='badge badge-success'>" + profitability + "%</span></h3>" + explain + "</td></tr>"
	} else {
		result = result + "<tr><td>TOTAL LOSS</td><td><h3><span class='badge badge-danger'>$" + savings + "</span></h3>" + explain_period + "</td></tr>"
		explain = "<div style='margin-top:-5px; font-size:14px;'>" + profitability + "% worse than just buying crypto-currency alone</div>"
		result = result + "<tr><td>PROFITABILITY</td><td><h3><span class='badge badge-warning'>" + profitability + "%</span></h3>" + explain + "</td></tr>"
	}

	result = result + "</table>";
	
	write_results(result);
	
}

function build_barchart(json) {

	// build the barchart
	chart_objs = buildPlot(json, series_data_columns, plot_title, bar_colors);
	
}

// FOR PROFITABILITY LABELS
function __add_text_labels(json_data, key, d, text_label_value, set_bar_class) {

	// first set the original value
	return_value = {"value": json_data[key][d]};

	// now we add some more information	
	return_value['text_label'] = text_label_value;
	return_value['class'] = 'bar_text';
	
	if (set_bar_class) {
		if (json_data['power_used_cost'][d] > json_data['coin_purchase_cost'][d]) {
			// not good...
			return_value['class'] = "bar_text_bad";
		} else {
			return_value['class'] = "bar_text_good";
		}
	}
									
	console.log('keys_map->' + json_data[key] + ":" + json_data[key][d]);
	return {key: key, value: return_value}; 


}

// FOR PROFITABILITY LABELS
function __add_text_labels_profitability(json_data, key, d) {

	// get the profitability value
	profitability = Math.round(( ((json_data['profitability'][d])-1) *100)) + "%";

	return __add_text_labels(json_data, key, d, profitability, true);

}	

// FOR COST LABELS
function __add_text_labels_cost(json_data, key, d) {

	// get the cost
	cost = currency_symb + " " + (Math.round(json_data[key][d] * 100) / 100);

	return __add_text_labels(json_data, key, d, cost, (key == 'power_used_cost'));

}
	

// FOR PROFITABILITY / BAR-CHART
function add_text_labels(json_data, key, d) {

	// handle profitability (single bar) with another method
	if (key == 'profitability') {
		return 	__add_text_labels_profitability(json_data, key, d);
	} else {
		return 	__add_text_labels_cost(json_data, key, d);
	}

}

function build_tooltip(json_data, key, d) {

	// d is the index grouping of the data
	// key is the variable for the bar being returned

	profitability = Math.round(( ((json_data['profitability'][d])-1) *100));
	power_used = Math.round((json_data['power_used'][d]/1000) * 100) / 100;
	coin_mined = json_data['coin_mined'][d];
	coin = json_data['coin'][d];
	savings = json_data['coin_purchase_cost'][d] - json_data['power_used_cost'][d];
	savings = Math.round(savings * 100) / 100;
	
	tooltip = "";
	
	if (key == 'power_used_cost' || key == 'profitability') {

		if (profitability>=0) {
			profitable = "<font color='green'><strong>Profitable (" + profitability + "%)</strong></font>";
		} else {
			profitable = "<font color='red'><strong>Not Profitable (" + profitability + "%)</strong></font>";
		}
		
		tooltip = profitable + "<BR>Power used: " + power_used + " kW<BR>Total <b>" + coin + "</b> mined: " + coin_mined;
		
	} else {
		if (savings>=0) {
			tooltip = "<font color='green'><strong>Saved</strong></font> " + currency_symb + savings + " by mining <b>" + coin + "</b>";
		} else {
			tooltip = "<font color='red'><strong>Lost</strong></font> " + currency_symb + savings + " by mining <b>" + coin + "</b>";
		}
	}
	
	return tooltip;
	
}


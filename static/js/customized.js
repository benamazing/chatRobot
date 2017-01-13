$(document).ready(function(){

	$.getJSON("/hs300list", function(result){

		//Render Bar chart
		var myChart = echarts.init(document.getElementById('chartArea'));
		var option = {
			title: {
				text: 'Top 10'
			},
			tooltip: {},
			legend: {
				data: ['Weight']
			},
			xAxis: {
				data: []
			},
			yAxis: {data: ['%']},
			series: [{
				name: "Weight",
				type: "bar",
				data: []
			}]
		};
		for (i = 0; i < result.data.length; i++){
			if (i > 9) break;
			option.xAxis.data[i] = result.data[i].name;
			option.series[0].data[i] = result.data[i].weight;
		}
		myChart.setOption(option);

		//Render dataTable
		$('#hs300').DataTable({
			buttons: [
					{
						extend: 'csv',
						text: 'Export to csv'
					},
					{
						extend: 'excel',
						text: 'Export to Excel'
					}
			],
			"lengthMenu": [[10,50,100, -1], [10,50,100,"All"]],
			//"ajax": "/hs300list",
			"data": result.data,
            "initComplete": function(settings, json){
                    var t = $('#hs300').DataTable();
                    t.buttons(0, null).containers().appendTo('body');
             },
			"columns": [
					{"data": "code"},
					{"data": "name"},
					{"data": "weight"}
			]
		});
	});
});

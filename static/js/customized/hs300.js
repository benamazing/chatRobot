$(document).ready(function(){
	var myContainer = document.getElementById('chartArea');
	var resizeContainer = function(){
		w1 = window.innerHeight / 2;
		w2 = 600;
		w = w1 > w2 ? w1 :w2;
		myContainer.style.width = w + 'px';
		myContainer.style.height = w * 0.5 + 'px';
	};
	//resizeContainer();
	var myChart = echarts.init(document.getElementById('chartArea'));
	myChart.showLoading();
	$.getJSON("/hs300list", function(result){
		//Render Bar chart
		myChart.hideLoading();
		var option = {
			title: {
				text: 'Top 10权重股',
				left: 'center'
			},
			tooltip: {},
			legend: {
				data: ['权重'],
				top:'bottom'
			},
			yAxis: {
				data: []
			},
			xAxis: {},
			series: [{
				name: "权重",
				type: "bar",
				data: []
			}]
		};
		for (i = 0; i < result.data.length; i++){
			if (i > 9) break;
			option.yAxis.data[i] = result.data[i].name;
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
			"lengthMenu": [[50,100, -1], [50,100,"All"]],
			//"ajax": "/hs300list",
			"data": result.data,
            "initComplete": function(settings, json){
                    var t = $('#hs300').DataTable();
                    t.buttons(0, null).containers().appendTo('#tableDiv');
             },
			"columns": [
					{"data": "code"},
					{"data": "name"},
					{"data": "weight"}
			]
		});
	});
	window.onresize = function() {
		resizeContainer();
		myChart.resize();
	}
});

$(document).ready(function(){
	var mapContainer = document.getElementById('mapContainer');
	var resizeContainer = function(){
		mapContainer.style.width = window.innerWidth + 'px';
		mapContainer.style.height = window.innerHeight * 3/4 + 'px';
	};
	//resizeContainer();
	var myChart = echarts.init(document.getElementById('mapContainer'), 'vintage');
	myChart.showLoading();
	$.getJSON("/stocklistjson?type=full", function(result){

		//Render map
		myChart.hideLoading();
		var option = {
			title: {
				text: '上市公司分布图',
				left: 'center'
			},
			tooltip: {
				trigger: 'item'
			},
			legend: {
				orient: 'vertical',
				left: 'left',
				data: ['数量']
			},
			visualMap: {
				min: 0,
				max: 500,
				left: 'left',
				top: 'bottom',
				text: ['High', 'Low'],
				calculable: true,
				inRange: {
					color: ['lightskyblue','yellow', 'orangered']
				}
			},
			toolbox: {
				show: true,
				orient: 'vertical',
				left: 'right',
				top: 'center',
				feature: {
					mark: {show: true},
					dataView: {show: true, readOnly: false},
					restore: {show: true},
					saveAsImage: {show: true}
				}
			},
			series: [{
				name: "quantity",
				type: "map",
				mapType: 'china',
				roam: false,
				label: {
					normal: {
						show: false
					},
					emphasis: {
						show: true
					}
				},
				data: []
			}]
		};
		areas = {}
		for (i = 0; i < result.data.length; i++){
			area = result.data[i].area;
			if (!!areas[area]) {
				areas[area] += 1;
			} else {
				areas[area] = 1;
			}
		}
		idx = 0;
		for (area in areas){
			option.series[0].data[idx] = {};
			option.series[0].data[idx]['name'] = area;
			option.series[0].data[idx]['value'] = areas[area];
			idx++;
		}
		myChart.setOption(option);

		//render tables
		$('#stockListTable').DataTable({
			"lengthMenu": [[50,100,-1],[50,100,'All']],
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
			"data": result.data,
			"initComplete": function(settings, json){
					var t = $('#stockListTable').DataTable();
					t.buttons(0, null).containers().appendTo('#tableDiv');
			 },
			"columns": [
				{"data": "name"},
				{"data": "industry"},
				{"data": "area"},
				{"data": "pe"},
				{"data": "outstanding"},
				{"data": "totals"},
				{"data": "totalAssets"},
				{"data": "liquidAssets"},
				{"data": "esp"},
				{"data": "bvps"},
				{"data": "timeToMarket"},
				{"data": "holders"}
			]
		});

		//Bind click
		myChart.on("click", function(params) {
			var area = params.name;
			$('#tableName').text(area + "股票列表");
			if ($('#stockListTable').hasClass('dataTable')) {
				dtable = $('#stockListTable').DataTable();
				//dtable.clear();
				dtable.destroy();
			}
			stockList = [];
			j = 0;
			for (i = 0; i < result.data.length; i++){
				if (result.data[i].area == area){
					stockList[stockList.length] = result.data[i]
				}
			}
			$('#stockListTable').DataTable({
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
				"lengthMenu": [[50,100,-1],[50,100,'All']],
				"data": stockList,
				"initComplete": function(settings, json){
						var t = $('#stockListTable').DataTable();
						t.buttons(0, null).containers().appendTo('#tableDiv');
				 },
				"columns": [
					{"data": "name"},
					{"data": "industry"},
					{"data": "area"},
					{"data": "pe"},
					{"data": "outstanding"},
					{"data": "totals"},
					{"data": "totalAssets"},
					{"data": "liquidAssets"},
					{"data": "esp"},
					{"data": "bvps"},
					{"data": "timeToMarket"},
					{"data": "holders"}
				]
			});

		});
	});

	window.onresize = function() {
		resizeContainer();
		myChart.resize();
	}
});

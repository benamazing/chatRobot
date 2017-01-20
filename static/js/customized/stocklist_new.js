$(document).ready(function(){
	var mapContainer = document.getElementById('mapContainer');
	var resizeContainer = function(){
		mapContainer.style.width = window.innerWidth + 'px';
		mapContainer.style.height = window.innerHeight * 3/4 + 'px';
	};
	//resizeContainer();
	var myChart = echarts.init(document.getElementById('mapContainer'));
	var industryChart = echarts.init(document.getElementById("industryChart"));
	myChart.showLoading();
	$.getJSON("/stocklistjson?type=full", function(result){

		//Render map
		myChart.hideLoading();
		var option = {
			title: {
				text: '上市公司区域分布图',
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
		industries = {}
		for (i = 0; i < result.data.length; i++){
			area = result.data[i].area;
			industry = result.data[i].industry;
			if (!!areas[area]) {
				areas[area] += 1;
			} else {
				areas[area] = 1;
			}
			if (!!industries[industry]){
				industries[industry] +=1;
			} else{
				industries[industry] = 1;
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

		//render industryChart
		var option2 = {
			title: {
				text: "行业分布图",
				left: "center"
			},
			tooltip: {},
			legend: {
				data: ['数量'],
				top: 'bottom'
			},
			yAxis: {
				data: []
			},
			xAxis: {},
			series: [{
				name: "数量",
				type: "bar",
				data: []
			}]
		};

		idx = 0;
		for (industry in industries){
			option2.yAxis.data[idx] = industry;
			option2.series[0].data[idx] = industries[industry];
			idx++;
		};
		industryChart.setOption(option2);

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
				{"data": "code"},
				{"data": "name"},
				{"data": "industry"},
				{"data": "area"},
				{"data": "timeToMarket"},
				{"data": "pe"},
				{"data": "outstanding"},
				{"data": "totals"},
				{"data": "totalAssets"},
				{"data": "liquidAssets"},
				{"data": "esp"},
				{"data": "bvps"},
				{"data": "pb"},
				{"data": "undp"},
				{"data": "rev"},
				{"data": "profit"},
				{"data": "gpr"},
				{"data": "npr"},
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
					{"data": "code"},
					{"data": "name"},
					{"data": "industry"},
					{"data": "area"},
					{"data": "timeToMarket"},
					{"data": "pe"},
					{"data": "outstanding"},
					{"data": "totals"},
					{"data": "totalAssets"},
					{"data": "liquidAssets"},
					{"data": "esp"},
					{"data": "bvps"},
					{"data": "pb"},
					{"data": "undp"},
					{"data": "rev"},
					{"data": "profit"},
					{"data": "gpr"},
					{"data": "npr"},
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

$(document).ready(function(){
	var mapContainer = document.getElementById('mapContainer');
	var resizeContainer = function(){
		mapContainer.style.width = window.innerWidth + 'px';
		mapContainer.style.height = window.innerHeight * 3/4 + 'px';
	};
	//resizeContainer();
	var myChart = echarts.init(document.getElementById('mapContainer'));
	var industryChart = echarts.init(document.getElementById("industryChart"));
	var pepbChart = echarts.init(document.getElementById("pepbChart"));
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
				top: 'top',
				left: 'right'
			},
			yAxis: {
				data: []
			},
			xAxis: {},
			series: [{
				name: "数量",
				type: "bar",
				data: []
			}],
			dataZoom: [
				{
					type: 'slider',
					show: true,
					start: 0,
					end: 100,
				},
				{
					type: 'inside'
				}
			]
		};

		idx = 0;
		for (industry in industries){
			option2.yAxis.data[idx] = industry;
			option2.series[0].data[idx] = industries[industry];
			idx++;
		};
		industryChart.setOption(option2);

		//render pepbChart
		var option3 = {
			backgroundColor: new echarts.graphic.RadialGradient(0.3, 0.3, 0.8, [{
				offset: 0,
				color: '#f7f8fa'
			}, {
				offset: 1,
				color: '#cdd0d5'
			}]),
			title: {
				text: '市盈率、市净率'
			},
			tooltip: {
				trigger: "item",
				formatter: function(param){
					return param.data[3] + "<br/>市盈率: " + param.data[0] +　"<br/>市净率: " + param.data[1] + "<br/>总资产: " + param.data[2] + "亿元";
				}
			},
			legend: {
				right: 10,
				data: ['市盈率/市净率']
			},
			xAxis: {
				splitLine: {
					lineStyle: {
						type: 'dashed'
					}
				},
				name: '市盈率',
				max: 1000,
				min: 0
			},
			yAxis: {
				splitLine: {
					lineStyle: {
						type: 'dashed'
					}
				},
				name: '市净率',
				max: 100,
				min: 0
			},
			series: [{
				name: '市盈率/市净率',
				data: [],
				type: 'scatter'
			}],
			dataZoom: [
				{
					type: 'slider',
					show: true,
					xAxisIndex: [0],
					start: 0,
					end: 100
				},
				{
					type: 'slider',
					show: true,
					yAxisIndex: [0],
					left: '93%',
					start: 0,
					end: 100
				},
				{
					type: 'inside',
					xAxisIndex: [0],
					start: 0,
					end: 100
				},
				{
					type: 'inside',
					yAxisIndex: [0],
					start: 0,
					end: 100
				}
			],
			visualMap: {
				min: 10,
				max: 10000,
				dimension: 2,
				calculable: true,
				text:['总资产: (亿元)'],
				color: ['orangered','yellow','lightskyblue']
			},
		};

		for (i = 0; i < result.data.length; i++) {
			option3.series[0].data[i] = [];
			option3.series[0].data[i][0] = result.data[i].pe;
			option3.series[0].data[i][1] = result.data[i].pb;
			option3.series[0].data[i][2] = (result.data[i].totalAssets/10000).toFixed(2);
			option3.series[0].data[i][3] = result.data[i].name;
		};


		pepbChart.setOption(option3);

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

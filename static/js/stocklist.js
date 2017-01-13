$(document).ready(function(){
	var myChart = echarts.init(document.getElementById('mapContainer'), 'vintage');
	myChart.showLoading();
	$.getJSON("/stocklistjson?type=simple", function(result){

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
						show: true
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
	});
});

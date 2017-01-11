$(document).ready(function(){
	$('#stockTable').DataTable({
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
		"ajax": "/stocklist",
                "initComplete": function(settings, json){
                    var t = $('#stockTable').DataTable();
                    t.buttons(0, null).containers().appendTo('body');
                },
		"columns": [
					{"data": "code"},
					{"data": "name"},
					{"data": "industry"},
					{"data": "area"},
					{"data": "pe"},
					{"data": "outstanding"},
					{"data": "totals"},
					{"data": "totalAssets"},
					{"data": "liquidAssets"},
					{"data": "fixedAssets"},
					{"data": "esp"},
					{"data": "bvps"},
					{"data": "pb"},
					{"data": "timeToMarket"}
		]
	});
});

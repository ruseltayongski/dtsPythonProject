window.onload = function() {
    console.log(bar_chart)
    var options = {
        animationEnabled: true,
        // title: {
        //     text: "Booking Traffic Source"
        // },
        data: [{
                type: "pie",
                startAngle: 45,
                showInLegend: "true",
                legendText: "{label}",
                indexLabel: "{label} ({y})",
                yValueFormatString:"#,##0.#"%"",
                dataPoints: [
                    {y: bar_chart['created']??0, label: "created"},
                    {y: bar_chart['released']??0, label: "released"},
                    {y: bar_chart['accepted']??0, label: "accepted"},
                    {y: bar_chart['cycled end']??0, label: "cycle end"}
                ]
        }]
    };
    $("#chartContainer").CanvasJSChart(options);


    /*let datapoints_bookings = [];
    $.each(<?php echo json_encode($linechart)?>, function( index, value ) {
        datapoints_bookings.push({
            x: new Date(value.date),
            y: parseFloat(value.value)
        });
    });*/

    var chart1 = new CanvasJS.Chart("chartContainer1", {
        animationEnabled: true,
        title:{
            text: "Document's Comprehensive Overview"
        },
        axisX:{
            valueFormatString: "DD MMM",
            crosshair: {
                enabled: true,
                snapToDataPoint: true
            }
        },
        axisY: {
            //title: "Closing Price (in PESOS)",
            valueFormatString: "##0",
            crosshair: {
                enabled: true,
                snapToDataPoint: true,
                labelFormatter: function(e) {
                    return "" + CanvasJS.formatNumber(e.value, "##0");
                }
            }
        },
        data: [{
            type: "area",
            xValueFormatString: "DD MMM",
            yValueFormatString: "##0",
            dataPoints:
            [
                { x: new Date(2017, 0, 3), y: 650 },
                { x: new Date(2017, 0, 4), y: 700 },
                { x: new Date(2017, 0, 5), y: 710 },
                { x: new Date(2017, 0, 6), y: 658 },
                { x: new Date(2017, 0, 7), y: 734 },
                { x: new Date(2017, 0, 8), y: 963 },
                { x: new Date(2017, 0, 9), y: 847 },
                { x: new Date(2017, 0, 10), y: 853 },
                { x: new Date(2017, 0, 11), y: 869 },
                { x: new Date(2017, 0, 12), y: 943 },
                { x: new Date(2017, 0, 13), y: 970 },
                { x: new Date(2017, 0, 14), y: 869 },
                { x: new Date(2017, 0, 15), y: 890 },
                { x: new Date(2017, 0, 16), y: 930 }
            ]
        }]
    });
    chart1.render();
}
import React, { useEffect } from 'react';
import * as am4core from '@amcharts/amcharts4/core';
import * as am4charts from '@amcharts/amcharts4/charts';

const PieChart = ({ data }) => {
    useEffect(() => {
        // Create chart instance
        let chart = am4core.create('chartdiv', am4charts.PieChart3D);

        // Set data for the chart
        chart.data = data;

        // Create pie series
        let series = chart.series.push(new am4charts.PieSeries3D());
        series.dataFields.value = 'value';
        series.dataFields.category = 'category';

        // Add labels
        let labelBullet = series.bullets.push(new am4charts.LabelBullet());
        labelBullet.label.text = '{category}';
        labelBullet.label.fontSize = 14;
        labelBullet.label.maxWidth = 200;
        labelBullet.label.wrap = true;
        labelBullet.label.truncate = true;
        labelBullet.label.hideOversized = true;
        labelBullet.label.align = 'center';
        labelBullet.label.verticalCenter = 'middle';

        // Dispose of the chart when the component unmounts
        return () => {
            chart.dispose();
        };
    }, [data]);

    return <div id="chartdiv" style={{ width: '100%', height: '400px' }}></div>;
};

export default PieChart;

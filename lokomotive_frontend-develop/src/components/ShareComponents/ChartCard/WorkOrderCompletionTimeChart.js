import React, { useEffect } from 'react';
import { create } from '@amcharts/amcharts4/core';
import { XYChart, CategoryAxis, ValueAxis, ColumnSeries, XYCursor, themes } from '@amcharts/amcharts4/charts';
import am4themes_animated from "@amcharts/amcharts4/themes/animated";
import * as am4core from "@amcharts/amcharts4/core";
import * as am4charts from "@amcharts/amcharts4/charts";
import { isMobileDevice } from "../../../helpers/helperFunctions";


const WorkOrderCompletionTimeChart = ({ data, height }) => {
    const isMobile = isMobileDevice();

    useEffect(() => {
        // Use am4core to create a chart instance
        const chart = create("chartdiv", XYChart);
    
        // Apply theme
        // am4core.useTheme(am4themes_animated);
    
        // Convert the data object into an array of objects
        const chartData = Object.keys(data).map(key => ({
            category: capitalizeFirstLetter(key.replace("_avg_completion_days", "")),
        value: data[key]
        }));
    
        // Set the chart data
        chart.data = chartData;
    
        // Create axes
        const categoryAxis = chart.yAxes.push(new CategoryAxis());
        categoryAxis.dataFields.category = "category";
        categoryAxis.renderer.grid.template.location = 0;
        categoryAxis.renderer.inversed = true;
    
        const valueAxis = chart.xAxes.push(new ValueAxis());
        valueAxis.min = 234;
        valueAxis.max = 234.18; 

        // Adjust margins or padding
        chart.paddingRight = 30; // Increase right padding to create more space for labels
        // Adjust margins or padding
        
        // Create series
        const series = chart.series.push(new ColumnSeries());
        series.dataFields.valueX = "value";
        series.dataFields.categoryY = "category";
        series.columns.template.tooltipText = "{categoryY}: [bold]{valueX}[/]";
        series.columns.template.strokeWidth = 0;
        series.columns.template.adapter.add("fill", (fill, target) => {
        return chart.colors.getIndex(target.dataItem.index);
        });

        // Add cursor
        chart.cursor = new XYCursor();
    
        // Cleanup on unmount
        return () => {
        chart.dispose();
        };
    }, [data]);

    // Capitalize the first letter of a string
    const capitalizeFirstLetter = (str) => {
        return str.charAt(0).toUpperCase() + str.slice(1);
    };
    if(isMobile) {
        return (
            <div id="chartdiv" style={{width: "100%", overflow: "auto"}}></div>
        )
    } else {
        return <div id="chartdiv" style={{ width: '99%', height: height }}></div>;
    }
};
export default WorkOrderCompletionTimeChart;
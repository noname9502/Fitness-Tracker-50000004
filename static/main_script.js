  // Initialize ECharts
        document.addEventListener('DOMContentLoaded', function() {
            // Pie Chart
            const pieChart = echarts.init(document.getElementById('pie-chart'));
            pieChart.setOption({
                tooltip: {
                    trigger: 'item'
                },
                legend: {
                    orient: 'horizontal',
                    bottom: 10,
                    textStyle: {
                        color: '#8d99ae'
                    }
                },
                series: [{
                    name: 'Activities',
                    type: 'pie',
                    radius: '70%',
                    data: [
                        { value: 35, name: 'Running' },
                        { value: 25, name: 'Cycling' },
                        { value: 20, name: 'Weightlifting' },
                        { value: 10, name: 'Swimming' },
                        { value: 10, name: 'Hiking' }
                    ],
                    emphasis: {
                        itemStyle: {
                            shadowBlur: 10,
                            shadowOffsetX: 0,
                            shadowColor: 'rgba(0, 0, 0, 0.5)'
                        }
                    },
                    itemStyle: {
                        borderRadius: 10,
                        borderColor: '#fff',
                        borderWidth: 2
                    }
                }]
            });
            
            // Line Chart
            const lineChart = echarts.init(document.getElementById('line-chart'));
            lineChart.setOption({
                tooltip: {
                    trigger: 'axis'
                },
                legend: {
                    data: ['Steps', 'Calories Burned', 'Active Minutes'],
                    textStyle: {
                        color: '#8d99ae'
                    }
                },
                grid: {
                    left: '3%',
                    right: '4%',
                    bottom: '3%',
                    containLabel: true
                },
                xAxis: {
                    type: 'category',
                    boundaryGap: false,
                    data: ['Week 1', 'Week 2', 'Week 3', 'Week 4'],
                    axisLine: {
                        lineStyle: {
                            color: '#8d99ae'
                        }
                    }
                },
                yAxis: {
                    type: 'value',
                    axisLine: {
                        lineStyle: {
                            color: '#8d99ae'
                        }
                    }
                },
                series: [
                    {
                        name: 'Steps',
                        type: 'line',
                        smooth: true,
                        data: [58000, 62000, 70000, 75000],
                        lineStyle: {
                            width: 4,
                            color: '#4361ee'
                        }
                    },
                    {
                        name: 'Calories Burned',
                        type: 'line',
                        smooth: true,
                        data: [12500, 13600, 15800, 17200],
                        lineStyle: {
                            width: 4,
                            color: '#4cc9f0'
                        }
                    },
                    {
                        name: 'Active Minutes',
                        type: 'line',
                        smooth: true,
                        data: [1250, 1420, 1650, 1820],
                        lineStyle: {
                            width: 4,
                            color: '#2ec4b6'
                        }
                    }
                ]
            });
            
            // Bar Chart
            const barChart = echarts.init(document.getElementById('bar-chart'));
            barChart.setOption({
                tooltip: {
                    trigger: 'axis',
                    axisPointer: {
                        type: 'shadow'
                    }
                },
                grid: {
                    left: '3%',
                    right: '4%',
                    bottom: '3%',
                    containLabel: true
                },
                xAxis: {
                    type: 'category',
                    data: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
                    axisLine: {
                        lineStyle: {
                            color: '#8d99ae'
                        }
                    }
                },
                yAxis: {
                    type: 'value',
                    name: 'Calories',
                    axisLine: {
                        lineStyle: {
                            color: '#8d99ae'
                        }
                    }
                },
                series: [
                    {
                        name: 'Calories Burned',
                        type: 'bar',
                        itemStyle: {
                            color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
                                { offset: 0, color: '#4361ee' },
                                { offset: 1, color: '#4cc9f0' }
                            ])
                        },
                        data: [3200, 2800, 3500, 4200, 3000, 5100, 3800],
                        barWidth: '40%'
                    }
                ]
            });
            
            // Radar Chart
            const radarChart = echarts.init(document.getElementById('radar-chart'));
            radarChart.setOption({
                tooltip: {},
                radar: {
                    indicator: [
                        { name: 'Running', max: 100 },
                        { name: 'Cycling', max: 100 },
                        { name: 'Swimming', max: 100 },
                        { name: 'Weightlifting', max: 100 },
                        { name: 'Yoga', max: 100 },
                        { name: 'HIIT', max: 100 }
                    ]
                },
                series: [{
                    name: 'Workout Time (min)',
                    type: 'radar',
                    data: [
                        {
                            value: [85, 70, 30, 60, 45, 75],
                            name: 'This Week',
                            lineStyle: {
                                width: 3,
                                color: '#4361ee'
                            }
                        },
                        {
                            value: [70, 65, 25, 55, 40, 65],
                            name: 'Last Week',
                            lineStyle: {
                                width: 3,
                                color: '#4cc9f0'
                            }
                        }
                    ]
                }]
            });
// Area Chart - Heart Rate Trends ❤️
const areaChart = echarts.init(document.getElementById('area-chart'));
areaChart.setOption({
    tooltip: { trigger: 'axis' },
    xAxis: {
        type: 'category',
        data: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
        axisLine: { lineStyle: { color: '#8d99ae' } }
    },
    yAxis: {
        type: 'value',
        name: 'BPM',
        axisLine: { lineStyle: { color: '#8d99ae' } }
    },
    series: [{
        data: [72, 78, 70, 75, 80, 77, 74],
        type: 'line',
        smooth: true,
        areaStyle: {
            color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
                { offset: 0, color: '#4cc9f0' },
                { offset: 1, color: '#4361ee' }
            ])
        },
        lineStyle: { width: 3, color: '#4895ef' },
        symbol: 'circle',
        symbolSize: 8
    }]
});

// Donut Chart - Workout Category Breakdown 🥧
const donutChart = echarts.init(document.getElementById('donut-chart'));
donutChart.setOption({
    tooltip: { trigger: 'item' },
    legend: {
        bottom: 10,
        textStyle: { color: '#8d99ae' }
    },
    series: [{
        name: 'Workout Types',
        type: 'pie',
        radius: ['45%', '70%'],
        avoidLabelOverlap: false,
        itemStyle: {
            borderRadius: 10,
            borderColor: '#fff',
            borderWidth: 2
        },
        label: { show: false },
        emphasis: {
            label: { show: true, fontSize: 18, fontWeight: 'bold' }
        },
        data: [
            { value: 1048, name: 'Cardio' },
            { value: 735, name: 'Strength' },
            { value: 580, name: 'Yoga' },
            { value: 484, name: 'Stretching' },
            { value: 300, name: 'HIIT' }
        ]
    }]
});

            
            
            // Handle window resize
            window.addEventListener('resize', function() {
                pieChart.resize();
                lineChart.resize();
                barChart.resize();
                radarChart.resize();
                areaChart.resize();
                donutChart.resize();
            });
        });


import React, { useEffect, useState, useMemo, useRef } from 'react';
import axios from 'axios';
import socketIOClient from 'socket.io-client';
import * as d3 from 'd3';
import { useTable, useSortBy } from 'react-table';

const ENDPOINT = "http://localhost:3001";

function App() {
    const [records, setRecords] = useState([]);
    const chartRef = useRef(null);
    const videoRef = useRef(null);

    useEffect(() => {
        const fetchData = async () => {
            try {
                const response = await axios.get(`${ENDPOINT}/cumulative_records`);
                setRecords(response.data);
            } catch (error) {
                console.error('Error fetching data:', error);
            }
        };

        fetchData();

        const socket = socketIOClient(ENDPOINT);
        socket.on('newCumulativeRecord', (newRecord) => {
            setRecords((prevRecords) => [newRecord, ...prevRecords]);
        });

        return () => socket.disconnect();
    }, []);

    useEffect(() => {
        if (records.length > 0) {
            const svg = d3.select(chartRef.current)
                .attr('height', 300);

            svg.selectAll('*').remove(); // Clear previous elements

            const margin = { top: 20, right: 30, bottom: 30, left: 40 };
            const width = records.length * 50; // Dynamic width based on data length
            const height = +svg.attr('height') - margin.top - margin.bottom;

            svg.attr('width', width + margin.left + margin.right);

            const x = d3.scaleTime()
                .domain([
                    d3.min(records, d => new Date(d.event_time)), 
                    d3.timeMinute.offset(d3.min(records, d => new Date(d.event_time)), records.length)
                ]) // Dynamic domain: based on the number of records
                .range([margin.left, margin.left + records.length * 200]); // 30 pixels per minute

            const y = d3.scaleLinear()
                .domain([0, 20]) // Default domain from 0 to 10
                .range([height - margin.bottom, margin.top]);
                
            const line = d3.line()
                .x(d => x(new Date(d.event_time)))
                .y(d => y(d.hit_count));

            svg.append('g')
                .attr('transform', `translate(0,${height - margin.bottom})`)
                .call(d3.axisBottom(x).ticks(width / 80).tickSizeOuter(0));

            svg.append('g')
                .attr('transform', `translate(${margin.left},0)`)
                .call(d3.axisLeft(y));

            svg.append('path')
                .datum(records)
                .attr('fill', 'none')
                .attr('stroke', 'steelblue')
                .attr('stroke-width', 1.5)
                .attr('d', line);

            svg.selectAll('.feeding-symbol')
                .data(records.filter(record => record.event_type === 'feeding'))
                .enter()
                .append('rect')
                .attr('class', 'feeding-symbol')
                .attr('x', d => x(new Date(d.event_time)) - 5)
                .attr('y', d => y(d.hit_count) - 5)
                .attr('width', 10)
                .attr('height', 10)
                .attr('fill', 'blue');

            svg.selectAll('.red-symbol')
                .data(records.filter(record => ['red-1', 'red-2', 'red-3', 'red-4'].includes(record.event_type)))
                .enter()
                .append('circle')
                .attr('class', 'red-symbol')
                .attr('cx', d => x(new Date(d.event_time)))
                .attr('cy', d => y(d.hit_count))
                .attr('r', 5)
                .attr('fill', 'red');

            svg.selectAll('.warning-symbol')
                .data(records.filter(record => ['warning-1', 'warning-2', 'warning-3', 'warning-4'].includes(record.event_type)))
                .enter()
                .append('circle')
                .attr('class', 'warning-symbol')
                .attr('cx', d => x(new Date(d.event_time)))
                .attr('cy', d => y(d.hit_count))
                .attr('r', 5)
                .attr('fill', 'none')
                .attr('stroke', 'red');

            svg.selectAll('.punishment-symbol')
                .data(records.filter(record => record.event_type === 'punishment'))
                .enter()
                .append('circle')
                .attr('class', 'punishment-symbol')
                .attr('cx', d => x(new Date(d.event_time)))
                .attr('cy', d => y(d.hit_count))
                .attr('r', 5)
                .attr('fill', 'black');
        }
    }, [records]);

    useEffect(() => {
        const startCamera = async () => {
            try {
                const stream = await navigator.mediaDevices.getUserMedia({ video: true });
                if (videoRef.current) {
                    videoRef.current.srcObject = stream;
                }
            } catch (error) {
                console.error('Error accessing camera:', error);
            }
        };

        startCamera();
    }, []);

    const columns = useMemo(
        () => [
            {
                Header: 'ID',
                accessor: 'event_id',
            },
            {
                Header: 'Type',
                accessor: 'event_type',
            },
            {
                Header: 'Time',
                accessor: 'event_time',
            },
            {
                Header: 'Hit Count',
                accessor: 'hit_count',
            },
        ],
        []
    );

    const tableInstance = useTable({ columns, data: records }, useSortBy);

    const {
        getTableProps,
        getTableBodyProps,
        headerGroups,
        rows,
        prepareRow,
    } = tableInstance;

    return (
        <div className="App" style={{ padding: '0 20px' }}>
            <h1>Cumulative Records</h1>

            <div style={{ display: 'flex', marginBottom: '20px' }}>
                <div style={{ flex: 1, marginRight: '20px' }}>
                    <h2>Score Updated Records Line Chart</h2>
                    <div style={{ height: '400px', overflowY: 'scroll' }}>
                        <table {...getTableProps()} style={{ width: '100%', borderCollapse: 'collapse' }}>
                            <thead>
                                {headerGroups.map(headerGroup => (
                                    <tr {...headerGroup.getHeaderGroupProps()}>
                                        {headerGroup.headers.map(column => (
                                            <th {...column.getHeaderProps(column.getSortByToggleProps())} style={{ border: '1px solid black', padding: '5px' }}>
                                                {column.render('Header')}
                                                <span>
                                                    {column.isSorted
                                                        ? column.isSortedDesc
                                                            ? ' 🔽'
                                                            : ' 🔼'
                                                        : ''}
                                                </span>
                                            </th>
                                        ))}
                                    </tr>
                                ))}
                            </thead>
                            <tbody {...getTableBodyProps()}>
                                {rows.map(row => {
                                    prepareRow(row);
                                    return (
                                        <tr {...row.getRowProps()}>
                                            {row.cells.map(cell => (
                                                <td {...cell.getCellProps()} style={{ border: '1px solid black', padding: '5px' }}>
                                                    {cell.render('Cell')}
                                                </td>
                                            ))}
                                        </tr>
                                    );
                                })}
                            </tbody>
                        </table>
                    </div>
                </div>
                <div style={{ flex: 1 }}>
                    <h2>Live Camera Feed</h2>
                    <video ref={videoRef} autoPlay style={{ width: '100%', maxHeight: '400px' }}></video>
                </div>
            </div>

            <div style={{ width: '100%', overflowX: 'auto' }}>
                <svg ref={chartRef}></svg>
            </div>
        </div>
    );
}

export default App;
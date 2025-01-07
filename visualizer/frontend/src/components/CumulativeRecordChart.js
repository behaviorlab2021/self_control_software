import React, { useEffect } from "react";
import * as d3 from "d3";

function CumulativeRecordChart({ chartRef, records, events, session }) {
  useEffect(() => {
    if (records.length > 0) {
      const svg = d3
        .select(chartRef.current)
        .attr("height", "100%")
        .attr("width", "100%");

      svg.selectAll("*").remove(); // Clear previous elements

      const margin = { top: 20, right: 30, bottom: 30, left: 40 };
      const minTime = d3.min(records, (d) => new Date(d.event_time));
      const maxTime = d3.max(records, (d) => new Date(d.event_time));
      const timeDiff = (maxTime - minTime) / (1000 * 60); // Difference in minutes
      const width = timeDiff * 240; // 240 pixels per minute to ensure overflow
      const height =
        +svg.node().getBoundingClientRect().height - margin.top - margin.bottom;

      svg.attr("width", width + margin.left + margin.right);

      const x = d3
        .scaleTime()
        .domain([minTime, maxTime])
        .range([margin.left, width + margin.left]);

      const y = d3
        .scaleLinear()
        .domain([0, session ? session.reinforcement_ratio : 10]) // Use session.reinforcement_ratio if available
        .range([height - margin.bottom, margin.top]);

      const line = d3
        .line()
        .x((d) => x(new Date(d.event_time)))
        .y((d) => y(d.hit_count));

      svg
        .append("g")
        .attr("transform", `translate(0,${height - margin.bottom})`)
        .call(
          d3
            .axisBottom(x)
            .ticks(width / 80)
            .tickSizeOuter(0)
        );

      svg
        .append("g")
        .attr("transform", `translate(${margin.left},0)`)
        .call(d3.axisLeft(y));

      svg
        .append("path")
        .datum(records)
        .attr("fill", "none")
        .attr("stroke", "steelblue")
        .attr("stroke-width", 1.5)
        .attr("d", line);

      svg
        .selectAll(".feeding-symbol")
        .data(events.filter((event) => event.event_type === "feeding"))
        .enter()
        .append("rect")
        .attr("class", "feeding-symbol")
        .attr("x", (d) => x(new Date(d.event_time)) - 5)
        .attr("y", (d) => y(d.hit_count) - 5)
        .attr("width", 10)
        .attr("height", 10)
        .attr("fill", "blue");

      svg
        .selectAll(".red-symbol")
        .data(events.filter((event) => event.event_type === "red"))
        .enter()
        .append("circle")
        .attr("class", "red-symbol")
        .attr("cx", (d) => x(new Date(d.event_time)))
        .attr("cy", (d) => y(d.hit_count))
        .attr("r", 5)
        .attr("fill", "red");

      svg
        .selectAll(".warning-symbol")
        .data(events.filter((event) => event.event_type === "warning"))
        .enter()
        .append("circle")
        .attr("class", "warning-symbol")
        .attr("cx", (d) => x(new Date(d.event_time)))
        .attr("cy", (d) => y(d.hit_count))
        .attr("r", 5)
        .attr("fill", "none")
        .attr("stroke", "red");

      svg
        .selectAll(".punishment-symbol")
        .data(events.filter((event) => event.event_type === "punishment"))
        .enter()
        .append("circle")
        .attr("class", "punishment-symbol")
        .attr("cx", (d) => x(new Date(d.event_time)))
        .attr("cy", (d) => y(d.hit_count))
        .attr("r", 5)
        .attr("fill", "black");

      svg
        .selectAll(".session-end-symbol")
        .data(events.filter((event) => event.event_type === "session_end"))
        .enter()
        .append("text")
        .attr("class", "session-end-symbol")
        .attr("x", (d) => x(new Date(d.event_time)))
        .attr("y", (d) => y(d.hit_count))
        .attr("dy", ".5em")
        .attr("text-anchor", "middle")
        .attr("font-size", "40px")
        .attr("fill", "purple")
        .text("*");

      svg
        .selectAll(".session-start-symbol")
        .data(events.filter((event) => event.event_type === "session_start"))
        .enter()
        .append("text")
        .attr("class", "session-start-symbol")
        .attr("x", (d) => x(new Date(d.event_time)))
        .attr("y", (d) => y(d.hit_count))
        .attr("dy", ".5em")
        .attr("text-anchor", "middle")
        .attr("font-size", "40px")
        .attr("fill", "green")
        .text("*");

      svg
        .selectAll(".new-round-symbol")
        .data(events.filter((event) => event.event_type === "new_round"))
        .enter()
        .append("text")
        .attr("class", "new-round-symbol")
        .attr("x", (d) => x(new Date(d.event_time)))
        .attr("y", (d) => y(d.hit_count))
        .attr("dy", "0.2em")
        .attr("text-anchor", "middle")
        .attr("font-size", "16px")
        .attr("fill", "blue")
        .text("|");

      // Scroll to the right after rendering
      chartRef.current.scrollLeft = chartRef.current.scrollWidth;
    }
  }, [records, events, session]);

  return <svg ref={chartRef}></svg>;
}

export default CumulativeRecordChart;

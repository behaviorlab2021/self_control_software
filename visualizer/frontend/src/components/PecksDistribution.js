import React, { useEffect, useRef } from "react";
import * as d3 from "d3";

function PecksDistribution({ pecks, session }) {
  const containerRef = useRef(null);

  useEffect(() => {
    if (session) {
      const svg = d3.select("#pecks_distribution_svg");

      svg.selectAll("*").remove(); // Clear previous elements

      const margin = { top: 10, right: 0, bottom: 10, left: 0 };
      const container = containerRef.current;
      const availableHeight = Math.floor(container.clientHeight); // Use Math.floor to avoid overflow
      const aspectRatio = session.window_width / session.window_height;
      const height = availableHeight - margin.top - margin.bottom;
      const width = height * aspectRatio;
      const button_radius = (session.button_size / 200) * height;
      const grace_radius =
        button_radius + (session.grace_radius / 200) * height;

      console.log("Height:", height);
      console.log("Width:", width);
      console.log("Button radius:", button_radius);

      svg.attr("width", width);
      svg.attr("height", height);

      const x = d3
        .scaleLinear()
        .domain([0, session.window_width])
        .range([margin.left, width + margin.left]);

      const y = d3
        .scaleLinear()
        .domain([0, session.window_height])
        .range([height - margin.bottom, margin.top]);

      svg
        .append("rect")
        .attr("x", x(0))
        .attr("y", y(session.window_height))
        .attr("width", x(session.window_width) - x(0))
        .attr("height", y(0) - y(session.window_height))
        .attr("fill", "none")
        .attr("stroke", "black");

      svg
        .selectAll(".peck-dot")
        .data(pecks)
        .enter()
        .append("circle")
        .attr("class", "peck-dot")
        .attr("cx", (d) => x(d.x_pos * session.window_width))
        .attr("cy", (d) => y(d.y_pos * session.window_height))
        .attr("r", 3)
        .attr("fill", "blue");

      // Add green circle without fill
      svg
        .append("circle")
        .attr("cx", x(0.7 * session.window_width))
        .attr("cy", y((session.button_height / 100) * session.window_height))
        .attr("r", button_radius)
        .attr("fill", "none")
        .attr("stroke", "green");

      // Add red circle if mode_id is 3 or 4
      if (session.mode_id === 3 || session.mode_id === 4) {
        svg
          .append("circle")
          .attr(
            "cx",
            x(
              (0.3 + session.warning_signal_position * 0.4) *
                session.window_width
            )
          )
          .attr("cy", y((session.button_height / 100) * session.window_height))
          .attr("r", button_radius)
          .attr("fill", "none")
          .attr("stroke", "red");
      }

      // Add dashed circles if grace_radius is greater than 0
      if (session.grace_radius > 0) {
        // Dashed circle around green circle
        svg
          .append("circle")
          .attr("cx", x(0.7 * session.window_width))
          .attr("cy", y((session.button_height / 100) * session.window_height))
          .attr("r", grace_radius)
          .attr("fill", "none")
          .attr("stroke", "green")
          .attr("stroke-dasharray", "4 2");

        // Dashed circle around red circle
        if (session.mode_id === 3 || session.mode_id === 4) {
          svg
            .append("circle")
            .attr(
              "cx",
              x(
                (0.3 + session.warning_signal_position * 0.4) *
                  session.window_width
              )
            )
            .attr(
              "cy",
              y((session.button_height / 100) * session.window_height)
            )
            .attr("r", grace_radius)
            .attr("fill", "none")
            .attr("stroke", "red")
            .attr("stroke-dasharray", "4 2");
        }
      }
    }
  }, [pecks, session]);

  return (
    <div
      id="pecks_distribution"
      ref={containerRef}
      style={{
        width: "100%",
        height: "100%",
        margin: "0 0",
        padding: "0 0",
        boxSizing: "border-box",
      }}
    >
      <svg
        id="pecks_distribution_svg"
        style={{
          width: "100%",
          height: "100%",
          margin: "0 0",
          padding: "0 0",
          boxSizing: "border-box",
        }}
      ></svg>
    </div>
  );
}

export default PecksDistribution;

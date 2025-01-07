import React, { useEffect, useRef } from "react";
import * as d3 from "d3";
import PecksDistribution from "./PecksDistribution";
import EventsTable from "./EventsTable";
import SessionInfo from "./SessionInfo";

function Tabs({
  activeTab,
  setActiveTab,
  events,
  session,
  pecks,
  getTableProps,
  getTableBodyProps,
  headerGroups,
  rows,
  prepareRow,
}) {
  const tabButtonsRef = useRef(null);
  const getButtonStyle = (tabName) => ({
    backgroundColor: activeTab === tabName ? "blue" : "transparent",
    color: activeTab === tabName ? "white" : "black",
  });

  useEffect(() => {
    const tabButtonsHeight = tabButtonsRef.current.clientHeight;
    const contentDiv = document.getElementById("tab_content");
    contentDiv.style.height = `calc(100% - ${tabButtonsHeight}px)`;
  }, []);

  return (
    <div
      style={{
        flex: 1,
        marginRight: "20px",
        overflow: "hidden",
        boxSizing: "border-box",
      }}
    >
      <div ref={tabButtonsRef}>
        <button
          onClick={() => setActiveTab("pecks_distribution")}
          style={getButtonStyle("pecks_distribution")}
        >
          Pecks Distribution
        </button>
        <button
          onClick={() => setActiveTab("events_table")}
          style={getButtonStyle("events_table")}
        >
          Events Table
        </button>
        <button
          onClick={() => setActiveTab("session_info")}
          style={getButtonStyle("session_info")}
        >
          Session Info
        </button>
      </div>
      <div
        id="tab_content"
        style={{
          overflowY: "auto",
          marginTop: "20px",
          width: "100%",
          height: "100%",
          boxSizing: "border-box",
        }}
      >
        {activeTab === "pecks_distribution" && (
          <PecksDistribution
            pecks={pecks}
            session={session}
            style={{
              width: "100%",
              height: "100%",
              marginTop: "20px",
              marginBottom: "20px",
              boxSizing: "border-box",
            }}
          />
        )}
        {activeTab === "events_table" && (
          <EventsTable
            getTableProps={getTableProps}
            getTableBodyProps={getTableBodyProps}
            headerGroups={headerGroups}
            rows={rows}
            prepareRow={prepareRow}
            style={{ width: "100%", height: "100%", boxSizing: "border-box" }}
          />
        )}
        {activeTab === "session_info" && session && (
          <SessionInfo
            session={session}
            style={{ width: "100%", height: "100%", boxSizing: "border-box" }}
          />
        )}
      </div>
    </div>
  );
}

export default Tabs;

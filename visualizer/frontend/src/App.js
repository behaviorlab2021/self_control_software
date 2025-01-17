import React, { useEffect, useState, useMemo, useRef } from "react";
import axios from "axios";
import socketIOClient from "socket.io-client";
import { useTable, useSortBy } from "react-table";
import { format } from "date-fns";
import CameraFeed from "./components/CameraFeed";
import Tabs from "./components/Tabs";
import CumulativeRecordChart from "./components/CumulativeRecordChart";

const ENDPOINT = "http://localhost:3001";

function App() {
  const [records, setRecords] = useState([]);
  const [events, setEvents] = useState([]);
  const [session, setSession] = useState(null);
  const [pecks, setPecks] = useState([]);
  const [activeTab, setActiveTab] = useState("pecks_distribution");
  const chartRef = useRef(null);
  const videoRef = useRef(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const recordsResponse = await axios.get(
          `${ENDPOINT}/cumulative_records`
        );
        setRecords(recordsResponse.data);

        const eventsResponse = await axios.get(`${ENDPOINT}/events`);
        setEvents(eventsResponse.data);

        const sessionResponse = await axios.get(`${ENDPOINT}/cur_session`);
        setSession(sessionResponse.data);

        const pecksResponse = await axios.get(`${ENDPOINT}/pecks`);
        setPecks(pecksResponse.data);
      } catch (error) {
        console.error("Error fetching data:", error);
      }
    };

    fetchData();

    const socket = socketIOClient(ENDPOINT);
    socket.on("newCumulativeRecord", (newRecord) => {
      setRecords((prevRecords) => [newRecord, ...prevRecords]);
    });

    socket.on("newEvent", async (newEvent) => {
      setEvents((prevEvents) => [newEvent, ...prevEvents]);
      if (newEvent.event_type === "new_round") {
        const pecksResponse = await axios.get(`${ENDPOINT}/pecks`);
        setPecks(pecksResponse.data);
      }
      if (newEvent.event_type === "session_start") {
        window.location.reload();
      }
    });

    socket.on("newPeck", (newPeck) => {
      setPecks((prevPecks) => [newPeck, ...prevPecks]);
    });

    const handleResize = () => {
      window.location.reload();
    };

    window.addEventListener("resize", handleResize);

    return () => {
      socket.disconnect();
      window.removeEventListener("resize", handleResize);
    };
  }, []);

  useEffect(() => {
    const bottomSection = document.querySelector(".bottom_section > div");
    if (bottomSection) {
      bottomSection.scrollLeft = bottomSection.scrollWidth;
    }
  }, [records, events, pecks]);

  const columns = useMemo(
    () => [
      {
        Header: "Hit Count",
        accessor: "hit_count",
      },
      {
        Header: "Type",
        accessor: "event_type",
      },
      {
        Header: "Time",
        accessor: "event_time",
        Cell: ({ value }) => format(new Date(value), "HH:mm:ss.S"),
      },
    ],
    []
  );

  const tableInstance = useTable({ columns, data: events }, useSortBy);

  const { getTableProps, getTableBodyProps, headerGroups, rows, prepareRow } =
    tableInstance;

  return (
    <div
      className="App"
      style={{
        padding: "0 40px",
        height: "100vh",
        display: "grid",
        gridTemplateRows: "10vh 45fr 40vh",
        boxSizing: "border-box", // Add this line
      }}
    >
      <div className="title_section" style={{ overflow: "hidden" }}>
        <h1>
          {session ? session.subject_name : ""} running{" "}
          {session ? session.mode_name : ""} -{" "}
          {session
            ? format(new Date(session.created_at), "EEEE dd MMMM yyyy HH:mm")
            : ""}
        </h1>
      </div>

      <div
        className="upper_section"
        style={{
          display: "flex",
          overflow: "hidden",
        }}
      >
        <CameraFeed
          videoRef={videoRef}
          style={{ height: "100%", width: "100%", boxSizing: "border-box" }} // Add boxSizing
        />
        <Tabs
          activeTab={activeTab}
          setActiveTab={setActiveTab}
          events={events}
          session={session}
          pecks={pecks}
          getTableProps={getTableProps}
          getTableBodyProps={getTableBodyProps}
          headerGroups={headerGroups}
          rows={rows}
          prepareRow={prepareRow}
          style={{ height: "100%" }} // Add boxSizing
        />
      </div>

      <div
        className="bottom_section"
        style={{
          width: "100%",
          height: "100%",
          display: "flex",
          flexDirection: "column",
          overflowX: "auto",
          boxSizing: "border-box", // Add this line
        }}
      >
        <h2 style={{ flex: "0 0 auto" }}>Cumulative Record</h2>
        <div
          style={{
            flex: "1 1 auto",
            height: "100%",
            overflowY: "hidden",
            overflowX: "auto",
            boxSizing: "border-box", // Add this line
          }}
        >
          <CumulativeRecordChart
            chartRef={chartRef}
            records={records}
            events={events}
            session={session}
            style={{ height: "100%", boxSizing: "border-box" }} // Add boxSizing
          />
        </div>
      </div>
    </div>
  );
}

export default App;

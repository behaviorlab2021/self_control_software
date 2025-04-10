const express = require("express");
const { Pool, Client } = require("pg");
const cors = require("cors");
const http = require("http");
const socketIo = require("socket.io");

const app = express();
const port = 3001;

app.use(cors());

const server = http.createServer(app);
const io = socketIo(server, {
  cors: {
    origin: "http://localhost:3000", // Replace with your frontend URL
    methods: ["GET", "POST"],
  },
});

const pool = new Pool({
  user: "postgres",
  host: "194.177.220.45",
  database: "self_control_db",
  password: "pigeon123!",
  port: 5432,
});

app.get("/pecks", async (req, res) => {
  try {
    const result = await pool.query(`
    SELECT * FROM pecks p
    WHERE p.round_id = (
        SELECT round_id FROM rounds
        ORDER BY started_at DESC
        LIMIT 1
    )
    ORDER BY peck_time DESC
    `);
    res.json(result.rows);
  } catch (err) {
    console.error(err);
    res.status(500).json({ error: "Internal Server Error" });
  }
});

app.get("/events", async (req, res) => {
  try {
    const result = await pool.query(`
      SELECT * FROM events e
      JOIN rounds r ON e.round_id = r.round_id
      WHERE r.session_id = (
          SELECT session_id FROM rounds
          ORDER BY started_at DESC
          LIMIT 1
      )
      ORDER BY e.event_time DESC
    `);
    res.json(result.rows);
  } catch (err) {
    console.error(err);
    res.status(500).json({ error: "Internal Server Error" });
  }
});

app.get("/cumulative_records", async (req, res) => {
  try {
    const result = await pool.query(`
      SELECT * FROM cumulative_record cr
      WHERE cr.session_id = (
          SELECT session_id FROM rounds
          ORDER BY started_at DESC
          LIMIT 1
      )
      ORDER BY cr.event_time DESC
    `);
    res.json(result.rows);
  } catch (err) {
    console.error(err);
    res.status(500).json({ error: "Internal Server Error" });
  }
});

app.get("/cur_session", async (req, res) => {
  try {
    const result = await pool.query(`
      SELECT * FROM sessions
      JOIN subjects s ON sessions.subject_id = s.subject_id
      JOIN experiment_modes em ON sessions.mode_id = em.mode_id
      ORDER BY created_at DESC
      LIMIT 1
    `);
    res.json(result.rows[0]);
  } catch (err) {
    console.error(err);
    res.status(500).json({ error: "Internal Server Error" });
  }
});

io.on("connection", (socket) => {
  console.log("New client connected");

  socket.on("disconnect", () => {
    console.log("Client disconnected");
  });
});

const client = new Client({
  user: "postgres",
  host: "194.177.220.45",
  database: "self_control_db",
  password: "pigeon123!",
  port: 5432,
});

client.connect();

client.query("LISTEN new_event");
client.query("LISTEN new_cumulative_record_event");
client.query("LISTEN new_peck");

client.on("notification", async (msg) => {
  const payload = JSON.parse(msg.payload);
  if (msg.channel === "new_event") {
    console.log("Received new_event notification:", payload); // Debug print
    io.emit("newEvent", payload);
  } else if (msg.channel === "new_cumulative_record_event") {
    console.log("Received new_cumulative_record_event notification:", payload); // Debug print
    io.emit("newCumulativeRecord", payload);
  } else if (msg.channel === "new_peck") {
    console.log("Received new_peck notification:", payload); // Debug print
    io.emit("newPeck", payload);
  }
});

server.listen(port, () => {
  console.log(`Server running on port ${port}`);
});

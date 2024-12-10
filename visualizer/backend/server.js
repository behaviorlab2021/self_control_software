const express = require('express');
const { Pool, Client } = require('pg');
const cors = require('cors');
const http = require('http');
const socketIo = require('socket.io');

const app = express();
const port = 3001;

app.use(cors());

const server = http.createServer(app);
const io = socketIo(server, {
    cors: {
        origin: "http://localhost:3000", // Replace with your frontend URL
        methods: ["GET", "POST"]
    }
});

const pool = new Pool({
    user: 'postgres',
    host: 'localhost',
    database: 'postgres',
    password: 'pigeon123!',
    port: 5432,
});

app.get('/events', async (req, res) => {
    try {
        const result = await pool.query('SELECT * FROM events');
        res.json(result.rows);
    } catch (err) {
        console.error(err);
        res.status(500).json({ error: 'Internal Server Error' });
    }
});

app.get('/cumulative_records', async (req, res) => {
    try {
        const result = await pool.query('SELECT * FROM cumulative_record');
        res.json(result.rows);
    } catch (err) {
        console.error(err);
        res.status(500).json({ error: 'Internal Server Error' });
    }
});

io.on('connection', (socket) => {
    console.log('New client connected');

    socket.on('disconnect', () => {
        console.log('Client disconnected');
    });
});

const client = new Client({
    user: 'postgres',
    host: 'localhost',
    database: 'postgres',
    password: 'pigeon123!',
    port: 5432,
});

client.connect();

client.query('LISTEN new_event');
client.query('LISTEN new_cumulative_recorder_event');

client.on('notification', async (msg) => {
    const payload = JSON.parse(msg.payload);
    console.log('Received new_event notification:', payload); // Debug print
    io.emit('newEvent', payload);
});

client.on('notification', async (msg) => {
    const payload = JSON.parse(msg.payload);
    console.log('Received new_cumulative_recorder_event notification:', payload); // Debug print
    io.emit('newCumulativeRecord', payload);
});

server.listen(port, () => {
    console.log(`Server running on port ${port}`);
});
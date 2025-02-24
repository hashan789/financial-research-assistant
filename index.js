require('dotenv').config();
const express = require('express');
const app = express();
const cors = require('cors');
const connection = require("./db");
const userRoutes = require("./routes/users");
const authRoutes = require("./routes/auth");
const azureRoutes = require("./routes/server");

const allowedOrigins = ['https://happy-tree-08fe0090f.4.azurestaticapps.net'];

connection();

app.use(express.json())

app.use(cors({
  origin: allowedOrigins,
  methods: ['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'],
  allowedHeaders: ['Content-Type', 'Authorization'],
  credentials: true
}));

// Handle preflight requests
app.options('*', cors({
  origin: allowedOrigins
}));

app.use("/api/auth",authRoutes)
app.use("/api/users",userRoutes)
app.use("/api/azure_data",azureRoutes)

const port = process.env.PORT || 8080;
app.listen(port, () => console.log(`Listening on port ${port}`));




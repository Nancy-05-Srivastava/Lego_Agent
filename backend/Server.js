 const express = require("express");
const cors = require("cors");

const app = express();

app.use(cors());
app.use(express.json());

app.get("/", (req, res) => {
  res.send("Backend is running 🚀");
});

app.post("/api/project", (req, res) => {

  const { repo, code, overview } = req.body;

  console.log("Repo:", repo);
  console.log("Code:", code);
  console.log("Overview:", overview);

  res.json({
    message: "Data received successfully"
  });

});

app.listen(5000, () => {
  console.log("Server running on port 5000");
});
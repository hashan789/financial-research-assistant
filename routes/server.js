const router = require("express").Router();
var axios = require('axios');

// API route to forward query to Python LLM service
router.post('/', async (req, res) => {
    const dataQuery = req.body;
    // const body = JSON.stringify({ query });
  
    try {
      const response = await axios.post('http://127.0.0.1:5000/process', { // Replace with your Python service URL
        dataQuery
      });
  
      // const data = await response.json();
      // console.log(body);
      res.send(response.data.response);
    } catch (error) {
      console.error('Error fetching from LLM service:', error);
      res.status(500).json({ message: 'Error processing query' });
    }
  
    // console.log(query);
    // res.send(req.body);
  });
  
module.exports = router  
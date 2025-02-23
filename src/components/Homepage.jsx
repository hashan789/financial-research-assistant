import React, { useState, useEffect } from 'react';
import axios from '../lib/axios';
import InputForm from './InputForm';
import ResponseDisplay from './ResponseDisplay';
import NavBar from './NavBar';
import styles from '../css/homepage.module.css'

function Homepage() {
  const [data, setData] = useState({
    company : '',
    query : ''
  });
  const [response, setResponse] = useState(null);
  const [error, setError] = useState('')

  const handleQuerySubmit = async (newData) => {
    setData(previousState => {
      return { ...previousState, company: newData.company, query: newData.query }
    });
    setError('')
    try{
      console.log(newData)
      const response = await axios.post("azure_data/",
        newData
      );
      // const data = await response.json();
      setResponse(response.data);
    }
    catch(err){
      // Handle specific error types
      if (err.code === 'ECONNABORTED') {
        setError('Request timed out. Please try again later.');
      } else if (err.response) {
        // Server responded with a status code outside the 2xx range
        setError(`${err.response.statusText}. Please try again later.`);
      } else if (err.request) {
        // Request was made, but no response received (network error)
        setError('Network Error: Failed to get a response from the server. Please try again later.');
      } else {
        // Something else happened
        setError('An unknown error occurred. Please try again later.');
      }
    }
  };

  useEffect(() => {
    // Simulate initial response (replace with actual LLM call later)
    if (!data.query) return;
    setResponse(`Your query "${data.query}" is being processed...`);
  }, [data.query]);

  return (
    <>
    <NavBar />
    <div className="App text-center">
      <h1 className={styles.color}><b>Financial Research Assistant</b></h1>
      <div className='d-block' ><InputForm onQuerySubmit={handleQuerySubmit} /></div>
      <br /><br/>
      {error && <div style={{ color: 'red' }}>{error}</div>}
      {response && <ResponseDisplay response={response} />}
    </div>
    </>
  );
}

export default Homepage;



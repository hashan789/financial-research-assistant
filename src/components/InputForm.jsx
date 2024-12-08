import React, { useState } from 'react';
import styles from '../css/inputform.module.css'

function InputForm({ onQuerySubmit }) {
  const [data, setData] = useState({
    company: '',
    query: ''
  });

  const handleInputChange = (event) => {
    setData(prevState => ({...prevState, [event.target.name]: event.target.value}));
    console.log(data);
  };

  console.log(data);

  const handleSubmit = async (event) => {
    event.preventDefault();
    await onQuerySubmit(data);
    setData({
      company : '',
      query : ''
    }); // Clear input after submit
  };

  return (
    <form onSubmit={handleSubmit} className={`${styles.top} 'form'}`}>
      <div className={styles.main_field}>
      <div className={styles.field} style={{ justifyContent : 'left' }}>
        <label htmlFor="company">Enter company name</label>
      </div>
      </div>
      <br/>
      <input id="company" name="company" value={data.company} onChange={handleInputChange} placeholder='ex:(keells,seylan bank,...)'/>
      <br/><br />
      <div className={styles.main_field}>
      <div className={styles.field} style={{ justifyContent : 'left' }}>
        <label htmlFor='query'>Enter your query</label>
      </div>
      </div>
      <br/>
      <input id="query" name="query" value={data.query} onChange={handleInputChange} />
      <br/><br />
      <div className={styles.main_field}>
      <div className={styles.field} style={{ justifyContent : 'right' }}>
        <button type="submit" className={styles.btn}>Submit</button>
      </div>
      </div>
    </form>
  );
}

export default InputForm
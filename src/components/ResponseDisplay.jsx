import React from 'react';
import styles from '../css/response.module.css';

function ResponseDisplay({ response }) {
  return (
    <div className={styles.response}>
      <p>{response}</p>
    </div>
  );
}

export default ResponseDisplay;

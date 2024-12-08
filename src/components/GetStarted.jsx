import React from 'react'
import styles from '../css/getStarted.module.css'
import { Link } from 'react-router-dom'
import NavBar from './NavBar'

export default function GetStarted() {
  return (
    <>
    <NavBar/>
      <div className={styles.box}>
       </div>
        <div className={styles.container_1}>
            <div className={styles.header1}>AI-powered Sri Lankan Market Research Assistant</div>
            <div className={styles.header2}>that provides you answers post analysing data from published CSE listed company annual reports.</div>
            <div>
                <Link to="/signup"><button className={styles.btn}>Get Started</button></Link>
            </div>
        </div>
    </>
  )
}

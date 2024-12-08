import React from 'react'
import styles from '../css/navbar.module.css'
import { Link, useNavigate } from 'react-router-dom'
import logo from '../images/fin assist.png'

export default function NavBar() {

  const navigate = useNavigate();

  const handleLogOut = (e) => {
    e.preventDefault();
    localStorage.removeItem("token");
    navigate("/");
  }

  return (
    <div className={styles.container}>
        <div className={styles.logo_box}>
            <Link to="/"><img src={logo} alt={logo} className={styles.logo}/></Link>
        </div>
        <div className={styles.btn_area}>
          <Link to="/login"><button type="submit" className={styles.nav_btn}>Log in</button></Link>
          <Link to="/signup"><button type="submit" className={styles.nav_btn}>Sign up</button></Link>
          <button type="submit" className={styles.nav_btn} onClick={handleLogOut}>Log out</button>
        </div>
    </div>
  )
}

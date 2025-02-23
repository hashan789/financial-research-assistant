import React, { useState } from 'react'
import axios from 'axios'
import { Link, useNavigate } from 'react-router-dom'
import styles from '../css/login.module.css'
import NavBar from './NavBar'

export default function Login() {

  const [data, setData] = useState({
    email : "",
    password : ""
  })

  const [error, setError] = useState("");

  const handleChange = ({currentTarget : input}) => {
    setData({...data, [input.name] : input.value})
  }

  const navigate = useNavigate()

  const handleSubmit = async (e) => {
    e.preventDefault();

    try{
      const url = "https://happy-tree-08fe0090f.4.azurestaticapps.net/api/auth";
      const { data: res } = await axios.post(url , data);
      localStorage.setItem("token", res.data);
      navigate("/homepage");
      console.log(res.message);
    }
    catch (error){
      if (error.response && error.response.status >= 400 && error.response.status <= 500){
        setError(error.response.data.message)
      }

    }
  }

  return (
    <div className={styles.container}>
       <NavBar />

      <div className={styles.box_con}>
        <div>
        <h3 style={{ textAlign : 'center' }}>Log in</h3>
        <div>
          <form onSubmit={handleSubmit}>
              <label htmlFor="email">Email</label><br />
              <input 
                type='email'
                name="email" 
                id="email"
                placeholder='email'
                required
                onChange={handleChange}
                value={data.email}
                className={styles.input}
              /><br /><br />
              <label htmlFor="password">Password</label><br />
              <input type="password" 
                name="password" 
                id="password"
                placeholder='password'
                required
                onChange={handleChange}
                value={data.password}
                className={styles.input}/><br /><br />
              { error && <div className={styles.error}>{error}</div> }
              <button type="submit" className={ `${styles.input} , ${styles.btn}` }>Log in</button>
          </form>
        </div>
        <div className={styles.box_con} style={{ textAlign : 'center' }}>
        <div>
        <h6>Don't you have an account?</h6>
        <Link to="/signup">
          <button type="button" className={`${styles.btn} , ${styles.input}`}>Sign up</button>
        </Link>
        </div>
       </div>
        </div>
      </div>

       {/* <div className={styles.box}></div>
       <div className={styles.box_con}>
       <div className={styles.color_box}>
       <h1>Log in</h1>
       <div className={styles.bottom}>
        <br />
        <h5>Don't you have an account?</h5>
        <Link to="/signup">
          <button type="button" className={styles.btn}>Sign up</button>
        </Link>
       </div>
       </div>
       <div>
       <form onSubmit={handleSubmit}>
          <label htmlFor='email'>Email</label><br /><br />
          <input 
          type='email'
          name="email" 
          id="email"
          placeholder='email'
          required
          onChange={handleChange}
          value={data.email}
          className={styles.input}
         /> <br /> <br />
         <label htmlFor='password'>Password</label><br /><br />
          <input 
          type="password" 
          name="password" 
          id="password"
          placeholder='password'
          required
          onChange={handleChange}
          value={data.password}
          className={styles.input}
         /> <br /> <br />
         { error && <div className={styles.error}>{error}</div> }
         <button type="submit" className={styles.btn}>Log in</button>
       </form>
       </div>
      </div> */}
    </div>
  )
}

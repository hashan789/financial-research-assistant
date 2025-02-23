import React, { useState } from 'react'
import axios from '../lib/axios'
import { Link , useNavigate } from 'react-router-dom'
import styles from '../css/signup.module.css'
import NavBar from './NavBar'

export default function Signup() {

  const [data, setData] = useState({
    firstName : "",
    lastName : "",
    email : "",
    password : ""
  })

  const [error, setError] = useState("");
  const [state, setState] = useState("");

  const handleChange = ({currentTarget : input}) => {
    setData({...data, [input.name] : input.value})
    setState('')
    console.log(data)
  }

  const navigate = useNavigate()

  const handleSubmit = async (e) => {
    e.preventDefault();

    try{
      const url = "users";
      const { data: res } = await axios.post(url , data);
      navigate("/login");
      console.log(res.message);
    }
    catch (error){
      if (error.response && error.response.status >= 400 && error.response.status <= 500){
        setError(error.response.data.message)
        console.log(error)
      }
      else{
        console.log(error)
      }

    }
  }

  return (
    <div className={styles.container}>
      <NavBar />

      <div className={styles.box_con}>
        <div>
        <h3 style={{ textAlign : 'center' }}>Sign up</h3>
        <div>
          <form onSubmit={handleSubmit}>
              <label htmlFor="">First name</label><br />
              <input type="text" 
                name="firstName" 
                id="firstName"
                placeholder='first name'
                required
                onChange={handleChange}
                value={data.firstName}
                className={styles.input}/><br /><br />
              <label htmlFor="">Last name</label><br />
              <input type="text" 
                name="lastName" 
                id="lastName"
                placeholder='last name'
                required
                onChange={handleChange}
                value={data.lastName}
                className={styles.input}/><br /><br />
              <label htmlFor="">Email</label><br />
              <input type="email" 
                name="email" 
                id="email"
                placeholder='email'
                required
                onChange={handleChange}
                value={data.email}
                className={styles.input}
              /><br/><br />
              <label htmlFor="">Password</label><br />
              <input type="password" 
                name="password" 
                id="password"
                placeholder='password'
                required
                onChange={handleChange}
                value={data.password}
                className={styles.input}/><br /><br />
              { error && <div className={styles.error}>{error}</div> }
              <button type="submit" className={ `${styles.input} , ${styles.btn}` }>Sign up</button>
          </form>
        </div>
        <div className={styles.error}>{error}</div>
         {state && <div className={styles.container}><div className={styles.state}>{state}</div></div>}
         {/* <br/> */}
        <div className={styles.box_con} style={{ textAlign : 'center' }}>
        {/* <div> */}
        <h6>Do you have an account?</h6>
        <Link to="/login">
          <button type="button" className={`${styles.btn} , ${styles.more_btn} `}>Log in</button>
        </Link>
        {/* </div> */}
       </div>
        </div>
      </div>

      {/* <div className={styles.box}></div>
      <div className={styles.box_con}>
        <div className={styles.color_box}>
       <h1>Sign up</h1>
       <br/>
       <div className={styles.bottom}>
       <h5>Do you have an account?</h5>
        <Link to="/login">
          <button type="button" className={styles.btn}>Log in</button>
        </Link>
        </div>
        </div>
       <div>
       <form onSubmit={handleSubmit}>
       <label htmlFor='firstName'>First name</label><br /><br />
         <input 
          type="text" 
          name="firstName" 
          id="firstName"
          placeholder='first name'
          required
          onChange={handleChange}
          value={data.firstName}
          className={styles.input}
         /><br/><br />
         <label htmlFor='lastName'>Last name</label><br /><br />
         <input 
          type="text" 
          name="lastName" 
          id="lastName"
          placeholder='last name'
          required
          onChange={handleChange}
          value={data.lastName}
          className={styles.input}
         /><br/><br />
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
         <div className={styles.error}>{error}</div>
         {state && <div className={styles.container}><div className={styles.state}>{state}</div></div>}
         <br/>
         <button type="submit" className={styles.btn}>Sign up</button>
       </form>
       <br />
       </div>
       </div> */}
    </div>
  )
}

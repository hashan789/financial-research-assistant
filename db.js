const mongoose = require("mongoose");
const dotenv = require("dotenv");

dotenv.config();

module.exports = () => {
    const connectionParams = {
        useNewUrlParser : true,
        useUnifiedTopology : true,

    }
    try{
       mongoose.connect(process.env.MONGO_URI);
       console.log("Connected to database successfully")
    }
    catch(error){
        console.log(error)
        console.log("Could not connect to database")
    }
}
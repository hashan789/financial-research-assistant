const router = require("express").Router();

router.get("/", async (req,res) => {
    return res.json({ message : "Welcome to financial research assistant" });

})

module.exports = router;


import {initLogMessageBtns, parseDetail, setLogMessage, validateEmail} from "./base.js"

window.addEventListener("DOMContentLoaded", () => {
    const hashKeyInp = document.querySelector("#hash-key")
    const hashTypeInp = document.querySelector("#hash-type")

    const hashKey = hashKeyInp.value
    const hashType = hashTypeInp.value

    hashKeyInp.remove()
    hashTypeInp.remove()

    initLogMessageBtns()

    document.querySelector("#go-to-sign").addEventListener("click", () => goToForm("sign"))
    document.querySelector("#go-to-auth").addEventListener("click", () => goToForm("auth"))

    document.querySelector("#sign-btn").addEventListener("click", async () => {
        try {
            const res = await signUser(hashKey, hashType)
            setLogMessage(res, "alert-success")
            window.location.replace("/show_user/me")
        } catch (error) {
            setLogMessage(error.message, "alert-danger")
        }
    })
    document.querySelector("#auth-btn").addEventListener("click", async () => {
        try {
            const res = await authUser(hashKey, hashType)
            setLogMessage(res, "alert-success")
            window.location.replace("/show_user/me")
        } catch (error) {
            setLogMessage(error.message, "alert-danger")
        }
    })
})

function goToForm(form) {
    const signForm = document.querySelector("#sign-form")
    const authForm = document.querySelector("#auth-form")

    if (form === "auth") {
        signForm.setAttribute("hidden", "hidden")
        authForm.removeAttribute("hidden")
    } else if (form === "sign") {
        signForm.removeAttribute("hidden")
        authForm.setAttribute("hidden", "hidden")
    }
}

async function signUser(hashKey, hashType) {
    const email = document.querySelector("#sign-email").value.trim()
    const username = document.querySelector("#sign-username").value.trim()
    const password = document.querySelector("#sign-password").value.trim()
    const confPassword = document.querySelector("#sign-password-confirm").value.trim()

    if (username.length < 8 || username.length > 32)
        throw Error("Username should be >8 and <32")

    if (!validateEmail(email))
        throw Error("Email is not correct")

    if (password.length < 8 || password.length > 32)
        throw Error("Password should be >8 and <32")

    if (password !== confPassword)
        throw Error("Passwords sould be matched")

    // const hashedPassword = jwt.verify(password, hashKey, {algorithms: [hashType]})
    
    const res = await fetch("/api/users/me/sign", {
        method: "POST",
        headers: {
            "Accept": "application/json",
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            email: email,
            username: username,
            password: password
        })
    })
    const response = await res.json()

    if (!res.ok)
        throw Error(parseDetail(response["detail"]))

    return response["detail"]
}


async function authUser(hashKey, hashType) {
    const email = document.querySelector("#auth-email").value.trim()
    const password = document.querySelector("#auth-password").value.trim()

    if (!validateEmail(email))
        throw Error("Email is not correct")

    if (password.length < 8 || password.length > 32)
        throw Error("Password should be >8 and <32")

    // const hashedPassword = jwt.verify(password, hashKey, {algorithms: [hashType]})

    const res = await fetch("/api/users/me/auth", {
        method: "POST",
        headers: {
            "Accept": "application/json",
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            email: email,
            password: password
        })
    })
    const response = await res.json()

    if (!res.ok)
        throw Error(parseDetail(response["detail"]))

    return response["detail"]
}
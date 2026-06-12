import {initLogMessageBtns, setLogMessage, validateEmail} from "./base.js"

window.addEventListener("DOMContentLoaded", () => {
    const toMeBtn = document.querySelector("#requests-to-me-btn")
    const toMyBtn = document.querySelector("#my-requests-btn")

    toMeBtn.addEventListener("click", () => {
        const fromMeForm = document.querySelector("#my-requests")
        fromMeForm.setAttribute("hidden", "hidden")

        const toMeForm = document.querySelector("#requests-to-me")
        toMeForm.removeAttribute("hidden")

        toMeBtn.classList.replace("text-secondary", "text-primary")
        toMyBtn.classList.replace("text-primary", "text-secondary")
    })
    toMyBtn.addEventListener("click", () => {
        const toMeForm = document.querySelector("#requests-to-me")
        toMeForm.setAttribute("hidden", "hidden")

        const fromMeForm = document.querySelector("#my-requests")
        fromMeForm.removeAttribute("hidden")

        toMyBtn.classList.replace("text-secondary", "text-primary")
        toMeBtn.classList.replace("text-primary", "text-secondary")
    })

    document.querySelectorAll(".approve-request-btn").forEach(el => el.addEventListener("click", async (event) => {
        console.log(event.target.id)
        const requestId = event.target.id.split("-").pop()

        const res = await fetch(`/api/requests/${requestId}/approve`, {method: "POST"})
        const response = await res.json()

        if (!res.ok) {
            setLogMessage(parseDetail(response["detatil"]), "alert-danger")
        } else {
            document.querySelector(`#request-${requestId}`).remove()
            setLogMessage("Friend was added", "alert-success")
        }
    }))
    document.querySelectorAll(".decline-request-btn").forEach(el => el.addEventListener("click", async (event) => {
        const requestId = event.target.id.split("-").pop()

        const res = await fetch(`/api/requests/${requestId}/decline`, {method: "POST"})
        const response = await res.json()

        if (!res.ok) {
            setLogMessage(parseDetail(response["detatil"]), "alert-danger")
        } else {
            document.querySelector(`#request-${requestId}`).remove()
            setLogMessage("Request was declined", "alert-success")
        }
    }))
})
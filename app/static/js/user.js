import {initLogMessageBtns, parseDetail, setLogMessage, validateEmail} from "./base.js"

window.addEventListener("DOMContentLoaded", () => {
    initLogMessageBtns()
    initUpdFormBtns()
    initDltFormBtns()
    initSendRequestBtns()
    initUpdDayFormBtns()
    initFriendRemoveBtn()

    const openInfoViewBtn = document.querySelector("#change-info-btn")
    const quitBtn = document.querySelector("#quit-btn")
    const openDeleteViewBtn = document.querySelector("#open-delete-form-btn")
    const openReqFormBtn = document.querySelector("#open-req-form-btn")

    openDeleteViewBtn.addEventListener("click", () => {
        document.querySelector("#dlt-user-form").removeAttribute("hidden")
    })
    openInfoViewBtn.addEventListener("click", () => {
        document.querySelector("#load-photo-form").removeAttribute("hidden")
    })
    quitBtn.addEventListener("click", async () => {
        const res = await fetch("/api/users/me/quit", {method: "POST"})
        const response = await res.json()

        if (!res.ok) {
            setLogMessage(parseDetail(response["detail"]), "alert-danger")
        } else {
            window.location.replace("/")
        }
    })
    openReqFormBtn.addEventListener("click", () => {
        document.querySelector("#req-form").removeAttribute("hidden")
    })
})

function initUpdFormBtns() {
    const updateUserPhotoBtn = document.querySelector("#upd-user-photo-btn")
    const closeUpdFormBtn = document.querySelector("#close-upd-form-btn")

    updateUserPhotoBtn.addEventListener("click", async () => {
        const file = document.querySelector("#upd-photo").files[0]
        const form = new FormData()

        form.append("file", file)

        const res = await fetch("/api/users/me/photo/upload", {
            method: "POST",
            // headers: {
            //     "Accept": "application/json",
            //     "Content-Type": "application/json"
            // },
            body: form
        })
        const response = await res.json()

        if (!res.ok){
            setLogMessage(parseDetail(response["detail"]), "alert-danger")
        } else {
            setLogMessage("Photo was downloaded", "alert-success")
            await setTimeout("", 5000)

            window.location.reload()
        }
    })
    closeUpdFormBtn.addEventListener("click", () => {
        document.querySelector("#load-photo-form").setAttribute("hidden", "hidden")
    })
}

function initDltFormBtns() {
    const quitBtn = document.querySelector("#not-delete-btn")
    const dltBtn = document.querySelector("#delete-btn")

    quitBtn.addEventListener("click", () => {
        document.querySelector("#dlt-user-form").setAttribute("hidden", "hidden")
    })
    dltBtn.addEventListener("click", async () => {
        const res = await fetch("/api/users/me", {method: "DELETE"})
        const response = await res.json()

        if (!res.ok) {
            setLogMessage(parseDetail(response["detail"]), "alert-danger")
        } else {
            setLogMessage("User was deleted", "alert-success")
            await setTimeout("", 5000)

            window.location.reload()
        }
    })
}

function initSendRequestBtns() {
    const closeReqFromBtn = document.querySelector("#close-req-form-btn")
    const sendReqBtn = document.querySelector("#send-req-btn")

    closeReqFromBtn.addEventListener("click", () => {
        document.querySelector("#req-form").setAttribute("hidden", "hidden")
    })

    sendReqBtn.addEventListener("click", async () => {
        const emailInp = document.querySelector("#req-user-email")
        const email = emailInp.value

        if (!validateEmail(email)) {
            setLogMessage("invalid email. rewrite it", "alert-danger")
            return
        }

        const res = await fetch("/api/requests/", {
            method: "POST",
            headers: {
                "Accept": "application/json",
                "Content-Type": "application/json"
            },
            body: JSON.stringify({to: {email: email}})
        })
        const response = await res.json()

        if (!res.ok) {
            setLogMessage(parseDetail(response["detail"]), "alert-danger")
        } else {
            setLogMessage("request was sent", "alert-success")
            emailInp.value = ""
        }
    })
}

function initUpdDayFormBtns() {
    document.querySelectorAll(".upd-day-btn").forEach(el => {
        el.addEventListener("click", async (event) => {
            const dayId = event.target.id.split("-").pop()

            const descripton = document.querySelector(`#description-${dayId}`).value
            const reaction = document.querySelector(`#reaction-${dayId}`).value
            const photo = document.querySelector(`#photo-${dayId}`).files[0]

            const res = await fetch(`/api/days/${dayId}`, {
                method: "PUT",
                headers: {
                    "Accept": "application/json",
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({description: descripton, reaction: reaction})
            })
            const response = await res.json()

            if (!res.ok){
                setLogMessage(parseDetail(response["detail"]), "alert-danger")
                return
            }

            if (photo) {
                const form = new FormData()
                form.append("file", photo)

                const resPhoto = await fetch(`/api/days/${dayId}/photo/upload`, {
                    method: "POST",
                    body: form
                })
                const responsePhoto = await resPhoto.json()

                if (!resPhoto.ok) {
                    setLogMessage(responsePhoto["detail"], "alert-danger")
                    return
                }
            }

            setLogMessage("Data was updated", "alert-success")
            await setTimeout("", 5000)

            window.location.reload()
        })
    })
    document.querySelectorAll(".close-day-btn").forEach(el => {
        el.addEventListener("click", (event) => {
            const dayId = event.target.id.split("-").pop()

            document.querySelector(`#day-form-${dayId}`).setAttribute("hidden", "hidden")
        })
    })
    document.querySelectorAll(".open-preview-day").forEach(el => {
        el.addEventListener("click", (event) => {
            const dayId = event.target.id.split("-").pop()  

            document.querySelector(`#day-form-${dayId}`).removeAttribute("hidden")
        })
    })
    document.querySelectorAll(".dlt-day-btn").forEach(el => {
        el.addEventListener("click", async (event) => {
            const dayId = event.target.id.split("-").pop()

            const res = await fetch(`/api/days/${dayId}`, {method: "DELETE"})
            const response = await res.json()

            if (!res.ok) {
                setLogMessage(parseDetail(response["detail"]), "alert-danger")
                return
            }

            setLogMessage("day was deleted", "alert-success")
            await setTimeout("", 5000)
            
            window.location.reload()
        })
    })
}

function initFriendRemoveBtn() {
    document.querySelectorAll(".rm-fr-btn").forEach(el => {
        el.addEventListener("click", async (event) => {
            const friendId = event.target.id.split("-").pop()

            const res = await fetch(`/api/users/me/friends/${friendId}`, {method: "DELETE"})
            const response = await res.json()

            if (!res.ok) {
                setLogMessage(parseDetail(response["detail"]), "alert-danger")
            } else {
                setLogMessage("Friend was removed...", "alert-success")
                document.querySelector(`#friend-container-${friendId}`).remove()
            }
        })
    })
}
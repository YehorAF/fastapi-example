import {initLogMessageBtns, setLogMessage, validateEmail} from "./base.js"

window.addEventListener("DOMContentLoaded", () => {
    initLogMessageBtns()
    const params = parseUrlParams()

    console.log(params)

    const limit = Number(params.get("limit") || 20)
    const reactions = params.get("reactions") || ["awful", "bad", "normal", "good", "awesome"]
    const minTimestamp = params.get("min_timestamp") || NaN
    const maxTimestamp = params.get("max_timestamp") || NaN

    setUrlParamsToFilter(limit, reactions, minTimestamp, maxTimestamp)

    const currentSkip = Number(params.get("skip") || 0)
    const prevSkip = currentSkip - limit
    const nextSkip = currentSkip + limit

    document.querySelector("#previous-days").setAttribute(
        "href", 
        createUrl({
            base: "/show_days", 
            skip: prevSkip,
            limit: limit,
            minTimestamp: minTimestamp,
            maxTimestamp: maxTimestamp,
            reactions: reactions
        }
    ))
    document.querySelector("#next-days").setAttribute(
        "href",
        createUrl({
            base: "/show_days", 
            skip: nextSkip,
            limit: limit,
            minTimestamp: minTimestamp,
            maxTimestamp: maxTimestamp,
            reactions: reactions
        })
    )

    document.querySelector("#use-filters").addEventListener("click", () => {
        const filterLimit = document.querySelector("#limit").value
        const filterMinTimestamp = document.querySelector("#min-timestamp").value
        const filterMaxTimestamp = document.querySelector("#max-timestamp").value
        const filterReactions = []

        document.querySelectorAll(".reaction-inp").forEach(el => {
            if (el.checked)
                filterReactions.push(el.value)
        })

        window.location.href = createUrl({
            base: "/show_days", 
            skip: 0,
            limit: filterLimit,
            minTimestamp: filterMinTimestamp,
            maxTimestamp: filterMaxTimestamp,
            reactions: filterReactions
        })
    })
})

function setUrlParamsToFilter(limit, reactions, minTimestamp, maxTimestamp) {
    document.querySelector("#limit").value = limit
    document.querySelector("#min-timestamp").value = minTimestamp
    document.querySelector("#max-timestamp").value = maxTimestamp
    
    document.querySelectorAll(".reaction-inp").forEach(el => el.checked = false)
    if (Array.isArray(reactions))
        reactions.forEach(
            el => document.querySelector(`#reaction-${el}`).checked = true)
}

function parseUrlParams() {
    const routers = window.location.href.split("/")
    const params = routers.at(routers.length - 1).split(/(\?|\&|#)/)
    const paramMap = new Map()

    params.forEach(el => {
        if (el.includes("=")) {
            const [k, v] = el.split("=")
            if (paramMap.has(k))
                paramMap.get(k).push(v)
            else
                paramMap.set(k, [v])
        }
    })

    for (const [k, v] of paramMap.entries()) {
        if (v.length < 2)
            paramMap.set(k, v.at(0))
    }

    // paramMap.forEach((k, v) => {
    //     if (v.length < 2)
    //         v = v.at(0)
    // })

    return paramMap
}

function createUrl({
    base,
    skip = 0, 
    limit = 20, 
    minTimestamp = NaN, 
    maxTimestamp = NaN, 
    reactions = NaN
}) {
    const params = []

    if (Array.isArray(reactions))
        reactions.forEach(el => params.push(`reactions=${el}`))
    else if (reactions)
        params.push(`reactions=${reactions}`)

    params.push(`skip=${skip || 0}`)
    params.push(`limit=${limit || 20}`)
    
    if (minTimestamp)
        params.push(`min_timestamp=${new Date(minTimestamp).toISOString()}`)

    if (maxTimestamp)
        params.push(`max_timestamp=${new Date(maxTimestamp).toISOString()}`)

    return `${base}?${params.join('&')}`
}
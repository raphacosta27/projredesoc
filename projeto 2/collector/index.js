// @ts-check
const { google } = require('googleapis')
const util = require('util')
const fs = require('fs')
const keypress = require('keypress')
const print = console.log
const KEY = 'AIzaSyAJAwDCuxdoaUOmPObTU_SNYu3OfhKSAvc'
const youtube = google.youtube('v3')
const SUB_LIMIT = 5000000
keypress(process.stdin);
const categories = require('./categories')
let running = true


const file = fs.openSync('./output.gml', 'a')
/** @typedef {{source: string, target: string}} Edge - creates a new type named 'SpecialType' */
/** @type {{directed: 1 | 0, nodes: {}, edges: Edge[]}} */
const graph = {
    directed: 1,
    nodes: {},
    edges: []
}

const history = []

// auto-increment counter
let counter = 0

const fetchChannel = async (id) => {
    const res = await youtube.channels.list({
        id: id,
        auth: KEY,
        part: 'snippet, brandingSettings, statistics, topicDetails'
    })

    // console.log(util.inspect(res.data, false, null, true /* enable colors */))
    if (res.data.pageInfo.totalResults > 0) {
        // print(res.data.items[0])
        return res.data.items[0]
    } else {
        return null
    }
}

const traverse = async (currentId) => {
    try {
        let data = await fetchChannel(currentId)

        if (data === null || data.brandingSettings === null || data.brandingSettings === undefined || !data) {
            console.log('Unexpected problem when traversing', currentId)
            return []
        }

        // Node has no children!!, return empty array
        if (data.brandingSettings.channel.featuredChannelsUrls === undefined) {
            print('Channel', currentId, 'has no chidren or some other problem!')
            return []
        }

        let children = data.brandingSettings.channel.featuredChannelsUrls
        let subCount = parseInt(data.statistics.subscriberCount)

        if (data.id !== currentId) {
            throw 'IDS UNMATCHED!'
        }

        // cria o nó
        graph.nodes[data.id] = {
            id: data.id,
            visited: 1,
            title: data.snippet.title,
            country: data.snippet.country,
            publishedAt: data.snippet.publishedAt,
            ...data.statistics,
            topics: data.topicDetails.topicIds,
            counterId: counter
        }

        counter++

        if (!running) {
            return []
        }



        let childData = await youtube.channels.list({
            auth: KEY,
            id: data.brandingSettings.channel.featuredChannelsUrls.join(','),
            part: 'statistics'
        })

        if (childData.data.pageInfo.totalResults !== children.length) {
            throw 'CHILDREN DATA LENGTH MISTMATCHED FEATURED LENGTH'
        }

        childData.data.items.forEach((child, index) => {
            let childSubCount = parseInt(child.statistics.subscriberCount)

            if (childSubCount > SUB_LIMIT) {
                graph.edges.push({
                    source: currentId,
                    target: child.id
                })

                if (child.id in graph.nodes && graph.nodes[child.id].visited) {
                    // Se o filho ja existe e foi visitado remove ele da lista de filhos dessa visita
                    children = children.filter((childId) => childId !== child.id)
                } else {
                    graph.nodes[child.id] = {
                        visited: 0,
                    }
                }
            } else {
                // console.log('channel', child.id, 'has less than 1kk')
                children = children.filter((childId) => childId !== child.id)
            }
        })

        return children
    } catch (error) {
        console.log('Unexpected error ocurred', error)
        return []
    }
}

const validateGraph = (graph) => {
    return graph.edges.every((e) => {
        return (
            (e.source in graph.nodes) &&
            (e.target in graph.nodes) &&
            (graph.nodes[e.source].visited) &&
            (graph.nodes[e.target].visited)
        )
    }) && Object.values(graph.nodes).every(e => e.visited)
}

const createGraph = async (channelId) => {
    let queue = [channelId]
    while (queue.length > 0) {
        let first = queue.shift()
        let children = await traverse(first)
        console.log('queue length:', queue.length, 'visiting', first, 'added', children.length)
        queue = queue.concat(children)
        history.push(first)
    }

    if (queue.length == 0) {
        console.log('Queue is empty! Its over')
        if (validateGraph(graph)) {
            console.log('GRAPH IS VALID')
        } else {
            console.log('INVALID GRAPH')
        }
    }


    if (!running) {
        console.log('Stopped manually')
    }

}

// let startingId = 'UCDlQwv99CovKafGvxyaiNDA'
// let startingId = 'UCOOCeqi5txwviDZ4M5W9QSg' // nando moura
// let startingId = 'UCYzPXprvl5Y-Sf0g4vX-m6g'
// let startingId = 'UCdTWvzwNIeZxSNZ_oWvnBbQ' // lucao
// let startingId = 'UCXuqSBlHAE6Xw-yeJA0Tunw' // ltt
// let startingId = 'UCsTcErHg8oDvUnTzoqsYeNw' // unbox therapy termina rapido
// let startingId = 'UC-lHJZR3Gqxm24_Vd_AJ5Yw' // pewdiepie nao inidica ninguem
// let startingId = 'UCYzPXprvl5Y-Sf0g4vX-m6g' // jackse nao termina
// let startingId = 'UCV306eHqgo0LvBf3Mh36AHg' //felipe neto
let startingId = 'UC3KQ5GWANYF8lChqjZpXsQw' //whindersson



const getVideo = async () => {
    let video = await youtube.videos.list({
        id: 'x9_us95MMr8',
        part: 'snippet',
        maxResults: 10,
        auth: KEY
    })
    print(video.data.items)
}

/**
 * @param {typeof graph} [json] - Somebody's name.
 */

const getNodeText = (node) => {
    let s = '  node [\n'
    for ([k, v] of Object.entries(node)) {
        if (v.constructor === Object) {
            s += `    ${k} [ `
            for ([k2, v2] of Object.entries(v)) {
                s += (typeof v2 === 'string' ? `${k2} "${v2}" ` : `${k2} ${v2} `)
            }
            s += `]\n`
        } else if (v.constructor === Array) {
            let c = 0
            let deduped = v.filter((item, index, self) => self.indexOf(item) == index);
            print(deduped)
            s += `    ${k} [ `
            for ([k2, v2] of Object.entries(deduped)) {
                s += `n${c} `
                s += k === 'topics' ? `"${categories[v2]}"` + ' ' : `${v2} `
                c++
            }
            s += `]\n`

        } else if (v.constructor === Boolean) {
            s += (v === true ? `    ${k} 1` : `${k} 0`)
            s += `\n`
        }
        else {
            s += (typeof v === 'string' ? `    ${k} "${v}" ` : `    ${k} ${v}`) + '\n'
        }

    }
    s += '  ]\n'
    return s
}

/**
 * @param {typeof graph} [graphJson] - Somebody's name.
 */
const writeGml = (graphJson) => {
    print('Writing gml')
    try {
        fs.unlinkSync('./output.gml')
    } catch (error) {
        console.log(error)
    }

    const outputFile = fs.openSync('./output.gml', 'a+')
    fs.writeSync(outputFile, 'graph [\n')
    fs.writeSync(outputFile, `  directed ${graphJson.directed}\n`)
    // @ts-ignore
    for ([k, v] of Object.entries(graphJson.nodes)) {
        if (v.visited) {
            fs.writeSync(outputFile, getNodeText(v))
        } else {
            console.log(k, 'wasnt visited, not writing')
        }

    }

    graphJson.edges.forEach(e => {
        fs.writeSync(outputFile, `  edge [
    source "${e.source}"
    target "${e.target}"
]\n`)
    })
    print('Finished writing')
}

createGraph(startingId)

process.stdin.resume();

process.stdin.on('keypress', function (ch, key) {
    if (key && key.name == 's') {
        running = false
        print('stopped running, wait for queue to empty')
    }
    if (key && key.name == 'p') {
        print(graph)
    }
    if (key && key.name == 'w') {
        fs.writeFileSync('graph.json', JSON.stringify(graph))
        print('Graph written to graph.json')
        print('Writing GML')

        /** @type {typeof graph}} */
        let json = JSON.parse(fs.readFileSync('./graph.json').toString())
        writeGml(json)
    }
})

process.on('SIGINT', () => {
    console.info('SIGTERM signal received.')
    // print(graph)
    process.exit(0)
})
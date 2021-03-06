from elasticsearch import Elasticsearch
from collections import defaultdict, OrderedDict, Set
import operator

QUERIES = {"152501": "recent immigration order obama",
           "152502": "immigration 20th century",
           "152503": "illegal immigration"}

es = Elasticsearch()


def getResult(query, indexName, type):
    documentSet = set()

    try:
        res = None
        try:
            res = es.search(index=indexName, doc_type=type, _source_include=['docno', 'url', 'grade'], body={
                "query": {
                    "match": {
                        "text": query
                    }
                },
                "sort": [
                    "_score"
                ],
                'size': 1000
            })
        except Exception, e:
            print e

        resultRankedListDict = defaultdict(lambda: 0.0)
        for hit in res['hits']['hits']:
            docno = str(hit['_source']['docno'].encode('utf-8', 'ignore'))
            normaldocNo = docno.lower()
            if normaldocNo not in documentSet:
                if len(documentSet) == 1000:
                    break
                resultRankedListDict[docno] = float(hit['_score'])
                documentSet.add(normaldocNo)

        return resultRankedListDict


    except Exception, e:
        print e


def writeRankedList(resultDict, topicID):
    rank = 1
    with open('result_1000.txt', 'a+') as f:
        for docId, score in resultDict.iteritems():
            f.write(str(topicID) + '<:>Q0<:>' + docId + '<:>' + str(rank) + '<:>' + str(score) + '<:>Exp\n')
            rank += 1


if __name__ == '__main__':
    for topicID in QUERIES:
        print topicID
        result = getResult(str(QUERIES[topicID]), 'mi', 'document')
        writeRankedList(OrderedDict(sorted(result.iteritems(), key=operator.itemgetter(1), reverse=True)), topicID)

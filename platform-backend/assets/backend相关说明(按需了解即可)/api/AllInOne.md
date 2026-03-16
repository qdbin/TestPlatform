# AutoTest API
Version |  Update Time  | Status | Author |  Description
---|---|---|---|---
v2025-10-06 23:37:25|2025-10-06 23:37:25|auto|@hanbin|Created by smart-doc



## 控制器：接口定义入口
用途：保存、删除、详情、列表分页查询
### 保存接口定义
**URL:** http://localhost}/autotest/api/save

**Type:** POST


**Content-Type:** application/json

**Description:** 保存接口定义

**Body-parameters:**

Parameter | Type|Required|Description|Since
---|---|---|---|---
id|string|false||No comments found.|-
name|string|false||No comments found.|-
level|string|false||No comments found.|-
moduleId|string|false||No comments found.|-
projectId|string|false||No comments found.|-
method|string|false||No comments found.|-
path|string|false||No comments found.|-
protocol|string|false||No comments found.|-
domainSign|string|false||No comments found.|-
description|string|false||No comments found.|-
header|object|false||No comments found.|-
└─list|array|false||No comments found.|-
body|object|false||No comments found.|-
└─map|map|false||No comments found.|-
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;└─any object|object|false||any object.|-
query|object|false||No comments found.|-
└─list|array|false||No comments found.|-
rest|object|false||No comments found.|-
└─list|array|false||No comments found.|-
createTime|int64|false||No comments found.|-
updateTime|int64|false||No comments found.|-
createUser|string|false||No comments found.|-
updateUser|string|false||No comments found.|-
status|string|false||No comments found.|-

**Request-example:**
```
curl -X POST -H 'Content-Type: application/json' -i http://localhost:8080/autotest/api/save --data '{
  "id": "90",
  "name": "laronda.predovic",
  "level": "l92q77",
  "moduleId": "90",
  "projectId": "90",
  "method": "yihbrp",
  "path": "uhsuyi",
  "protocol": "o77co8",
  "domainSign": "logqrz",
  "description": "gnopva",
  "header": {
    "list": [
      {
        "object": "any object"
      }
    ]
  },
  "body": {
    "map": {
      "mapKey": {}
    }
  },
  "query": {
    "list": [
      {
        "object": "any object"
      }
    ]
  },
  "rest": {
    "list": [
      {
        "object": "any object"
      }
    ]
  },
  "createTime": 1759765053864,
  "updateTime": 1759765053864,
  "createUser": "3sbayy",
  "updateUser": "pvrow5",
  "status": "yfdxvf"
}'
```

**Response-example:**
```
string
```

### 删除接口定义
**URL:** http://localhost}/autotest/api/delete

**Type:** POST


**Content-Type:** application/json

**Description:** 删除接口定义

**Body-parameters:**

Parameter | Type|Required|Description|Since
---|---|---|---|---
id|string|false||No comments found.|-
name|string|false||No comments found.|-
level|string|false||No comments found.|-
moduleId|string|false||No comments found.|-
projectId|string|false||No comments found.|-
method|string|false||No comments found.|-
path|string|false||No comments found.|-
protocol|string|false||No comments found.|-
domainSign|string|false||No comments found.|-
description|string|false||No comments found.|-
header|object|false||No comments found.|-
└─list|array|false||No comments found.|-
body|object|false||No comments found.|-
└─map|map|false||No comments found.|-
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;└─any object|object|false||any object.|-
query|object|false||No comments found.|-
└─list|array|false||No comments found.|-
rest|object|false||No comments found.|-
└─list|array|false||No comments found.|-
createTime|int64|false||No comments found.|-
updateTime|int64|false||No comments found.|-
createUser|string|false||No comments found.|-
updateUser|string|false||No comments found.|-
status|string|false||No comments found.|-

**Request-example:**
```
curl -X POST -H 'Content-Type: application/json' -i http://localhost:8080/autotest/api/delete --data '{
  "id": "90",
  "name": "laronda.predovic",
  "level": "w00wpn",
  "moduleId": "90",
  "projectId": "90",
  "method": "xxe186",
  "path": "ntqb41",
  "protocol": "ityu94",
  "domainSign": "8ffg2b",
  "description": "qlflku",
  "header": {
    "list": [
      {
        "object": "any object"
      }
    ]
  },
  "body": {
    "map": {
      "mapKey": {}
    }
  },
  "query": {
    "list": [
      {
        "object": "any object"
      }
    ]
  },
  "rest": {
    "list": [
      {
        "object": "any object"
      }
    ]
  },
  "createTime": 1759765053864,
  "updateTime": 1759765053864,
  "createUser": "vlfyvd",
  "updateUser": "wipmoe",
  "status": "x6jfmc"
}'
```

**Response-example:**
```
Return void.
```

### 获取接口详情
**URL:** http://localhost}/autotest/api/detail/{apiId}

**Type:** GET


**Content-Type:** application/x-www-form-urlencoded;charset=UTF-8

**Description:** 获取接口详情

**Path-parameters:**

Parameter | Type|Required|Description|Since
---|---|---|---|---
apiId|string|true|   // 接口主键ID|-

**Request-example:**
```
curl -X GET -i http://localhost:8080/autotest/api/detail/90
```
**Response-fields:**

Field | Type|Description|Since
---|---|---|---
id|string|No comments found.|-
num|int64|No comments found.|-
name|string|No comments found.|-
level|string|No comments found.|-
moduleId|string|No comments found.|-
projectId|string|No comments found.|-
method|string|No comments found.|-
path|string|No comments found.|-
protocol|string|No comments found.|-
domainSign|string|No comments found.|-
description|string|No comments found.|-
header|string|No comments found.|-
body|string|No comments found.|-
query|string|No comments found.|-
rest|string|No comments found.|-
createTime|int64|No comments found.|-
updateTime|int64|No comments found.|-
createUser|string|No comments found.|-
updateUser|string|No comments found.|-
status|string|No comments found.|-
moduleName|string|No comments found.|-
username|string|No comments found.|-

**Response-example:**
```
{
  "id": "90",
  "num": 765,
  "name": "laronda.predovic",
  "level": "10rd7i",
  "moduleId": "90",
  "projectId": "90",
  "method": "mk0vk7",
  "path": "d24mh2",
  "protocol": "hhw19f",
  "domainSign": "p1w1ja",
  "description": "wjvbfm",
  "header": "8ztxow",
  "body": "5mfivh",
  "query": "fqg6vj",
  "rest": "ysofx2",
  "createTime": 1759765053864,
  "updateTime": 1759765053864,
  "createUser": "twn6yx",
  "updateUser": "lmpvsy",
  "status": "id4lmj",
  "moduleName": "laronda.predovic",
  "username": "laronda.predovic"
}
```

### 分页查询接口列表
**URL:** http://localhost}/autotest/api/list/{goPage}/{pageSize}

**Type:** POST


**Content-Type:** application/json

**Description:** 分页查询接口列表

**Path-parameters:**

Parameter | Type|Required|Description|Since
---|---|---|---|---
goPage|int32|true|    // 页码|-
pageSize|int32|true|  // 每页数量|-

**Body-parameters:**

Parameter | Type|Required|Description|Since
---|---|---|---|---
condition|string|false||No comments found.|-
moduleId|string|false||No comments found.|-
createUser|string|false||No comments found.|-
projectId|string|false||No comments found.|-
caseType|string|false||No comments found.|-
collectionId|string|false||No comments found.|-
planId|string|false||No comments found.|-
operationType|string|false||No comments found.|-
roleId|string|false||No comments found.|-
requestUser|string|false||No comments found.|-
uiType|string|false||No comments found.|-
system|string|false||No comments found.|-
status|string|false||No comments found.|-
filter|object|false||No comments found.|-
└─map|map|false||No comments found.|-
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;└─any object|object|false||any object.|-

**Request-example:**
```
curl -X POST -H 'Content-Type: application/json' -i http://localhost:8080/autotest/api/list/1/10 --data '{
  "condition": "gu5r3t",
  "moduleId": "90",
  "createUser": "24n3wg",
  "projectId": "90",
  "caseType": "25qpko",
  "collectionId": "90",
  "planId": "90",
  "operationType": "hxbrt2",
  "roleId": "90",
  "requestUser": "erwsit",
  "uiType": "0cfm0a",
  "system": "2lxbkd",
  "status": "71fhwp",
  "filter": {
    "map": {
      "mapKey": {}
    }
  }
}'
```
**Response-fields:**

Field | Type|Description|Since
---|---|---|---
list|array|No comments found.|-
└─id|string|No comments found.|-
└─num|int64|No comments found.|-
└─name|string|No comments found.|-
└─level|string|No comments found.|-
└─moduleId|string|No comments found.|-
└─projectId|string|No comments found.|-
└─method|string|No comments found.|-
└─path|string|No comments found.|-
└─protocol|string|No comments found.|-
└─domainSign|string|No comments found.|-
└─description|string|No comments found.|-
└─header|string|No comments found.|-
└─body|string|No comments found.|-
└─query|string|No comments found.|-
└─rest|string|No comments found.|-
└─createTime|int64|No comments found.|-
└─updateTime|int64|No comments found.|-
└─createUser|string|No comments found.|-
└─updateUser|string|No comments found.|-
└─status|string|No comments found.|-
└─moduleName|string|No comments found.|-
└─username|string|No comments found.|-
total|int64|No comments found.|-

**Response-example:**
```
{
  "list": [
    {
      "id": "90",
      "num": 942,
      "name": "laronda.predovic",
      "level": "fy8klh",
      "moduleId": "90",
      "projectId": "90",
      "method": "mkvv7t",
      "path": "1br6kt",
      "protocol": "y9erpo",
      "domainSign": "fiks7h",
      "description": "5tdcme",
      "header": "exjcw3",
      "body": "byartj",
      "query": "lkuzfk",
      "rest": "y98lpm",
      "createTime": 1759765053864,
      "updateTime": 1759765053864,
      "createUser": "r6dsxq",
      "updateUser": "2dpvpz",
      "status": "ycudeq",
      "moduleName": "laronda.predovic",
      "username": "laronda.predovic"
    }
  ],
  "total": 575
}
```

## 控制器：接口导入入口
职责：接收并解析外部接口文件（如 Swagger/Postman），批量导入到指定项目与模块。
### 导入接口定义文件
**URL:** http://localhost}/autotest/import/api

**Type:** POST


**Content-Type:** multipart/form-data

**Description:** 导入接口定义文件

**Query-parameters:**

Parameter | Type|Required|Description|Since
---|---|---|---|---
file|file|true|     // 上传文件（multipart），包含接口定义|-
sourceType|string|true|// 源类型（如 swagger、postman）|-
projectId|string|true|// 目标项目ID|-
moduleId|string|true| // 目标模块ID|-

**Request-example:**
```
curl -X POST -H 'Content-Type: multipart/form-data' -F 'file=' -i http://localhost:8080/autotest/import/api --data 'sourceType=ddgbli&projectId=90&moduleId=90'
```

**Response-example:**
```
Return void.
```

## 控制器：应用管理入口
职责：保存、删除应用；按系统类型与分页列表查询。
### 保存应用（新增或更新）
**URL:** http://localhost}/autotest/application/save

**Type:** POST


**Content-Type:** application/json

**Description:** 保存应用（新增或更新）

**Body-parameters:**

Parameter | Type|Required|Description|Since
---|---|---|---|---
id|string|false||No comments found.|-
name|string|false||No comments found.|-
system|string|false||No comments found.|-
appId|string|false||No comments found.|-
mainActivity|string|false||No comments found.|-
description|string|false||No comments found.|-
projectId|string|false||No comments found.|-
createTime|int64|false||No comments found.|-
updateTime|int64|false||No comments found.|-

**Request-example:**
```
curl -X POST -H 'Content-Type: application/json' -i http://localhost:8080/autotest/application/save --data '{
  "id": "90",
  "name": "laronda.predovic",
  "system": "obeffx",
  "appId": "90",
  "mainActivity": "xs2tha",
  "description": "jo883f",
  "projectId": "90",
  "createTime": 1759765053864,
  "updateTime": 1759765053864
}'
```

**Response-example:**
```
Return void.
```

### 删除应用
**URL:** http://localhost}/autotest/application/delete

**Type:** POST


**Content-Type:** application/json

**Description:** 删除应用

**Body-parameters:**

Parameter | Type|Required|Description|Since
---|---|---|---|---
id|string|false||No comments found.|-
name|string|false||No comments found.|-
system|string|false||No comments found.|-
appId|string|false||No comments found.|-
mainActivity|string|false||No comments found.|-
description|string|false||No comments found.|-
projectId|string|false||No comments found.|-
createTime|int64|false||No comments found.|-
updateTime|int64|false||No comments found.|-

**Request-example:**
```
curl -X POST -H 'Content-Type: application/json' -i http://localhost:8080/autotest/application/delete --data '{
  "id": "90",
  "name": "laronda.predovic",
  "system": "h3vekh",
  "appId": "90",
  "mainActivity": "g3hgav",
  "description": "twaw6v",
  "projectId": "90",
  "createTime": 1759765053864,
  "updateTime": 1759765053864
}'
```

**Response-example:**
```
Return void.
```

### 按系统类型查询应用列表
**URL:** http://localhost}/autotest/application/list/{system}/{projectId}

**Type:** GET


**Content-Type:** application/x-www-form-urlencoded;charset=UTF-8

**Description:** 按系统类型查询应用列表

**Path-parameters:**

Parameter | Type|Required|Description|Since
---|---|---|---|---
system|string|true|    // 系统类型（android/apple/web等）|-
projectId|string|true| // 项目ID|-

**Request-example:**
```
curl -X GET -i http://localhost:8080/autotest/application/list/rg5dq1/90
```
**Response-fields:**

Field | Type|Description|Since
---|---|---|---
id|string|No comments found.|-
name|string|No comments found.|-
system|string|No comments found.|-
appId|string|No comments found.|-
mainActivity|string|No comments found.|-
description|string|No comments found.|-
projectId|string|No comments found.|-
createTime|int64|No comments found.|-
updateTime|int64|No comments found.|-

**Response-example:**
```
[
  {
    "id": "90",
    "name": "laronda.predovic",
    "system": "h08ewq",
    "appId": "90",
    "mainActivity": "2il70z",
    "description": "w3fu9d",
    "projectId": "90",
    "createTime": 1759765053864,
    "updateTime": 1759765053864
  }
]
```

### 分页查询应用列表
**URL:** http://localhost}/autotest/application/list/{goPage}/{pageSize}

**Type:** POST


**Content-Type:** application/json

**Description:** 分页查询应用列表

**Path-parameters:**

Parameter | Type|Required|Description|Since
---|---|---|---|---
goPage|int32|true|   // 页码|-
pageSize|int32|true| // 每页大小|-

**Body-parameters:**

Parameter | Type|Required|Description|Since
---|---|---|---|---
condition|string|false||No comments found.|-
moduleId|string|false||No comments found.|-
createUser|string|false||No comments found.|-
projectId|string|false||No comments found.|-
caseType|string|false||No comments found.|-
collectionId|string|false||No comments found.|-
planId|string|false||No comments found.|-
operationType|string|false||No comments found.|-
roleId|string|false||No comments found.|-
requestUser|string|false||No comments found.|-
uiType|string|false||No comments found.|-
system|string|false||No comments found.|-
status|string|false||No comments found.|-
filter|object|false||No comments found.|-
└─map|map|false||No comments found.|-
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;└─any object|object|false||any object.|-

**Request-example:**
```
curl -X POST -H 'Content-Type: application/json' -i http://localhost:8080/autotest/application/list/1/10 --data '{
  "condition": "qd194p",
  "moduleId": "90",
  "createUser": "tggu3b",
  "projectId": "90",
  "caseType": "2y97dk",
  "collectionId": "90",
  "planId": "90",
  "operationType": "87psln",
  "roleId": "90",
  "requestUser": "1aotov",
  "uiType": "67plac",
  "system": "ihplhi",
  "status": "gk2w5x",
  "filter": {
    "map": {
      "mapKey": {}
    }
  }
}'
```
**Response-fields:**

Field | Type|Description|Since
---|---|---|---
list|array|No comments found.|-
└─id|string|No comments found.|-
└─name|string|No comments found.|-
└─system|string|No comments found.|-
└─appId|string|No comments found.|-
└─mainActivity|string|No comments found.|-
└─description|string|No comments found.|-
└─projectId|string|No comments found.|-
└─createTime|int64|No comments found.|-
└─updateTime|int64|No comments found.|-
total|int64|No comments found.|-

**Response-example:**
```
{
  "list": [
    {
      "id": "90",
      "name": "laronda.predovic",
      "system": "mehq2l",
      "appId": "90",
      "mainActivity": "z9d3ig",
      "description": "rpyc6h",
      "projectId": "90",
      "createTime": 1759765053864,
      "updateTime": 1759765053864
    }
  ],
  "total": 802
}
```

## 控制层：用例管理入口

    职责简述：提供用例保存、删除、详情、系统类型查询与分页列表的HTTP接口。
    说明：参数透传至Service层，控制器负责轻量的用户上下文注入与分页包装。
### 保存用例
**URL:** http://localhost}/autotest/case/save

**Type:** POST


**Content-Type:** application/json

**Description:** 保存用例

**Body-parameters:**

Parameter | Type|Required|Description|Since
---|---|---|---|---
id|string|false||No comments found.|-
num|int64|false||No comments found.|-
name|string|false||No comments found.|-
level|string|false||No comments found.|-
moduleId|string|false||No comments found.|-
moduleName|string|false||No comments found.|-
projectId|string|false||No comments found.|-
type|string|false||No comments found.|-
thirdParty|string|false||No comments found.|-
description|string|false||No comments found.|-
environmentIds|object|false||No comments found.|-
└─list|array|false||No comments found.|-
system|string|false||No comments found.|-
commonParam|object|false||No comments found.|-
└─map|map|false||No comments found.|-
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;└─any object|object|false||any object.|-
createTime|int64|false||No comments found.|-
updateTime|int64|false||No comments found.|-
createUser|string|false||No comments found.|-
updateUser|string|false||No comments found.|-
status|string|false||No comments found.|-
caseApis|array|false||No comments found.|-
└─id|string|false||No comments found.|-
└─index|int64|false||No comments found.|-
└─caseId|string|false||No comments found.|-
└─apiId|string|false||No comments found.|-
└─description|string|false||No comments found.|-
└─header|object|false||No comments found.|-
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;└─list|array|false||No comments found.|-
└─body|object|false||No comments found.|-
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;└─map|map|false||No comments found.|-
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;└─any object|object|false||any object.|-
└─query|object|false||No comments found.|-
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;└─list|array|false||No comments found.|-
└─rest|object|false||No comments found.|-
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;└─list|array|false||No comments found.|-
└─assertion|object|false||No comments found.|-
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;└─list|array|false||No comments found.|-
└─relation|object|false||No comments found.|-
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;└─list|array|false||No comments found.|-
└─controller|object|false||No comments found.|-
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;└─list|array|false||No comments found.|-
caseWebs|array|false||No comments found.|-
└─id|string|false||No comments found.|-
└─index|int64|false||No comments found.|-
└─caseId|string|false||No comments found.|-
└─operationId|string|false||No comments found.|-
└─description|string|false||No comments found.|-
└─element|object|false||No comments found.|-
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;└─list|array|false||No comments found.|-
└─data|object|false||No comments found.|-
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;└─list|array|false||No comments found.|-
caseApps|array|false||No comments found.|-
└─id|string|false||No comments found.|-
└─index|int64|false||No comments found.|-
└─caseId|string|false||No comments found.|-
└─operationId|string|false||No comments found.|-
└─description|string|false||No comments found.|-
└─element|object|false||No comments found.|-
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;└─list|array|false||No comments found.|-
└─data|object|false||No comments found.|-
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;└─list|array|false||No comments found.|-

**Request-example:**
```
curl -X POST -H 'Content-Type: application/json' -i http://localhost:8080/autotest/case/save --data '{
  "id": "90",
  "num": 631,
  "name": "laronda.predovic",
  "level": "f77tka",
  "moduleId": "90",
  "moduleName": "laronda.predovic",
  "projectId": "90",
  "type": "3cw6rp",
  "thirdParty": "5228i5",
  "description": "qblmaw",
  "environmentIds": {
    "list": [
      {
        "object": "any object"
      }
    ]
  },
  "system": "4ga51g",
  "commonParam": {
    "map": {
      "mapKey": {}
    }
  },
  "createTime": 1759765053864,
  "updateTime": 1759765053864,
  "createUser": "jzzmmd",
  "updateUser": "p8nduz",
  "status": "fl17j8",
  "caseApis": [
    {
      "id": "90",
      "index": 638,
      "caseId": "90",
      "apiId": "90",
      "description": "m40hp9",
      "header": {
        "list": [
          {
            "object": "any object"
          }
        ]
      },
      "body": {
        "map": {
          "mapKey": {}
        }
      },
      "query": {
        "list": [
          {
            "object": "any object"
          }
        ]
      },
      "rest": {
        "list": [
          {
            "object": "any object"
          }
        ]
      },
      "assertion": {
        "list": [
          {
            "object": "any object"
          }
        ]
      },
      "relation": {
        "list": [
          {
            "object": "any object"
          }
        ]
      },
      "controller": {
        "list": [
          {
            "object": "any object"
          }
        ]
      }
    }
  ],
  "caseWebs": [
    {
      "id": "90",
      "index": 801,
      "caseId": "90",
      "operationId": "90",
      "description": "u602an",
      "element": {
        "list": [
          {
            "object": "any object"
          }
        ]
      },
      "data": {
        "list": [
          {
            "object": "any object"
          }
        ]
      }
    }
  ],
  "caseApps": [
    {
      "id": "90",
      "index": 536,
      "caseId": "90",
      "operationId": "90",
      "description": "q8l0vg",
      "element": {
        "list": [
          {
            "object": "any object"
          }
        ]
      },
      "data": {
        "list": [
          {
            "object": "any object"
          }
        ]
      }
    }
  ]
}'
```

**Response-example:**
```
Return void.
```

### 删除用例
**URL:** http://localhost}/autotest/case/delete

**Type:** POST


**Content-Type:** application/json

**Description:** 删除用例

**Body-parameters:**

Parameter | Type|Required|Description|Since
---|---|---|---|---
id|string|false||No comments found.|-
num|int64|false||No comments found.|-
name|string|false||No comments found.|-
level|string|false||No comments found.|-
moduleId|string|false||No comments found.|-
moduleName|string|false||No comments found.|-
projectId|string|false||No comments found.|-
type|string|false||No comments found.|-
thirdParty|string|false||No comments found.|-
description|string|false||No comments found.|-
environmentIds|object|false||No comments found.|-
└─list|array|false||No comments found.|-
system|string|false||No comments found.|-
commonParam|object|false||No comments found.|-
└─map|map|false||No comments found.|-
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;└─any object|object|false||any object.|-
createTime|int64|false||No comments found.|-
updateTime|int64|false||No comments found.|-
createUser|string|false||No comments found.|-
updateUser|string|false||No comments found.|-
status|string|false||No comments found.|-
caseApis|array|false||No comments found.|-
└─id|string|false||No comments found.|-
└─index|int64|false||No comments found.|-
└─caseId|string|false||No comments found.|-
└─apiId|string|false||No comments found.|-
└─description|string|false||No comments found.|-
└─header|object|false||No comments found.|-
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;└─list|array|false||No comments found.|-
└─body|object|false||No comments found.|-
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;└─map|map|false||No comments found.|-
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;└─any object|object|false||any object.|-
└─query|object|false||No comments found.|-
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;└─list|array|false||No comments found.|-
└─rest|object|false||No comments found.|-
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;└─list|array|false||No comments found.|-
└─assertion|object|false||No comments found.|-
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;└─list|array|false||No comments found.|-
└─relation|object|false||No comments found.|-
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;└─list|array|false||No comments found.|-
└─controller|object|false||No comments found.|-
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;└─list|array|false||No comments found.|-
caseWebs|array|false||No comments found.|-
└─id|string|false||No comments found.|-
└─index|int64|false||No comments found.|-
└─caseId|string|false||No comments found.|-
└─operationId|string|false||No comments found.|-
└─description|string|false||No comments found.|-
└─element|object|false||No comments found.|-
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;└─list|array|false||No comments found.|-
└─data|object|false||No comments found.|-
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;└─list|array|false||No comments found.|-
caseApps|array|false||No comments found.|-
└─id|string|false||No comments found.|-
└─index|int64|false||No comments found.|-
└─caseId|string|false||No comments found.|-
└─operationId|string|false||No comments found.|-
└─description|string|false||No comments found.|-
└─element|object|false||No comments found.|-
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;└─list|array|false||No comments found.|-
└─data|object|false||No comments found.|-
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;└─list|array|false||No comments found.|-

**Request-example:**
```
curl -X POST -H 'Content-Type: application/json' -i http://localhost:8080/autotest/case/delete --data '{
  "id": "90",
  "num": 62,
  "name": "laronda.predovic",
  "level": "gsjr8g",
  "moduleId": "90",
  "moduleName": "laronda.predovic",
  "projectId": "90",
  "type": "pod4m8",
  "thirdParty": "vt7e8w",
  "description": "e0hdp3",
  "environmentIds": {
    "list": [
      {
        "object": "any object"
      }
    ]
  },
  "system": "pdaxfs",
  "commonParam": {
    "map": {
      "mapKey": {}
    }
  },
  "createTime": 1759765053864,
  "updateTime": 1759765053864,
  "createUser": "i4l3v9",
  "updateUser": "i6i4ga",
  "status": "zkebur",
  "caseApis": [
    {
      "id": "90",
      "index": 300,
      "caseId": "90",
      "apiId": "90",
      "description": "9yjzuj",
      "header": {
        "list": [
          {
            "object": "any object"
          }
        ]
      },
      "body": {
        "map": {
          "mapKey": {}
        }
      },
      "query": {
        "list": [
          {
            "object": "any object"
          }
        ]
      },
      "rest": {
        "list": [
          {
            "object": "any object"
          }
        ]
      },
      "assertion": {
        "list": [
          {
            "object": "any object"
          }
        ]
      },
      "relation": {
        "list": [
          {
            "object": "any object"
          }
        ]
      },
      "controller": {
        "list": [
          {
            "object": "any object"
          }
        ]
      }
    }
  ],
  "caseWebs": [
    {
      "id": "90",
      "index": 190,
      "caseId": "90",
      "operationId": "90",
      "description": "z5cikb",
      "element": {
        "list": [
          {
            "object": "any object"
          }
        ]
      },
      "data": {
        "list": [
          {
            "object": "any object"
          }
        ]
      }
    }
  ],
  "caseApps": [
    {
      "id": "90",
      "index": 914,
      "caseId": "90",
      "operationId": "90",
      "description": "k5awz0",
      "element": {
        "list": [
          {
            "object": "any object"
          }
        ]
      },
      "data": {
        "list": [
          {
            "object": "any object"
          }
        ]
      }
    }
  ]
}'
```

**Response-example:**
```
Return void.
```

### 获取用例详情
**URL:** http://localhost}/autotest/case/detail/{caseType}/{caseId}

**Type:** GET


**Content-Type:** application/x-www-form-urlencoded;charset=UTF-8

**Description:** 获取用例详情

**Path-parameters:**

Parameter | Type|Required|Description|Since
---|---|---|---|---
caseType|string|true|// 用例类型（API/WEB/android/apple）|-
caseId|string|true|  // 用例ID|-

**Request-example:**
```
curl -X GET -i http://localhost:8080/autotest/case/detail/nepmco/90
```
**Response-fields:**

Field | Type|Description|Since
---|---|---|---
id|string|No comments found.|-
num|int64|No comments found.|-
name|string|No comments found.|-
level|string|No comments found.|-
moduleId|string|No comments found.|-
projectId|string|No comments found.|-
type|string|No comments found.|-
thirdParty|string|No comments found.|-
description|string|No comments found.|-
environmentIds|string|No comments found.|-
system|string|No comments found.|-
commonParam|string|No comments found.|-
createTime|int64|No comments found.|-
updateTime|int64|No comments found.|-
createUser|string|No comments found.|-
updateUser|string|No comments found.|-
status|string|No comments found.|-
moduleName|string|No comments found.|-
username|string|No comments found.|-
caseApis|array|No comments found.|-
└─id|string|No comments found.|-
└─index|int64|No comments found.|-
└─caseId|string|No comments found.|-
└─apiId|string|No comments found.|-
└─description|string|No comments found.|-
└─header|string|No comments found.|-
└─body|string|No comments found.|-
└─query|string|No comments found.|-
└─rest|string|No comments found.|-
└─assertion|string|No comments found.|-
└─relation|string|No comments found.|-
└─controller|string|No comments found.|-
└─apiName|string|No comments found.|-
└─apiPath|string|No comments found.|-
└─apiMethod|string|No comments found.|-
└─apiProtocol|string|No comments found.|-
└─apiDomainSign|string|No comments found.|-
caseWebs|array|No comments found.|-
└─id|string|No comments found.|-
└─index|int64|No comments found.|-
└─caseId|string|No comments found.|-
└─operationId|string|No comments found.|-
└─description|string|No comments found.|-
└─element|string|No comments found.|-
└─data|string|No comments found.|-
└─operationName|string|No comments found.|-
└─operationType|string|No comments found.|-
caseApps|array|No comments found.|-
└─id|string|No comments found.|-
└─index|int64|No comments found.|-
└─caseId|string|No comments found.|-
└─operationId|string|No comments found.|-
└─description|string|No comments found.|-
└─element|string|No comments found.|-
└─data|string|No comments found.|-
└─operationName|string|No comments found.|-
└─operationType|string|No comments found.|-

**Response-example:**
```
{
  "id": "90",
  "num": 109,
  "name": "laronda.predovic",
  "level": "8l7lml",
  "moduleId": "90",
  "projectId": "90",
  "type": "ugmwt9",
  "thirdParty": "7p6toy",
  "description": "u05770",
  "environmentIds": "23",
  "system": "3881ht",
  "commonParam": "uv8fti",
  "createTime": 1759765053864,
  "updateTime": 1759765053864,
  "createUser": "26at2m",
  "updateUser": "lzcq53",
  "status": "hztua7",
  "moduleName": "laronda.predovic",
  "username": "laronda.predovic",
  "caseApis": [
    {
      "id": "90",
      "index": 37,
      "caseId": "90",
      "apiId": "90",
      "description": "wb14r6",
      "header": "m79ifa",
      "body": "m2yjh2",
      "query": "v87q8f",
      "rest": "qqw59m",
      "assertion": "9yhk0s",
      "relation": "nnalli",
      "controller": "uxkea1",
      "apiName": "laronda.predovic",
      "apiPath": "c19jvi",
      "apiMethod": "yeobu8",
      "apiProtocol": "r587vq",
      "apiDomainSign": "6qsrgn"
    }
  ],
  "caseWebs": [
    {
      "id": "90",
      "index": 361,
      "caseId": "90",
      "operationId": "90",
      "description": "1ly8sm",
      "element": "3uc3pj",
      "data": "sl3a42",
      "operationName": "laronda.predovic",
      "operationType": "5q2gop"
    }
  ],
  "caseApps": [
    {
      "id": "90",
      "index": 55,
      "caseId": "90",
      "operationId": "90",
      "description": "x6b3h4",
      "element": "ae22e6",
      "data": "0ryp9z",
      "operationName": "laronda.predovic",
      "operationType": "9jsa89"
    }
  ]
}
```

### 查询用例系统类型
**URL:** http://localhost}/autotest/case/system/{caseId}

**Type:** GET


**Content-Type:** application/x-www-form-urlencoded;charset=UTF-8

**Description:** 查询用例系统类型

**Path-parameters:**

Parameter | Type|Required|Description|Since
---|---|---|---|---
caseId|string|true| // 用例ID|-

**Request-example:**
```
curl -X GET -i http://localhost:8080/autotest/case/system/90
```

**Response-example:**
```
string
```

### 分页查询用例列表<br><br>    说明：使用分页助手进行分页，透传模糊条件与筛选，返回分页信息包装的列表。
**URL:** http://localhost}/autotest/case/list/{goPage}/{pageSize}

**Type:** POST


**Content-Type:** application/json

**Description:** 分页查询用例列表

    说明：使用分页助手进行分页，透传模糊条件与筛选，返回分页信息包装的列表。

**Path-parameters:**

Parameter | Type|Required|Description|Since
---|---|---|---|---
goPage|int32|true|  // 目标页码|-
pageSize|int32|true|// 每页条数|-

**Body-parameters:**

Parameter | Type|Required|Description|Since
---|---|---|---|---
condition|string|false||No comments found.|-
moduleId|string|false||No comments found.|-
createUser|string|false||No comments found.|-
projectId|string|false||No comments found.|-
caseType|string|false||No comments found.|-
collectionId|string|false||No comments found.|-
planId|string|false||No comments found.|-
operationType|string|false||No comments found.|-
roleId|string|false||No comments found.|-
requestUser|string|false||No comments found.|-
uiType|string|false||No comments found.|-
system|string|false||No comments found.|-
status|string|false||No comments found.|-
filter|object|false||No comments found.|-
└─map|map|false||No comments found.|-
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;└─any object|object|false||any object.|-

**Request-example:**
```
curl -X POST -H 'Content-Type: application/json' -i http://localhost:8080/autotest/case/list/1/10 --data '{
  "condition": "e3d43v",
  "moduleId": "90",
  "createUser": "2ash2i",
  "projectId": "90",
  "caseType": "qo9xlp",
  "collectionId": "90",
  "planId": "90",
  "operationType": "i2qmyd",
  "roleId": "90",
  "requestUser": "qhe62v",
  "uiType": "79rnrl",
  "system": "cwxysh",
  "status": "7spqrp",
  "filter": {
    "map": {
      "mapKey": {}
    }
  }
}'
```
**Response-fields:**

Field | Type|Description|Since
---|---|---|---
list|array|No comments found.|-
└─id|string|No comments found.|-
└─num|int64|No comments found.|-
└─name|string|No comments found.|-
└─level|string|No comments found.|-
└─moduleId|string|No comments found.|-
└─projectId|string|No comments found.|-
└─type|string|No comments found.|-
└─thirdParty|string|No comments found.|-
└─description|string|No comments found.|-
└─environmentIds|string|No comments found.|-
└─system|string|No comments found.|-
└─commonParam|string|No comments found.|-
└─createTime|int64|No comments found.|-
└─updateTime|int64|No comments found.|-
└─createUser|string|No comments found.|-
└─updateUser|string|No comments found.|-
└─status|string|No comments found.|-
└─moduleName|string|No comments found.|-
└─username|string|No comments found.|-
└─caseApis|array|No comments found.|-
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;└─id|string|No comments found.|-
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;└─index|int64|No comments found.|-
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;└─caseId|string|No comments found.|-
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;└─apiId|string|No comments found.|-
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;└─description|string|No comments found.|-
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;└─header|string|No comments found.|-
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;└─body|string|No comments found.|-
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;└─query|string|No comments found.|-
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;└─rest|string|No comments found.|-
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;└─assertion|string|No comments found.|-
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;└─relation|string|No comments found.|-
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;└─controller|string|No comments found.|-
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;└─apiName|string|No comments found.|-
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;└─apiPath|string|No comments found.|-
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;└─apiMethod|string|No comments found.|-
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;└─apiProtocol|string|No comments found.|-
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;└─apiDomainSign|string|No comments found.|-
└─caseWebs|array|No comments found.|-
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;└─id|string|No comments found.|-
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;└─index|int64|No comments found.|-
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;└─caseId|string|No comments found.|-
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;└─operationId|string|No comments found.|-
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;└─description|string|No comments found.|-
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;└─element|string|No comments found.|-
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;└─data|string|No comments found.|-
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;└─operationName|string|No comments found.|-
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;└─operationType|string|No comments found.|-
└─caseApps|array|No comments found.|-
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;└─id|string|No comments found.|-
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;└─index|int64|No comments found.|-
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;└─caseId|string|No comments found.|-
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;└─operationId|string|No comments found.|-
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;└─description|string|No comments found.|-
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;└─element|string|No comments found.|-
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;└─data|string|No comments found.|-
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;└─operationName|string|No comments found.|-
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;└─operationType|string|No comments found.|-
total|int64|No comments found.|-

**Response-example:**
```
{
  "list": [
    {
      "id": "90",
      "num": 976,
      "name": "laronda.predovic",
      "level": "4cftaj",
      "moduleId": "90",
      "projectId": "90",
      "type": "06uqeh",
      "thirdParty": "0ycft5",
      "description": "ijorl6",
      "environmentIds": "23",
      "system": "yssd1f",
      "commonParam": "2x9vq1",
      "createTime": 1759765053864,
      "updateTime": 1759765053864,
      "createUser": "vvc8md",
      "updateUser": "jeqwo5",
      "status": "rux84d",
      "moduleName": "laronda.predovic",
      "username": "laronda.predovic",
      "caseApis": [
        {
          "id": "90",
          "index": 281,
          "caseId": "90",
          "apiId": "90",
          "description": "wi2e0h",
          "header": "w43xrt",
          "body": "2xl6fp",
          "query": "jzk7dj",
          "rest": "ldnole",
          "assertion": "rd1j4l",
          "relation": "3suiqf",
          "controller": "x6v9k5",
          "apiName": "laronda.predovic",
          "apiPath": "0kzvhe",
          "apiMethod": "gh7xvw",
          "apiProtocol": "0ghn2d",
          "apiDomainSign": "bbyzxw"
        }
      ],
      "caseWebs": [
        {
          "id": "90",
          "index": 835,
          "caseId": "90",
          "operationId": "90",
          "description": "odi11i",
          "element": "lxrdfz",
          "data": "zbp7t7",
          "operationName": "laronda.predovic",
          "operationType": "y70sf6"
        }
      ],
      "caseApps": [
        {
          "id": "90",
          "index": 907,
          "caseId": "90",
          "operationId": "90",
          "description": "ueo7tv",
          "element": "0gilov",
          "data": "mrgeqf",
          "operationName": "laronda.predovic",
          "operationType": "v613e5"
        }
      ]
    }
  ],
  "total": 0
}
```

### 
**URL:** http://localhost}/autotest/case/api/report/{apiId}

**Type:** GET


**Content-Type:** application/x-www-form-urlencoded;charset=UTF-8

**Description:** 

**Path-parameters:**

Parameter | Type|Required|Description|Since
---|---|---|---|---
apiId|string|true|No comments found.|-

**Request-example:**
```
curl -X GET -i http://localhost:8080/autotest/case/api/report/90
```
**Response-fields:**

Field | Type|Description|Since
---|---|---|---
map|map|No comments found.|-
└─any object|object|any object.|-

**Response-example:**
```
{
  "map": {
    "mapKey": {}
  }
}
```

### 
**URL:** http://localhost}/autotest/case/auto/generate

**Type:** POST


**Content-Type:** application/json

**Description:** 

**Body-parameters:**

Parameter | Type|Required|Description|Since
---|---|---|---|---
apiId|string|false||No comments found.|-
header|array|false||No comments found.|-
└─name|string|false||No comments found.|-
└─type|string|false||No comments found.|-
└─required|string|false||No comments found.|-
└─random|string|false||No comments found.|-
└─value|string|false||No comments found.|-
body|array|false||No comments found.|-
└─name|string|false||No comments found.|-
└─type|string|false||No comments found.|-
└─required|string|false||No comments found.|-
└─random|string|false||No comments found.|-
└─value|string|false||No comments found.|-
query|array|false||No comments found.|-
└─name|string|false||No comments found.|-
└─type|string|false||No comments found.|-
└─required|string|false||No comments found.|-
└─random|string|false||No comments found.|-
└─value|string|false||No comments found.|-
rest|array|false||No comments found.|-
└─name|string|false||No comments found.|-
└─type|string|false||No comments found.|-
└─required|string|false||No comments found.|-
└─random|string|false||No comments found.|-
└─value|string|false||No comments found.|-
positiveAssertion|object|false||No comments found.|-
└─list|array|false||No comments found.|-
oppositeAssertion|object|false||No comments found.|-
└─list|array|false||No comments found.|-
createUser|string|false||No comments found.|-

**Request-example:**
```
curl -X POST -H 'Content-Type: application/json' -i http://localhost:8080/autotest/case/auto/generate --data '{
  "apiId": "90",
  "header": [
    {
      "name": "laronda.predovic",
      "type": "i3c1o6",
      "required": "m8ayp4",
      "random": "6m0rfu",
      "value": "zjc8ro"
    }
  ],
  "body": [
    {
      "name": "laronda.predovic",
      "type": "z6b4ih",
      "required": "35355q",
      "random": "3n3344",
      "value": "wiwfz0"
    }
  ],
  "query": [
    {
      "name": "laronda.predovic",
      "type": "ymx595",
      "required": "se3p0h",
      "random": "3xajko",
      "value": "dqefgc"
    }
  ],
  "rest": [
    {
      "name": "laronda.predovic",
      "type": "kgfcnj",
      "required": "uwadcx",
      "random": "v46w60",
      "value": "2xukna"
    }
  ],
  "positiveAssertion": {
    "list": [
      {
        "object": "any object"
      }
    ]
  },
  "oppositeAssertion": {
    "list": [
      {
        "object": "any object"
      }
    ]
  },
  "createUser": "gk39ha"
}'
```

**Response-example:**
```
Return void.
```

## 控制器：集合管理

    职责简述：提供集合保存、类型查询、删除、详情与分页列表的HTTP入口。
    入参与返回遵循Service契约，进行轻量参数拼装与透传。
### 保存集合（新增或更新）
**URL:** http://localhost}/autotest/collection/save

**Type:** POST


**Content-Type:** application/json

**Description:** 保存集合（新增或更新）

**Body-parameters:**

Parameter | Type|Required|Description|Since
---|---|---|---|---
id|string|false||No comments found.|-
name|string|false||No comments found.|-
deviceId|string|false||No comments found.|-
versionId|string|false||No comments found.|-
description|string|false||No comments found.|-
projectId|string|false||No comments found.|-
createTime|int64|false||No comments found.|-
updateTime|int64|false||No comments found.|-
createUser|string|false||No comments found.|-
updateUser|string|false||No comments found.|-
status|int32|false||No comments found.|-
username|string|false||No comments found.|-
versionName|string|false||No comments found.|-
collectionCases|array|false||No comments found.|-
└─id|string|false||No comments found.|-
└─index|int64|false||No comments found.|-
└─collectionId|string|false||No comments found.|-
└─caseId|string|false||No comments found.|-
└─caseName|string|false||No comments found.|-
└─caseModule|string|false||No comments found.|-
└─caseType|string|false||No comments found.|-
└─caseSystem|string|false||No comments found.|-

**Request-example:**
```
curl -X POST -H 'Content-Type: application/json' -i http://localhost:8080/autotest/collection/save --data '{
  "id": "90",
  "name": "laronda.predovic",
  "deviceId": "90",
  "versionId": "90",
  "description": "5lyu0a",
  "projectId": "90",
  "createTime": 1759765053864,
  "updateTime": 1759765053864,
  "createUser": "fzt0qi",
  "updateUser": "kxq4oh",
  "status": 375,
  "username": "laronda.predovic",
  "versionName": "laronda.predovic",
  "collectionCases": [
    {
      "id": "90",
      "index": 874,
      "collectionId": "90",
      "caseId": "90",
      "caseName": "laronda.predovic",
      "caseModule": "hdqw6y",
      "caseType": "vvj5pl",
      "caseSystem": "v1sune"
    }
  ]
}'
```

**Response-example:**
```
Return void.
```

### 删除集合（逻辑删除）
**URL:** http://localhost}/autotest/collection/delete

**Type:** POST


**Content-Type:** application/json

**Description:** 删除集合（逻辑删除）

**Body-parameters:**

Parameter | Type|Required|Description|Since
---|---|---|---|---
id|string|false||No comments found.|-
name|string|false||No comments found.|-
deviceId|string|false||No comments found.|-
versionId|string|false||No comments found.|-
description|string|false||No comments found.|-
projectId|string|false||No comments found.|-
createTime|int64|false||No comments found.|-
updateTime|int64|false||No comments found.|-
createUser|string|false||No comments found.|-
updateUser|string|false||No comments found.|-
status|int32|false||No comments found.|-
username|string|false||No comments found.|-
versionName|string|false||No comments found.|-
collectionCases|array|false||No comments found.|-
└─id|string|false||No comments found.|-
└─index|int64|false||No comments found.|-
└─collectionId|string|false||No comments found.|-
└─caseId|string|false||No comments found.|-
└─caseName|string|false||No comments found.|-
└─caseModule|string|false||No comments found.|-
└─caseType|string|false||No comments found.|-
└─caseSystem|string|false||No comments found.|-

**Request-example:**
```
curl -X POST -H 'Content-Type: application/json' -i http://localhost:8080/autotest/collection/delete --data '{
  "id": "90",
  "name": "laronda.predovic",
  "deviceId": "90",
  "versionId": "90",
  "description": "qk36eq",
  "projectId": "90",
  "createTime": 1759765053864,
  "updateTime": 1759765053864,
  "createUser": "c6ow2g",
  "updateUser": "5ld3c1",
  "status": 687,
  "username": "laronda.predovic",
  "versionName": "laronda.predovic",
  "collectionCases": [
    {
      "id": "90",
      "index": 110,
      "collectionId": "90",
      "caseId": "90",
      "caseName": "laronda.predovic",
      "caseModule": "3bfmnw",
      "caseType": "v5dzw4",
      "caseSystem": "pjj5lm"
    }
  ]
}'
```

**Response-example:**
```
Return void.
```

### 获取集合详情
**URL:** http://localhost}/autotest/collection/detail/{collectionId}

**Type:** GET


**Content-Type:** application/x-www-form-urlencoded;charset=UTF-8

**Description:** 获取集合详情

**Path-parameters:**

Parameter | Type|Required|Description|Since
---|---|---|---|---
collectionId|string|true|  // 集合ID|-

**Request-example:**
```
curl -X GET -i http://localhost:8080/autotest/collection/detail/90
```
**Response-fields:**

Field | Type|Description|Since
---|---|---|---
id|string|No comments found.|-
name|string|No comments found.|-
deviceId|string|No comments found.|-
versionId|string|No comments found.|-
description|string|No comments found.|-
projectId|string|No comments found.|-
createTime|int64|No comments found.|-
updateTime|int64|No comments found.|-
createUser|string|No comments found.|-
updateUser|string|No comments found.|-
status|int32|No comments found.|-
username|string|No comments found.|-
versionName|string|No comments found.|-
collectionCases|array|No comments found.|-
└─id|string|No comments found.|-
└─index|int64|No comments found.|-
└─collectionId|string|No comments found.|-
└─caseId|string|No comments found.|-
└─caseName|string|No comments found.|-
└─caseModule|string|No comments found.|-
└─caseType|string|No comments found.|-
└─caseSystem|string|No comments found.|-

**Response-example:**
```
{
  "id": "90",
  "name": "laronda.predovic",
  "deviceId": "90",
  "versionId": "90",
  "description": "p1z8sh",
  "projectId": "90",
  "createTime": 1759765053864,
  "updateTime": 1759765053864,
  "createUser": "5raf2r",
  "updateUser": "lfulrr",
  "status": 724,
  "username": "laronda.predovic",
  "versionName": "laronda.predovic",
  "collectionCases": [
    {
      "id": "90",
      "index": 440,
      "collectionId": "90",
      "caseId": "90",
      "caseName": "laronda.predovic",
      "caseModule": "u1a6tk",
      "caseType": "4yll1j",
      "caseSystem": "mp09yc"
    }
  ]
}
```

### 查询集合包含的用例系统类型
**URL:** http://localhost}/autotest/collection/types/{collectionId}

**Type:** GET


**Content-Type:** application/x-www-form-urlencoded;charset=UTF-8

**Description:** 查询集合包含的用例系统类型

**Path-parameters:**

Parameter | Type|Required|Description|Since
---|---|---|---|---
collectionId|string|true|           // 集合ID|-

**Request-example:**
```
curl -X GET -i http://localhost:8080/autotest/collection/types/90
```
**Response-fields:**

Field | Type|Description|Since
---|---|---|---
mapKey|boolean|A map key.|-

**Response-example:**
```
{
  "mapKey1": true,
  "mapKey2": true
}
```

### 分页查询集合列表
**URL:** http://localhost}/autotest/collection/list/{goPage}/{pageSize}

**Type:** POST


**Content-Type:** application/json

**Description:** 分页查询集合列表

**Path-parameters:**

Parameter | Type|Required|Description|Since
---|---|---|---|---
goPage|int32|true|                 // 页码|-
pageSize|int32|true|               // 页大小|-

**Body-parameters:**

Parameter | Type|Required|Description|Since
---|---|---|---|---
condition|string|false||No comments found.|-
moduleId|string|false||No comments found.|-
createUser|string|false||No comments found.|-
projectId|string|false||No comments found.|-
caseType|string|false||No comments found.|-
collectionId|string|false||No comments found.|-
planId|string|false||No comments found.|-
operationType|string|false||No comments found.|-
roleId|string|false||No comments found.|-
requestUser|string|false||No comments found.|-
uiType|string|false||No comments found.|-
system|string|false||No comments found.|-
status|string|false||No comments found.|-
filter|object|false||No comments found.|-
└─map|map|false||No comments found.|-
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;└─any object|object|false||any object.|-

**Request-example:**
```
curl -X POST -H 'Content-Type: application/json' -i http://localhost:8080/autotest/collection/list/1/10 --data '{
  "condition": "bfw5mj",
  "moduleId": "90",
  "createUser": "ynld6m",
  "projectId": "90",
  "caseType": "3qktv9",
  "collectionId": "90",
  "planId": "90",
  "operationType": "iuh875",
  "roleId": "90",
  "requestUser": "cabs12",
  "uiType": "o2v73m",
  "system": "uloz6h",
  "status": "j61hvo",
  "filter": {
    "map": {
      "mapKey": {}
    }
  }
}'
```
**Response-fields:**

Field | Type|Description|Since
---|---|---|---
list|array|No comments found.|-
└─id|string|No comments found.|-
└─name|string|No comments found.|-
└─deviceId|string|No comments found.|-
└─versionId|string|No comments found.|-
└─description|string|No comments found.|-
└─projectId|string|No comments found.|-
└─createTime|int64|No comments found.|-
└─updateTime|int64|No comments found.|-
└─createUser|string|No comments found.|-
└─updateUser|string|No comments found.|-
└─status|int32|No comments found.|-
└─username|string|No comments found.|-
└─versionName|string|No comments found.|-
└─collectionCases|array|No comments found.|-
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;└─id|string|No comments found.|-
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;└─index|int64|No comments found.|-
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;└─collectionId|string|No comments found.|-
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;└─caseId|string|No comments found.|-
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;└─caseName|string|No comments found.|-
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;└─caseModule|string|No comments found.|-
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;└─caseType|string|No comments found.|-
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;└─caseSystem|string|No comments found.|-
total|int64|No comments found.|-

**Response-example:**
```
{
  "list": [
    {
      "id": "90",
      "name": "laronda.predovic",
      "deviceId": "90",
      "versionId": "90",
      "description": "xbtjhc",
      "projectId": "90",
      "createTime": 1759765053864,
      "updateTime": 1759765053864,
      "createUser": "q0sli3",
      "updateUser": "ji9eko",
      "status": 846,
      "username": "laronda.predovic",
      "versionName": "laronda.predovic",
      "collectionCases": [
        {
          "id": "90",
          "index": 125,
          "collectionId": "90",
          "caseId": "90",
          "caseName": "laronda.predovic",
          "caseModule": "fdhaix",
          "caseType": "5wl0au",
          "caseSystem": "bfh9td"
        }
      ]
    }
  ],
  "total": 468
}
```

## 控制器：公共参数管理
职责：参数数据的新增/删除、分页查询、按分组与项目维度查询。
### 保存参数数据（新增或更新），并记录更新人
**URL:** http://localhost}/autotest/commonParam/param/save

**Type:** POST


**Content-Type:** application/json

**Description:** 保存参数数据（新增或更新），并记录更新人

**Body-parameters:**

Parameter | Type|Required|Description|Since
---|---|---|---|---
id|string|false||No comments found.|-
name|string|false||No comments found.|-
paramData|string|false||No comments found.|-
groupId|string|false||No comments found.|-
dataType|string|false||No comments found.|-
description|string|false||No comments found.|-
createTime|int64|false||No comments found.|-
updateTime|int64|false||No comments found.|-
createUser|string|false||No comments found.|-
updateUser|string|false||No comments found.|-
status|int32|false||No comments found.|-

**Request-example:**
```
curl -X POST -H 'Content-Type: application/json' -i http://localhost:8080/autotest/commonParam/param/save --data '{
  "id": "90",
  "name": "laronda.predovic",
  "paramData": "dksd2t",
  "groupId": "90",
  "dataType": "xby67o",
  "description": "y952vi",
  "createTime": 1759765053864,
  "updateTime": 1759765053864,
  "createUser": "beqapb",
  "updateUser": "9k00f7",
  "status": 302
}'
```

**Response-example:**
```
Return void.
```

### 删除参数数据
**URL:** http://localhost}/autotest/commonParam/param/delete

**Type:** POST


**Content-Type:** application/json

**Description:** 删除参数数据

**Body-parameters:**

Parameter | Type|Required|Description|Since
---|---|---|---|---
id|string|false||No comments found.|-
name|string|false||No comments found.|-
paramData|string|false||No comments found.|-
groupId|string|false||No comments found.|-
dataType|string|false||No comments found.|-
description|string|false||No comments found.|-
createTime|int64|false||No comments found.|-
updateTime|int64|false||No comments found.|-
createUser|string|false||No comments found.|-
updateUser|string|false||No comments found.|-
status|int32|false||No comments found.|-

**Request-example:**
```
curl -X POST -H 'Content-Type: application/json' -i http://localhost:8080/autotest/commonParam/param/delete --data '{
  "id": "90",
  "name": "laronda.predovic",
  "paramData": "sq87yb",
  "groupId": "90",
  "dataType": "uuce5a",
  "description": "sozx6w",
  "createTime": 1759765053864,
  "updateTime": 1759765053864,
  "createUser": "q6qi2p",
  "updateUser": "vqt992",
  "status": 315
}'
```

**Response-example:**
```
Return void.
```

### 分页查询指定分组的参数数据
**URL:** http://localhost}/autotest/commonParam/param/{groupId}/list/{goPage}/{pageSize}

**Type:** POST


**Content-Type:** application/json

**Description:** 分页查询指定分组的参数数据

**Path-parameters:**

Parameter | Type|Required|Description|Since
---|---|---|---|---
goPage|int32|true|  // 页码|-
pageSize|int32|true|// 每页大小|-
groupId|string|true| // 分组ID|-

**Body-parameters:**

Parameter | Type|Required|Description|Since
---|---|---|---|---
condition|string|false||No comments found.|-
moduleId|string|false||No comments found.|-
createUser|string|false||No comments found.|-
projectId|string|false||No comments found.|-
caseType|string|false||No comments found.|-
collectionId|string|false||No comments found.|-
planId|string|false||No comments found.|-
operationType|string|false||No comments found.|-
roleId|string|false||No comments found.|-
requestUser|string|false||No comments found.|-
uiType|string|false||No comments found.|-
system|string|false||No comments found.|-
status|string|false||No comments found.|-
filter|object|false||No comments found.|-
└─map|map|false||No comments found.|-
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;└─any object|object|false||any object.|-

**Request-example:**
```
curl -X POST -H 'Content-Type: application/json' -i http://localhost:8080/autotest/commonParam/param/90/list/1/10 --data '{
  "condition": "jnw86w",
  "moduleId": "90",
  "createUser": "jgcoma",
  "projectId": "90",
  "caseType": "3yrx9g",
  "collectionId": "90",
  "planId": "90",
  "operationType": "81d0k0",
  "roleId": "90",
  "requestUser": "skh4vw",
  "uiType": "hm2em1",
  "system": "2eg9g4",
  "status": "m2m04s",
  "filter": {
    "map": {
      "mapKey": {}
    }
  }
}'
```
**Response-fields:**

Field | Type|Description|Since
---|---|---|---
list|array|No comments found.|-
└─id|string|No comments found.|-
└─name|string|No comments found.|-
└─paramData|string|No comments found.|-
└─groupId|string|No comments found.|-
└─dataType|string|No comments found.|-
└─description|string|No comments found.|-
└─createTime|int64|No comments found.|-
└─updateTime|int64|No comments found.|-
└─createUser|string|No comments found.|-
└─updateUser|string|No comments found.|-
└─status|int32|No comments found.|-
└─username|string|用户名称（创建/更新操作者的展示名）|-
total|int64|No comments found.|-

**Response-example:**
```
{
  "list": [
    {
      "id": "90",
      "name": "laronda.predovic",
      "paramData": "vcfp7x",
      "groupId": "90",
      "dataType": "4otv4h",
      "description": "8blylo",
      "createTime": 1759765053864,
      "updateTime": 1759765053864,
      "createUser": "h9jizb",
      "updateUser": "uccquo",
      "status": 578,
      "username": "laronda.predovic"
    }
  ],
  "total": 668
}
```

### 按分组名称与项目查询参数数据
**URL:** http://localhost}/autotest/commonParam/param/list/{groupName}/{projectId}

**Type:** GET


**Content-Type:** application/x-www-form-urlencoded;charset=UTF-8

**Description:** 按分组名称与项目查询参数数据

**Path-parameters:**

Parameter | Type|Required|Description|Since
---|---|---|---|---
groupName|string|true|// 分组名称|-
projectId|string|true|// 项目ID|-

**Request-example:**
```
curl -X GET -i http://localhost:8080/autotest/commonParam/param/list/laronda.predovic/90
```
**Response-fields:**

Field | Type|Description|Since
---|---|---|---
id|string|No comments found.|-
name|string|No comments found.|-
paramData|string|No comments found.|-
groupId|string|No comments found.|-
dataType|string|No comments found.|-
description|string|No comments found.|-
createTime|int64|No comments found.|-
updateTime|int64|No comments found.|-
createUser|string|No comments found.|-
updateUser|string|No comments found.|-
status|int32|No comments found.|-
username|string|用户名称（创建/更新操作者的展示名）|-

**Response-example:**
```
[
  {
    "id": "90",
    "name": "laronda.predovic",
    "paramData": "kbxojv",
    "groupId": "90",
    "dataType": "nspr2m",
    "description": "e0g3pg",
    "createTime": 1759765053864,
    "updateTime": 1759765053864,
    "createUser": "3arkkw",
    "updateUser": "y77x96",
    "status": 864,
    "username": "laronda.predovic"
  }
]
```

### 查询项目下的自定义参数列表
**URL:** http://localhost}/autotest/commonParam/custom/list/{projectId}

**Type:** GET


**Content-Type:** application/x-www-form-urlencoded;charset=UTF-8

**Description:** 查询项目下的自定义参数列表

**Path-parameters:**

Parameter | Type|Required|Description|Since
---|---|---|---|---
projectId|string|true|// 项目ID|-

**Request-example:**
```
curl -X GET -i http://localhost:8080/autotest/commonParam/custom/list/90
```
**Response-fields:**

Field | Type|Description|Since
---|---|---|---
id|string|No comments found.|-
name|string|No comments found.|-
paramData|string|No comments found.|-
groupId|string|No comments found.|-
dataType|string|No comments found.|-
description|string|No comments found.|-
createTime|int64|No comments found.|-
updateTime|int64|No comments found.|-
createUser|string|No comments found.|-
updateUser|string|No comments found.|-
status|int32|No comments found.|-

**Response-example:**
```
[
  {
    "id": "90",
    "name": "laronda.predovic",
    "paramData": "fmdg13",
    "groupId": "90",
    "dataType": "meeu9m",
    "description": "abqasb",
    "createTime": 1759765053864,
    "updateTime": 1759765053864,
    "createUser": "azsbdf",
    "updateUser": "orbohd",
    "status": 568
  }
]
```

### 查询项目下的参数分组列表
**URL:** http://localhost}/autotest/commonParam/group/list/{projectId}

**Type:** GET


**Content-Type:** application/x-www-form-urlencoded;charset=UTF-8

**Description:** 查询项目下的参数分组列表

**Path-parameters:**

Parameter | Type|Required|Description|Since
---|---|---|---|---
projectId|string|true|// 项目ID|-

**Request-example:**
```
curl -X GET -i http://localhost:8080/autotest/commonParam/group/list/90
```
**Response-fields:**

Field | Type|Description|Since
---|---|---|---
id|string|No comments found.|-
name|string|No comments found.|-
paramType|string|No comments found.|-
projectId|string|No comments found.|-
description|string|No comments found.|-
createTime|int64|No comments found.|-
updateTime|int64|No comments found.|-
createUser|string|No comments found.|-
updateUser|string|No comments found.|-

**Response-example:**
```
[
  {
    "id": "90",
    "name": "laronda.predovic",
    "paramType": "zwbr0v",
    "projectId": "90",
    "description": "cdghu6",
    "createTime": 1759765053864,
    "updateTime": 1759765053864,
    "createUser": "vfwfac",
    "updateUser": "0r3wjf"
  }
]
```

## 控制器：控件管理入口
职责：保存、删除、模块控件查询与分页列表
### 功能：保存控件
**URL:** http://localhost}/autotest/control/save

**Type:** POST


**Content-Type:** application/json

**Description:** 功能：保存控件

**Body-parameters:**

Parameter | Type|Required|Description|Since
---|---|---|---|---
id|string|false||No comments found.|-
num|int64|false||No comments found.|-
name|string|false||No comments found.|-
system|string|false||No comments found.|-
moduleId|string|false||No comments found.|-
projectId|string|false||No comments found.|-
by|string|false||No comments found.|-
expression|string|false||No comments found.|-
description|string|false||No comments found.|-
createTime|int64|false||No comments found.|-
updateTime|int64|false||No comments found.|-
createUser|string|false||No comments found.|-
updateUser|string|false||No comments found.|-
status|string|false||No comments found.|-

**Request-example:**
```
curl -X POST -H 'Content-Type: application/json' -i http://localhost:8080/autotest/control/save --data '{
  "id": "90",
  "num": 80,
  "name": "laronda.predovic",
  "system": "dxu6ri",
  "moduleId": "90",
  "projectId": "90",
  "by": "pid7bs",
  "expression": "eyj66d",
  "description": "4e0df2",
  "createTime": 1759765053864,
  "updateTime": 1759765053864,
  "createUser": "cd56hg",
  "updateUser": "a1rm6e",
  "status": "rj7y4e"
}'
```

**Response-example:**
```
Return void.
```

### 功能：删除控件
**URL:** http://localhost}/autotest/control/delete

**Type:** POST


**Content-Type:** application/json

**Description:** 功能：删除控件

**Body-parameters:**

Parameter | Type|Required|Description|Since
---|---|---|---|---
id|string|false||No comments found.|-
num|int64|false||No comments found.|-
name|string|false||No comments found.|-
system|string|false||No comments found.|-
moduleId|string|false||No comments found.|-
projectId|string|false||No comments found.|-
by|string|false||No comments found.|-
expression|string|false||No comments found.|-
description|string|false||No comments found.|-
createTime|int64|false||No comments found.|-
updateTime|int64|false||No comments found.|-
createUser|string|false||No comments found.|-
updateUser|string|false||No comments found.|-
status|string|false||No comments found.|-

**Request-example:**
```
curl -X POST -H 'Content-Type: application/json' -i http://localhost:8080/autotest/control/delete --data '{
  "id": "90",
  "num": 521,
  "name": "laronda.predovic",
  "system": "0ymyqq",
  "moduleId": "90",
  "projectId": "90",
  "by": "uvo09n",
  "expression": "ewvkug",
  "description": "4st9o7",
  "createTime": 1759765053864,
  "updateTime": 1759765053864,
  "createUser": "o964ia",
  "updateUser": "a0zqys",
  "status": "wqo9mh"
}'
```

**Response-example:**
```
Return void.
```

### 功能：查询模块下控件列表
**URL:** http://localhost}/autotest/control/list/module

**Type:** POST


**Content-Type:** application/json

**Description:** 功能：查询模块下控件列表

**Body-parameters:**

Parameter | Type|Required|Description|Since
---|---|---|---|---
condition|string|false||No comments found.|-
moduleId|string|false||No comments found.|-
createUser|string|false||No comments found.|-
projectId|string|false||No comments found.|-
caseType|string|false||No comments found.|-
collectionId|string|false||No comments found.|-
planId|string|false||No comments found.|-
operationType|string|false||No comments found.|-
roleId|string|false||No comments found.|-
requestUser|string|false||No comments found.|-
uiType|string|false||No comments found.|-
system|string|false||No comments found.|-
status|string|false||No comments found.|-
filter|object|false||No comments found.|-
└─map|map|false||No comments found.|-
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;└─any object|object|false||any object.|-

**Request-example:**
```
curl -X POST -H 'Content-Type: application/json' -i http://localhost:8080/autotest/control/list/module --data '{
  "condition": "me2bjw",
  "moduleId": "90",
  "createUser": "gbr6ea",
  "projectId": "90",
  "caseType": "fdbf3v",
  "collectionId": "90",
  "planId": "90",
  "operationType": "0xoclc",
  "roleId": "90",
  "requestUser": "bjx82s",
  "uiType": "rl2e6b",
  "system": "vnwgpv",
  "status": "53xbi0",
  "filter": {
    "map": {
      "mapKey": {}
    }
  }
}'
```
**Response-fields:**

Field | Type|Description|Since
---|---|---|---
id|string|No comments found.|-
num|int64|No comments found.|-
name|string|No comments found.|-
system|string|No comments found.|-
moduleId|string|No comments found.|-
projectId|string|No comments found.|-
by|string|No comments found.|-
expression|string|No comments found.|-
description|string|No comments found.|-
createTime|int64|No comments found.|-
updateTime|int64|No comments found.|-
createUser|string|No comments found.|-
updateUser|string|No comments found.|-
status|string|No comments found.|-

**Response-example:**
```
[
  {
    "id": "90",
    "num": 479,
    "name": "laronda.predovic",
    "system": "msamvy",
    "moduleId": "90",
    "projectId": "90",
    "by": "sfio1e",
    "expression": "owyneb",
    "description": "rt1wbl",
    "createTime": 1759765053864,
    "updateTime": 1759765053864,
    "createUser": "asgipa",
    "updateUser": "rew3wg",
    "status": "2a3fp6"
  }
]
```

### 功能：分页查询控件列表
**URL:** http://localhost}/autotest/control/list/{goPage}/{pageSize}

**Type:** POST


**Content-Type:** application/json

**Description:** 功能：分页查询控件列表

**Path-parameters:**

Parameter | Type|Required|Description|Since
---|---|---|---|---
goPage|int32|true|  // 页码|-
pageSize|int32|true|// 每页大小|-

**Body-parameters:**

Parameter | Type|Required|Description|Since
---|---|---|---|---
condition|string|false||No comments found.|-
moduleId|string|false||No comments found.|-
createUser|string|false||No comments found.|-
projectId|string|false||No comments found.|-
caseType|string|false||No comments found.|-
collectionId|string|false||No comments found.|-
planId|string|false||No comments found.|-
operationType|string|false||No comments found.|-
roleId|string|false||No comments found.|-
requestUser|string|false||No comments found.|-
uiType|string|false||No comments found.|-
system|string|false||No comments found.|-
status|string|false||No comments found.|-
filter|object|false||No comments found.|-
└─map|map|false||No comments found.|-
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;└─any object|object|false||any object.|-

**Request-example:**
```
curl -X POST -H 'Content-Type: application/json' -i http://localhost:8080/autotest/control/list/1/10 --data '{
  "condition": "1pevis",
  "moduleId": "90",
  "createUser": "7upese",
  "projectId": "90",
  "caseType": "aw2jt4",
  "collectionId": "90",
  "planId": "90",
  "operationType": "h5g76a",
  "roleId": "90",
  "requestUser": "gu6w3d",
  "uiType": "acebqi",
  "system": "5yqgku",
  "status": "7inmt0",
  "filter": {
    "map": {
      "mapKey": {}
    }
  }
}'
```
**Response-fields:**

Field | Type|Description|Since
---|---|---|---
list|array|No comments found.|-
└─id|string|No comments found.|-
└─num|int64|No comments found.|-
└─name|string|No comments found.|-
└─system|string|No comments found.|-
└─moduleId|string|No comments found.|-
└─projectId|string|No comments found.|-
└─by|string|No comments found.|-
└─expression|string|No comments found.|-
└─description|string|No comments found.|-
└─createTime|int64|No comments found.|-
└─updateTime|int64|No comments found.|-
└─createUser|string|No comments found.|-
└─updateUser|string|No comments found.|-
└─status|string|No comments found.|-
└─moduleName|string|模块名称（所属模块的可读名称）|-
└─username|string|用户名称（创建或更新操作者的展示名称）|-
total|int64|No comments found.|-

**Response-example:**
```
{
  "list": [
    {
      "id": "90",
      "num": 192,
      "name": "laronda.predovic",
      "system": "hhhxzz",
      "moduleId": "90",
      "projectId": "90",
      "by": "6nx6v6",
      "expression": "jz2ohc",
      "description": "fy9ptk",
      "createTime": 1759765053864,
      "updateTime": 1759765053864,
      "createUser": "pttxwc",
      "updateUser": "x9m6nu",
      "status": "tolqsv",
      "moduleName": "laronda.predovic",
      "username": "laronda.predovic"
    }
  ],
  "total": 865
}
```

## 控制器：仪表盘数据入口
职责：提供项目仪表盘数据聚合查询接口。
### 查询项目仪表盘数据
**URL:** http://localhost}/autotest/dashboard/get/{projectId}

**Type:** GET


**Content-Type:** application/x-www-form-urlencoded;charset=UTF-8

**Description:** 查询项目仪表盘数据

**Path-parameters:**

Parameter | Type|Required|Description|Since
---|---|---|---|---
projectId|string|true|// 项目ID|-

**Request-example:**
```
curl -X GET -i http://localhost:8080/autotest/dashboard/get/90
```
**Response-fields:**

Field | Type|Description|Since
---|---|---|---
map|map|No comments found.|-
└─any object|object|any object.|-

**Response-example:**
```
{
  "map": {
    "mapKey": {}
  }
}
```

## 控制器：数据库配置入口
用途：保存、删除、名称查询、列表查询
### 保存数据库配置
**URL:** http://localhost}/autotest/database/save

**Type:** POST


**Content-Type:** application/json

**Description:** 保存数据库配置

**Body-parameters:**

Parameter | Type|Required|Description|Since
---|---|---|---|---
id|string|false||No comments found.|-
databaseType|string|false||No comments found.|-
databaseKey|string|false||No comments found.|-
connectInfo|string|false||No comments found.|-
environmentId|string|false||No comments found.|-
createTime|int64|false||No comments found.|-
updateTime|int64|false||No comments found.|-
createUser|string|false||No comments found.|-
updateUser|string|false||No comments found.|-
status|int32|false||No comments found.|-
info|object|false||No comments found.|-
└─host|string|false||No comments found.|-
└─port|string|false||No comments found.|-
└─user|string|false||No comments found.|-
└─password|string|false||No comments found.|-

**Request-example:**
```
curl -X POST -H 'Content-Type: application/json' -i http://localhost:8080/autotest/database/save --data '{
  "id": "90",
  "databaseType": "p0p88q",
  "databaseKey": "tt4r7i",
  "connectInfo": "r60tb7",
  "environmentId": "90",
  "createTime": 1759765053864,
  "updateTime": 1759765053864,
  "createUser": "1nut8h",
  "updateUser": "9aala2",
  "status": 718,
  "info": {
    "host": "z97nvj",
    "port": "46uv6a",
    "user": "lz8axr",
    "password": "smo1kf"
  }
}'
```

**Response-example:**
```
Return void.
```

### 删除数据库配置
**URL:** http://localhost}/autotest/database/delete

**Type:** POST


**Content-Type:** application/json

**Description:** 删除数据库配置

**Body-parameters:**

Parameter | Type|Required|Description|Since
---|---|---|---|---
id|string|false||No comments found.|-
databaseType|string|false||No comments found.|-
databaseKey|string|false||No comments found.|-
connectInfo|string|false||No comments found.|-
environmentId|string|false||No comments found.|-
createTime|int64|false||No comments found.|-
updateTime|int64|false||No comments found.|-
createUser|string|false||No comments found.|-
updateUser|string|false||No comments found.|-
status|int32|false||No comments found.|-

**Request-example:**
```
curl -X POST -H 'Content-Type: application/json' -i http://localhost:8080/autotest/database/delete --data '{
  "id": "90",
  "databaseType": "f3ld4v",
  "databaseKey": "3krhht",
  "connectInfo": "5mngln",
  "environmentId": "90",
  "createTime": 1759765053864,
  "updateTime": 1759765053864,
  "createUser": "ydo4sk",
  "updateUser": "z6vr6c",
  "status": 667
}'
```

**Response-example:**
```
Return void.
```

### 获取项目下数据库键名称列表
**URL:** http://localhost}/autotest/database/name/list/{projectId}

**Type:** GET


**Content-Type:** application/x-www-form-urlencoded;charset=UTF-8

**Description:** 获取项目下数据库键名称列表

**Path-parameters:**

Parameter | Type|Required|Description|Since
---|---|---|---|---
projectId|string|true|    // 项目ID|-

**Request-example:**
```
curl -X GET -i http://localhost:8080/autotest/database/name/list/90
```

**Response-example:**
```
[
  "tageff",
  "fgtgin"
]
```

### 获取环境下数据库列表
**URL:** http://localhost}/autotest/database/list/{environmentId}

**Type:** GET


**Content-Type:** application/x-www-form-urlencoded;charset=UTF-8

**Description:** 获取环境下数据库列表

**Path-parameters:**

Parameter | Type|Required|Description|Since
---|---|---|---|---
environmentId|string|true|       // 环境ID|-

**Request-example:**
```
curl -X GET -i http://localhost:8080/autotest/database/list/90
```
**Response-fields:**

Field | Type|Description|Since
---|---|---|---
id|string|No comments found.|-
databaseType|string|No comments found.|-
databaseKey|string|No comments found.|-
connectInfo|string|No comments found.|-
environmentId|string|No comments found.|-
createTime|int64|No comments found.|-
updateTime|int64|No comments found.|-
createUser|string|No comments found.|-
updateUser|string|No comments found.|-
status|int32|No comments found.|-
info|object|No comments found.|-
└─host|string|No comments found.|-
└─port|string|No comments found.|-
└─user|string|No comments found.|-
└─password|string|No comments found.|-

**Response-example:**
```
[
  {
    "id": "90",
    "databaseType": "crb73o",
    "databaseKey": "xl7mb8",
    "connectInfo": "0jdupm",
    "environmentId": "90",
    "createTime": 1759765053864,
    "updateTime": 1759765053864,
    "createUser": "06l7s0",
    "updateUser": "82hbq4",
    "status": 745,
    "info": {
      "host": "vqnosf",
      "port": "07z5s6",
      "user": "wq8p8t",
      "password": "jq2bbe"
    }
  }
]
```

## 控制器：设备管理
职责：设备筛选、占用/释放、激活、更新，以及明细与列表查询。
### 获取设备筛选条件
**URL:** http://localhost}/autotest/device/filter/{projectId}

**Type:** GET


**Content-Type:** application/x-www-form-urlencoded;charset=UTF-8

**Description:** 获取设备筛选条件

**Path-parameters:**

Parameter | Type|Required|Description|Since
---|---|---|---|---
projectId|string|true|// 项目ID|-

**Request-example:**
```
curl -X GET -i http://localhost:8080/autotest/device/filter/90
```
**Response-fields:**

Field | Type|Description|Since
---|---|---|---
mapKey|array|A map key.|-
-|string|Return string.|-

**Response-example:**
```
{
  "mapKey": [
    "dserv1",
    "h55xu2"
  ]
}
```

### 停止使用设备（释放占用）
**URL:** http://localhost}/autotest/device/stop/{deviceId}

**Type:** POST


**Content-Type:** application/x-www-form-urlencoded;charset=UTF-8

**Description:** 停止使用设备（释放占用）

**Path-parameters:**

Parameter | Type|Required|Description|Since
---|---|---|---|---
deviceId|string|true|// 设备ID|-

**Request-example:**
```
curl -X POST -i http://localhost:8080/autotest/device/stop/90
```

**Response-example:**
```
Return void.
```

### 激活设备
**URL:** http://localhost}/autotest/device/active/{deviceId}

**Type:** POST


**Content-Type:** application/x-www-form-urlencoded;charset=UTF-8

**Description:** 激活设备

**Path-parameters:**

Parameter | Type|Required|Description|Since
---|---|---|---|---
deviceId|string|true|// 设备ID|-

**Request-example:**
```
curl -X POST -i http://localhost:8080/autotest/device/active/90
```

**Response-example:**
```
true
```

### 更新设备信息
**URL:** http://localhost}/autotest/device/update

**Type:** POST


**Content-Type:** application/json

**Description:** 更新设备信息

**Body-parameters:**

Parameter | Type|Required|Description|Since
---|---|---|---|---
id|string|false||No comments found.|-
serial|string|false||No comments found.|-
name|string|false||No comments found.|-
system|string|false||No comments found.|-
brand|string|false||No comments found.|-
model|string|false||No comments found.|-
version|string|false||No comments found.|-
size|string|false||No comments found.|-
sources|string|false||No comments found.|-
owner|string|false||No comments found.|-
user|string|false||No comments found.|-
agent|string|false||No comments found.|-
timeout|int32|false||No comments found.|-
projectId|string|false||No comments found.|-
createTime|int64|false||No comments found.|-
updateTime|int64|false||No comments found.|-
status|string|false||No comments found.|-

**Request-example:**
```
curl -X POST -H 'Content-Type: application/json' -i http://localhost:8080/autotest/device/update --data '{
  "id": "90",
  "serial": "q79zds",
  "name": "laronda.predovic",
  "system": "i8cvd6",
  "brand": "yz1j8c",
  "model": "fljvy9",
  "version": "0.8.1",
  "size": "441sl6",
  "sources": "erqofa",
  "owner": "3f7lpn",
  "user": "oj9qcx",
  "agent": "svnop4",
  "timeout": 209,
  "projectId": "90",
  "createTime": 1759765053864,
  "updateTime": 1759765053864,
  "status": "vadnr2"
}'
```

**Response-example:**
```
Return void.
```

### 占用设备（设置占用超时时间）
**URL:** http://localhost}/autotest/device/use/{deviceId}/{timeout}

**Type:** POST


**Content-Type:** application/x-www-form-urlencoded;charset=UTF-8

**Description:** 占用设备（设置占用超时时间）

**Path-parameters:**

Parameter | Type|Required|Description|Since
---|---|---|---|---
deviceId|string|true|// 设备ID|-
timeout|int32|true| // 占用超时时间（分钟）|-

**Request-example:**
```
curl -X POST -i http://localhost:8080/autotest/device/use/90/464
```

**Response-example:**
```
true
```

### 查询设备详情
**URL:** http://localhost}/autotest/device/detail/{deviceId}

**Type:** GET


**Content-Type:** application/x-www-form-urlencoded;charset=UTF-8

**Description:** 查询设备详情

**Path-parameters:**

Parameter | Type|Required|Description|Since
---|---|---|---|---
deviceId|string|true|// 设备ID|-

**Request-example:**
```
curl -X GET -i http://localhost:8080/autotest/device/detail/90
```
**Response-fields:**

Field | Type|Description|Since
---|---|---|---
id|string|No comments found.|-
serial|string|No comments found.|-
name|string|No comments found.|-
system|string|No comments found.|-
brand|string|No comments found.|-
model|string|No comments found.|-
version|string|No comments found.|-
size|string|No comments found.|-
sources|string|No comments found.|-
owner|string|No comments found.|-
user|string|No comments found.|-
agent|string|No comments found.|-
timeout|int32|No comments found.|-
projectId|string|No comments found.|-
createTime|int64|No comments found.|-
updateTime|int64|No comments found.|-
status|string|No comments found.|-

**Response-example:**
```
{
  "id": "90",
  "serial": "ww38xo",
  "name": "laronda.predovic",
  "system": "2itz1z",
  "brand": "mgnfj6",
  "model": "ikd6gp",
  "version": "0.8.1",
  "size": "ervbj5",
  "sources": "lc0u8a",
  "owner": "a8v8go",
  "user": "rs7xi5",
  "agent": "9l2hx8",
  "timeout": 440,
  "projectId": "90",
  "createTime": 1759765053864,
  "updateTime": 1759765053864,
  "status": "ga6asi"
}
```

### 条件查询设备列表
**URL:** http://localhost}/autotest/device/list

**Type:** POST


**Content-Type:** application/json

**Description:** 条件查询设备列表

**Body-parameters:**

Parameter | Type|Required|Description|Since
---|---|---|---|---
condition|string|false||No comments found.|-
moduleId|string|false||No comments found.|-
createUser|string|false||No comments found.|-
projectId|string|false||No comments found.|-
caseType|string|false||No comments found.|-
collectionId|string|false||No comments found.|-
planId|string|false||No comments found.|-
operationType|string|false||No comments found.|-
roleId|string|false||No comments found.|-
requestUser|string|false||No comments found.|-
uiType|string|false||No comments found.|-
system|string|false||No comments found.|-
status|string|false||No comments found.|-
filter|object|false||No comments found.|-
└─map|map|false||No comments found.|-
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;└─any object|object|false||any object.|-

**Request-example:**
```
curl -X POST -H 'Content-Type: application/json' -i http://localhost:8080/autotest/device/list --data '{
  "condition": "r7bb8p",
  "moduleId": "90",
  "createUser": "hhbxtr",
  "projectId": "90",
  "caseType": "lbtjrf",
  "collectionId": "90",
  "planId": "90",
  "operationType": "1pj3g3",
  "roleId": "90",
  "requestUser": "n6ic2e",
  "uiType": "zo7nck",
  "system": "jcgolj",
  "status": "6w4kap",
  "filter": {
    "map": {
      "mapKey": {}
    }
  }
}'
```
**Response-fields:**

Field | Type|Description|Since
---|---|---|---
id|string|No comments found.|-
serial|string|No comments found.|-
name|string|No comments found.|-
system|string|No comments found.|-
brand|string|No comments found.|-
model|string|No comments found.|-
version|string|No comments found.|-
size|string|No comments found.|-
sources|string|No comments found.|-
owner|string|No comments found.|-
user|string|No comments found.|-
agent|string|No comments found.|-
timeout|int32|No comments found.|-
projectId|string|No comments found.|-
createTime|int64|No comments found.|-
updateTime|int64|No comments found.|-
status|string|No comments found.|-
username|string|No comments found.|-

**Response-example:**
```
[
  {
    "id": "90",
    "serial": "ps6l44",
    "name": "laronda.predovic",
    "system": "bt2xtc",
    "brand": "pucho5",
    "model": "tod8de",
    "version": "0.8.1",
    "size": "i8chsh",
    "sources": "muzckx",
    "owner": "u8mda0",
    "user": "6n30pw",
    "agent": "box20a",
    "timeout": 433,
    "projectId": "90",
    "createTime": 1759765053864,
    "updateTime": 1759765053864,
    "status": "vpfae9",
    "username": "laronda.predovic"
  }
]
```

### 按系统类型查询设备列表
**URL:** http://localhost}/autotest/device/{system}/list/{projectId}

**Type:** GET


**Content-Type:** application/x-www-form-urlencoded;charset=UTF-8

**Description:** 按系统类型查询设备列表

**Path-parameters:**

Parameter | Type|Required|Description|Since
---|---|---|---|---
system|string|true|   // 系统类型（android/apple/web等）|-
projectId|string|true|// 项目ID|-

**Request-example:**
```
curl -X GET -i http://localhost:8080/autotest/device/xtdqen/list/90
```
**Response-fields:**

Field | Type|Description|Since
---|---|---|---
id|string|No comments found.|-
serial|string|No comments found.|-
name|string|No comments found.|-
system|string|No comments found.|-
brand|string|No comments found.|-
model|string|No comments found.|-
version|string|No comments found.|-
size|string|No comments found.|-
sources|string|No comments found.|-
owner|string|No comments found.|-
user|string|No comments found.|-
agent|string|No comments found.|-
timeout|int32|No comments found.|-
projectId|string|No comments found.|-
createTime|int64|No comments found.|-
updateTime|int64|No comments found.|-
status|string|No comments found.|-

**Response-example:**
```
[
  {
    "id": "90",
    "serial": "1cus3y",
    "name": "laronda.predovic",
    "system": "x8853h",
    "brand": "7872hk",
    "model": "8298si",
    "version": "0.8.1",
    "size": "z4qw8g",
    "sources": "mddrfd",
    "owner": "nf7cys",
    "user": "35mc5c",
    "agent": "gl16ar",
    "timeout": 290,
    "projectId": "90",
    "createTime": 1759765053864,
    "updateTime": 1759765053864,
    "status": "krygtm"
  }
]
```

## 控制器：域配置接口
    职责：保存；删除；列表查询
### 保存域配置
**URL:** http://localhost}/autotest/domain/save

**Type:** POST


**Content-Type:** application/json

**Description:** 保存域配置

**Body-parameters:**

Parameter | Type|Required|Description|Since
---|---|---|---|---
id|string|false||No comments found.|-
domainKeyType|string|false||No comments found.|-
domainKey|string|false||No comments found.|-
domainData|string|false||No comments found.|-
environmentId|string|false||No comments found.|-
createTime|int64|false||No comments found.|-
updateTime|int64|false||No comments found.|-
createUser|string|false||No comments found.|-
updateUser|string|false||No comments found.|-
status|int32|false||No comments found.|-

**Request-example:**
```
curl -X POST -H 'Content-Type: application/json' -i http://localhost:8080/autotest/domain/save --data '{
  "id": "90",
  "domainKeyType": "7kofzx",
  "domainKey": "z4bi1j",
  "domainData": "b75l66",
  "environmentId": "90",
  "createTime": 1759765053864,
  "updateTime": 1759765053864,
  "createUser": "dhv0vg",
  "updateUser": "idcdgd",
  "status": 226
}'
```

**Response-example:**
```
Return void.
```

### 删除域配置
**URL:** http://localhost}/autotest/domain/delete

**Type:** POST


**Content-Type:** application/json

**Description:** 删除域配置

**Body-parameters:**

Parameter | Type|Required|Description|Since
---|---|---|---|---
id|string|false||No comments found.|-
domainKeyType|string|false||No comments found.|-
domainKey|string|false||No comments found.|-
domainData|string|false||No comments found.|-
environmentId|string|false||No comments found.|-
createTime|int64|false||No comments found.|-
updateTime|int64|false||No comments found.|-
createUser|string|false||No comments found.|-
updateUser|string|false||No comments found.|-
status|int32|false||No comments found.|-

**Request-example:**
```
curl -X POST -H 'Content-Type: application/json' -i http://localhost:8080/autotest/domain/delete --data '{
  "id": "90",
  "domainKeyType": "0gpdug",
  "domainKey": "fb4gnu",
  "domainData": "adrj1b",
  "environmentId": "90",
  "createTime": 1759765053864,
  "updateTime": 1759765053864,
  "createUser": "3cy75h",
  "updateUser": "ach2gc",
  "status": 363
}'
```

**Response-example:**
```
Return void.
```

### 获取环境下域配置列表
**URL:** http://localhost}/autotest/domain/list/{environmentId}

**Type:** GET


**Content-Type:** application/x-www-form-urlencoded;charset=UTF-8

**Description:** 获取环境下域配置列表

**Path-parameters:**

Parameter | Type|Required|Description|Since
---|---|---|---|---
environmentId|string|true|// 环境ID|-

**Request-example:**
```
curl -X GET -i http://localhost:8080/autotest/domain/list/90
```
**Response-fields:**

Field | Type|Description|Since
---|---|---|---
id|string|No comments found.|-
domainKeyType|string|No comments found.|-
domainKey|string|No comments found.|-
domainData|string|No comments found.|-
environmentId|string|No comments found.|-
createTime|int64|No comments found.|-
updateTime|int64|No comments found.|-
createUser|string|No comments found.|-
updateUser|string|No comments found.|-
status|int32|No comments found.|-
DomainSignName|string|No comments found.|-

**Response-example:**
```
[
  {
    "id": "90",
    "domainKeyType": "43g2yr",
    "domainKey": "ylv3bw",
    "domainData": "j21ufn",
    "environmentId": "90",
    "createTime": 1759765053864,
    "updateTime": 1759765053864,
    "createUser": "impzox",
    "updateUser": "0hpe8c",
    "status": 621,
    "DomainSignName": "laronda.predovic"
  }
]
```

## 控制器：DomainSign 域标识管理入口
职责：提供域标识的创建、删除、列表与分页查询接口。
### 新增或更新域标识
**URL:** http://localhost}/autotest/domainSign/save

**Type:** POST


**Content-Type:** application/json

**Description:** 新增或更新域标识

**Body-parameters:**

Parameter | Type|Required|Description|Since
---|---|---|---|---
id|string|false||No comments found.|-
name|string|false||No comments found.|-
description|string|false||No comments found.|-
projectId|string|false||No comments found.|-
createTime|int64|false||No comments found.|-
updateTime|int64|false||No comments found.|-

**Request-example:**
```
curl -X POST -H 'Content-Type: application/json' -i http://localhost:8080/autotest/domainSign/save --data '{
  "id": "90",
  "name": "laronda.predovic",
  "description": "fzq60x",
  "projectId": "90",
  "createTime": 1759765053864,
  "updateTime": 1759765053864
}'
```

**Response-example:**
```
Return void.
```

### 删除域标识（逻辑删除）
**URL:** http://localhost}/autotest/domainSign/delete

**Type:** POST


**Content-Type:** application/json

**Description:** 删除域标识（逻辑删除）

**Body-parameters:**

Parameter | Type|Required|Description|Since
---|---|---|---|---
id|string|false||No comments found.|-
name|string|false||No comments found.|-
description|string|false||No comments found.|-
projectId|string|false||No comments found.|-
createTime|int64|false||No comments found.|-
updateTime|int64|false||No comments found.|-

**Request-example:**
```
curl -X POST -H 'Content-Type: application/json' -i http://localhost:8080/autotest/domainSign/delete --data '{
  "id": "90",
  "name": "laronda.predovic",
  "description": "p2eif0",
  "projectId": "90",
  "createTime": 1759765053864,
  "updateTime": 1759765053864
}'
```

**Response-example:**
```
Return void.
```

### 根据项目查询域标识列表
**URL:** http://localhost}/autotest/domainSign/list/{projectId}

**Type:** GET


**Content-Type:** application/x-www-form-urlencoded;charset=UTF-8

**Description:** 根据项目查询域标识列表

**Path-parameters:**

Parameter | Type|Required|Description|Since
---|---|---|---|---
projectId|string|true|      // 项目ID|-

**Request-example:**
```
curl -X GET -i http://localhost:8080/autotest/domainSign/list/90
```
**Response-fields:**

Field | Type|Description|Since
---|---|---|---
id|string|No comments found.|-
name|string|No comments found.|-
description|string|No comments found.|-
projectId|string|No comments found.|-
createTime|int64|No comments found.|-
updateTime|int64|No comments found.|-

**Response-example:**
```
[
  {
    "id": "90",
    "name": "laronda.predovic",
    "description": "kw1lnx",
    "projectId": "90",
    "createTime": 1759765053864,
    "updateTime": 1759765053864
  }
]
```

### 分页查询域标识列表<br><br>说明：统一使用 PageHelper 进行分页拦截，返回 Pager。
**URL:** http://localhost}/autotest/domainSign/list/{goPage}/{pageSize}

**Type:** POST


**Content-Type:** application/json

**Description:** 分页查询域标识列表

说明：统一使用 PageHelper 进行分页拦截，返回 Pager。

**Path-parameters:**

Parameter | Type|Required|Description|Since
---|---|---|---|---
goPage|int32|true|   // 页码|-
pageSize|int32|true| // 每页大小|-

**Body-parameters:**

Parameter | Type|Required|Description|Since
---|---|---|---|---
condition|string|false||No comments found.|-
moduleId|string|false||No comments found.|-
createUser|string|false||No comments found.|-
projectId|string|false||No comments found.|-
caseType|string|false||No comments found.|-
collectionId|string|false||No comments found.|-
planId|string|false||No comments found.|-
operationType|string|false||No comments found.|-
roleId|string|false||No comments found.|-
requestUser|string|false||No comments found.|-
uiType|string|false||No comments found.|-
system|string|false||No comments found.|-
status|string|false||No comments found.|-
filter|object|false||No comments found.|-
└─map|map|false||No comments found.|-
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;└─any object|object|false||any object.|-

**Request-example:**
```
curl -X POST -H 'Content-Type: application/json' -i http://localhost:8080/autotest/domainSign/list/1/10 --data '{
  "condition": "lyabgf",
  "moduleId": "90",
  "createUser": "b2eucd",
  "projectId": "90",
  "caseType": "02nbnm",
  "collectionId": "90",
  "planId": "90",
  "operationType": "6tezol",
  "roleId": "90",
  "requestUser": "krp21j",
  "uiType": "oetzd0",
  "system": "kv8p57",
  "status": "x2g85o",
  "filter": {
    "map": {
      "mapKey": {}
    }
  }
}'
```
**Response-fields:**

Field | Type|Description|Since
---|---|---|---
list|array|No comments found.|-
└─id|string|No comments found.|-
└─name|string|No comments found.|-
└─description|string|No comments found.|-
└─projectId|string|No comments found.|-
└─createTime|int64|No comments found.|-
└─updateTime|int64|No comments found.|-
total|int64|No comments found.|-

**Response-example:**
```
{
  "list": [
    {
      "id": "90",
      "name": "laronda.predovic",
      "description": "2i9h9d",
      "projectId": "90",
      "createTime": 1759765053864,
      "updateTime": 1759765053864
    }
  ],
  "total": 848
}
```

## 控制器：驱动配置入口
职责：保存、删除、项目驱动查询与分页列表
### 功能：保存驱动配置
**URL:** http://localhost}/autotest/driver/save

**Type:** POST


**Content-Type:** application/json

**Description:** 功能：保存驱动配置

**Body-parameters:**

Parameter | Type|Required|Description|Since
---|---|---|---|---
id|string|false||No comments found.|-
name|string|false||No comments found.|-
setting|string|false||No comments found.|-
description|string|false||No comments found.|-
projectId|string|false||No comments found.|-
createTime|int64|false||No comments found.|-
updateTime|int64|false||No comments found.|-

**Request-example:**
```
curl -X POST -H 'Content-Type: application/json' -i http://localhost:8080/autotest/driver/save --data '{
  "id": "90",
  "name": "laronda.predovic",
  "setting": "w9tgch",
  "description": "4eus9u",
  "projectId": "90",
  "createTime": 1759765053864,
  "updateTime": 1759765053864
}'
```

**Response-example:**
```
Return void.
```

### 功能：删除驱动配置
**URL:** http://localhost}/autotest/driver/delete

**Type:** POST


**Content-Type:** application/json

**Description:** 功能：删除驱动配置

**Body-parameters:**

Parameter | Type|Required|Description|Since
---|---|---|---|---
id|string|false||No comments found.|-
name|string|false||No comments found.|-
setting|string|false||No comments found.|-
description|string|false||No comments found.|-
projectId|string|false||No comments found.|-
createTime|int64|false||No comments found.|-
updateTime|int64|false||No comments found.|-

**Request-example:**
```
curl -X POST -H 'Content-Type: application/json' -i http://localhost:8080/autotest/driver/delete --data '{
  "id": "90",
  "name": "laronda.predovic",
  "setting": "oiu2kb",
  "description": "9okc5e",
  "projectId": "90",
  "createTime": 1759765053864,
  "updateTime": 1759765053864
}'
```

**Response-example:**
```
Return void.
```

### 功能：查询项目下所有驱动
**URL:** http://localhost}/autotest/driver/list/{projectId}

**Type:** GET


**Content-Type:** application/x-www-form-urlencoded;charset=UTF-8

**Description:** 功能：查询项目下所有驱动

**Path-parameters:**

Parameter | Type|Required|Description|Since
---|---|---|---|---
projectId|string|true|// 项目ID|-

**Request-example:**
```
curl -X GET -i http://localhost:8080/autotest/driver/list/90
```
**Response-fields:**

Field | Type|Description|Since
---|---|---|---
id|string|No comments found.|-
name|string|No comments found.|-
setting|string|No comments found.|-
description|string|No comments found.|-
projectId|string|No comments found.|-
createTime|int64|No comments found.|-
updateTime|int64|No comments found.|-

**Response-example:**
```
[
  {
    "id": "90",
    "name": "laronda.predovic",
    "setting": "l0xw3b",
    "description": "a7k866",
    "projectId": "90",
    "createTime": 1759765053864,
    "updateTime": 1759765053864
  }
]
```

### 功能：分页查询驱动列表
**URL:** http://localhost}/autotest/driver/list/{goPage}/{pageSize}

**Type:** POST


**Content-Type:** application/json

**Description:** 功能：分页查询驱动列表

**Path-parameters:**

Parameter | Type|Required|Description|Since
---|---|---|---|---
goPage|int32|true|   // 页码|-
pageSize|int32|true| // 每页大小|-

**Body-parameters:**

Parameter | Type|Required|Description|Since
---|---|---|---|---
condition|string|false||No comments found.|-
moduleId|string|false||No comments found.|-
createUser|string|false||No comments found.|-
projectId|string|false||No comments found.|-
caseType|string|false||No comments found.|-
collectionId|string|false||No comments found.|-
planId|string|false||No comments found.|-
operationType|string|false||No comments found.|-
roleId|string|false||No comments found.|-
requestUser|string|false||No comments found.|-
uiType|string|false||No comments found.|-
system|string|false||No comments found.|-
status|string|false||No comments found.|-
filter|object|false||No comments found.|-
└─map|map|false||No comments found.|-
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;└─any object|object|false||any object.|-

**Request-example:**
```
curl -X POST -H 'Content-Type: application/json' -i http://localhost:8080/autotest/driver/list/1/10 --data '{
  "condition": "554y59",
  "moduleId": "90",
  "createUser": "9z0z2r",
  "projectId": "90",
  "caseType": "taf5j1",
  "collectionId": "90",
  "planId": "90",
  "operationType": "jzr5eq",
  "roleId": "90",
  "requestUser": "5ae61x",
  "uiType": "05tcbx",
  "system": "lqka6f",
  "status": "kenovl",
  "filter": {
    "map": {
      "mapKey": {}
    }
  }
}'
```
**Response-fields:**

Field | Type|Description|Since
---|---|---|---
list|array|No comments found.|-
└─id|string|No comments found.|-
└─name|string|No comments found.|-
└─setting|string|No comments found.|-
└─description|string|No comments found.|-
└─projectId|string|No comments found.|-
└─createTime|int64|No comments found.|-
└─updateTime|int64|No comments found.|-
total|int64|No comments found.|-

**Response-example:**
```
{
  "list": [
    {
      "id": "90",
      "name": "laronda.predovic",
      "setting": "qze9sc",
      "description": "wjhdft",
      "projectId": "90",
      "createTime": 1759765053864,
      "updateTime": 1759765053864
    }
  ],
  "total": 677
}
```

## 控制器：页面元素入口
用途：保存、删除、详情与分页列表查询
### 保存页面元素
**URL:** http://localhost}/autotest/element/save

**Type:** POST


**Content-Type:** application/json

**Description:** 保存页面元素

**Body-parameters:**

Parameter | Type|Required|Description|Since
---|---|---|---|---
id|string|false||No comments found.|-
num|int64|false||No comments found.|-
name|string|false||No comments found.|-
moduleId|string|false||No comments found.|-
projectId|string|false||No comments found.|-
by|string|false||No comments found.|-
expression|string|false||No comments found.|-
description|string|false||No comments found.|-
createTime|int64|false||No comments found.|-
updateTime|int64|false||No comments found.|-
createUser|string|false||No comments found.|-
updateUser|string|false||No comments found.|-
status|string|false||No comments found.|-

**Request-example:**
```
curl -X POST -H 'Content-Type: application/json' -i http://localhost:8080/autotest/element/save --data '{
  "id": "90",
  "num": 712,
  "name": "laronda.predovic",
  "moduleId": "90",
  "projectId": "90",
  "by": "4cjsgf",
  "expression": "qmstst",
  "description": "mux62d",
  "createTime": 1759765053864,
  "updateTime": 1759765053864,
  "createUser": "i9imby",
  "updateUser": "di20l3",
  "status": "g1tajk"
}'
```

**Response-example:**
```
Return void.
```

### 删除页面元素
**URL:** http://localhost}/autotest/element/delete

**Type:** POST


**Content-Type:** application/json

**Description:** 删除页面元素

**Body-parameters:**

Parameter | Type|Required|Description|Since
---|---|---|---|---
id|string|false||No comments found.|-
num|int64|false||No comments found.|-
name|string|false||No comments found.|-
moduleId|string|false||No comments found.|-
projectId|string|false||No comments found.|-
by|string|false||No comments found.|-
expression|string|false||No comments found.|-
description|string|false||No comments found.|-
createTime|int64|false||No comments found.|-
updateTime|int64|false||No comments found.|-
createUser|string|false||No comments found.|-
updateUser|string|false||No comments found.|-
status|string|false||No comments found.|-

**Request-example:**
```
curl -X POST -H 'Content-Type: application/json' -i http://localhost:8080/autotest/element/delete --data '{
  "id": "90",
  "num": 434,
  "name": "laronda.predovic",
  "moduleId": "90",
  "projectId": "90",
  "by": "m5vtza",
  "expression": "l3o68y",
  "description": "hiixn3",
  "createTime": 1759765053864,
  "updateTime": 1759765053864,
  "createUser": "884ej2",
  "updateUser": "r7xlo9",
  "status": "z5fiub"
}'
```

**Response-example:**
```
Return void.
```

### 查询模块下元素列表
**URL:** http://localhost}/autotest/element/list/module

**Type:** POST


**Content-Type:** application/json

**Description:** 查询模块下元素列表

**Body-parameters:**

Parameter | Type|Required|Description|Since
---|---|---|---|---
condition|string|false||No comments found.|-
moduleId|string|false||No comments found.|-
createUser|string|false||No comments found.|-
projectId|string|false||No comments found.|-
caseType|string|false||No comments found.|-
collectionId|string|false||No comments found.|-
planId|string|false||No comments found.|-
operationType|string|false||No comments found.|-
roleId|string|false||No comments found.|-
requestUser|string|false||No comments found.|-
uiType|string|false||No comments found.|-
system|string|false||No comments found.|-
status|string|false||No comments found.|-
filter|object|false||No comments found.|-
└─map|map|false||No comments found.|-
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;└─any object|object|false||any object.|-

**Request-example:**
```
curl -X POST -H 'Content-Type: application/json' -i http://localhost:8080/autotest/element/list/module --data '{
  "condition": "mfyz9v",
  "moduleId": "90",
  "createUser": "8dwkyw",
  "projectId": "90",
  "caseType": "yqrdgo",
  "collectionId": "90",
  "planId": "90",
  "operationType": "dfxn79",
  "roleId": "90",
  "requestUser": "lkbq12",
  "uiType": "gwqn95",
  "system": "g6nn5r",
  "status": "i2jokr",
  "filter": {
    "map": {
      "mapKey": {}
    }
  }
}'
```
**Response-fields:**

Field | Type|Description|Since
---|---|---|---
id|string|No comments found.|-
num|int64|No comments found.|-
name|string|No comments found.|-
moduleId|string|No comments found.|-
projectId|string|No comments found.|-
by|string|No comments found.|-
expression|string|No comments found.|-
description|string|No comments found.|-
createTime|int64|No comments found.|-
updateTime|int64|No comments found.|-
createUser|string|No comments found.|-
updateUser|string|No comments found.|-
status|string|No comments found.|-

**Response-example:**
```
[
  {
    "id": "90",
    "num": 260,
    "name": "laronda.predovic",
    "moduleId": "90",
    "projectId": "90",
    "by": "z62f5r",
    "expression": "1uxz90",
    "description": "zt1m51",
    "createTime": 1759765053864,
    "updateTime": 1759765053864,
    "createUser": "t246e8",
    "updateUser": "s7esde",
    "status": "4yyy7u"
  }
]
```

### 分页查询元素列表
**URL:** http://localhost}/autotest/element/list/{goPage}/{pageSize}

**Type:** POST


**Content-Type:** application/json

**Description:** 分页查询元素列表

**Path-parameters:**

Parameter | Type|Required|Description|Since
---|---|---|---|---
goPage|int32|true|    // 页码|-
pageSize|int32|true|  // 每页数量|-

**Body-parameters:**

Parameter | Type|Required|Description|Since
---|---|---|---|---
condition|string|false||No comments found.|-
moduleId|string|false||No comments found.|-
createUser|string|false||No comments found.|-
projectId|string|false||No comments found.|-
caseType|string|false||No comments found.|-
collectionId|string|false||No comments found.|-
planId|string|false||No comments found.|-
operationType|string|false||No comments found.|-
roleId|string|false||No comments found.|-
requestUser|string|false||No comments found.|-
uiType|string|false||No comments found.|-
system|string|false||No comments found.|-
status|string|false||No comments found.|-
filter|object|false||No comments found.|-
└─map|map|false||No comments found.|-
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;└─any object|object|false||any object.|-

**Request-example:**
```
curl -X POST -H 'Content-Type: application/json' -i http://localhost:8080/autotest/element/list/1/10 --data '{
  "condition": "8ffblr",
  "moduleId": "90",
  "createUser": "sfjmrw",
  "projectId": "90",
  "caseType": "yzkscb",
  "collectionId": "90",
  "planId": "90",
  "operationType": "bpdgyo",
  "roleId": "90",
  "requestUser": "35o6hu",
  "uiType": "fbn8qu",
  "system": "ot054x",
  "status": "7l9lto",
  "filter": {
    "map": {
      "mapKey": {}
    }
  }
}'
```
**Response-fields:**

Field | Type|Description|Since
---|---|---|---
list|array|No comments found.|-
└─id|string|No comments found.|-
└─num|int64|No comments found.|-
└─name|string|No comments found.|-
└─moduleId|string|No comments found.|-
└─projectId|string|No comments found.|-
└─by|string|No comments found.|-
└─expression|string|No comments found.|-
└─description|string|No comments found.|-
└─createTime|int64|No comments found.|-
└─updateTime|int64|No comments found.|-
└─createUser|string|No comments found.|-
└─updateUser|string|No comments found.|-
└─status|string|No comments found.|-
└─moduleName|string|No comments found.|-
└─username|string|No comments found.|-
total|int64|No comments found.|-

**Response-example:**
```
{
  "list": [
    {
      "id": "90",
      "num": 366,
      "name": "laronda.predovic",
      "moduleId": "90",
      "projectId": "90",
      "by": "6g3g1y",
      "expression": "v47af7",
      "description": "kqve5u",
      "createTime": 1759765053864,
      "updateTime": 1759765053864,
      "createUser": "dx3tle",
      "updateUser": "m3dfdv",
      "status": "ui2614",
      "moduleName": "laronda.predovic",
      "username": "laronda.predovic"
    }
  ],
  "total": 408
}
```

## 控制器：执行引擎入口
职责：注册/删除引擎、停止任务、详情与分页列表
### 功能：注册或更新引擎
**URL:** http://localhost}/autotest/engine/register

**Type:** POST


**Content-Type:** application/json

**Description:** 功能：注册或更新引擎

**Body-parameters:**

Parameter | Type|Required|Description|Since
---|---|---|---|---
id|string|false||No comments found.|-
name|string|false||No comments found.|-
engineType|string|false||No comments found.|-
secret|string|false||No comments found.|-
status|string|false||No comments found.|-
lastHeartbeatTime|int64|false||No comments found.|-
projectId|string|false||No comments found.|-
createUser|string|false||No comments found.|-
updateUser|string|false||No comments found.|-
createTime|int64|false||No comments found.|-
updateTime|int64|false||No comments found.|-

**Request-example:**
```
curl -X POST -H 'Content-Type: application/json' -i http://localhost:8080/autotest/engine/register --data '{
  "id": "90",
  "name": "laronda.predovic",
  "engineType": "d1shlf",
  "secret": "bwljh3",
  "status": "va0rc1",
  "lastHeartbeatTime": 1759765053864,
  "projectId": "90",
  "createUser": "6xu1mj",
  "updateUser": "43wkmk",
  "createTime": 1759765053864,
  "updateTime": 1759765053864
}'
```
**Response-fields:**

Field | Type|Description|Since
---|---|---|---
id|string|No comments found.|-
name|string|No comments found.|-
engineType|string|No comments found.|-
secret|string|No comments found.|-
status|string|No comments found.|-
lastHeartbeatTime|int64|No comments found.|-
projectId|string|No comments found.|-
createUser|string|No comments found.|-
updateUser|string|No comments found.|-
createTime|int64|No comments found.|-
updateTime|int64|No comments found.|-

**Response-example:**
```
{
  "id": "90",
  "name": "laronda.predovic",
  "engineType": "9q7zq1",
  "secret": "osuiad",
  "status": "vbvwaq",
  "lastHeartbeatTime": 1759765053864,
  "projectId": "90",
  "createUser": "dok94t",
  "updateUser": "b1nbtg",
  "createTime": 1759765053864,
  "updateTime": 1759765053864
}
```

### 功能：删除引擎
**URL:** http://localhost}/autotest/engine/delete

**Type:** POST


**Content-Type:** application/json

**Description:** 功能：删除引擎

**Body-parameters:**

Parameter | Type|Required|Description|Since
---|---|---|---|---
id|string|false||No comments found.|-
name|string|false||No comments found.|-
engineType|string|false||No comments found.|-
secret|string|false||No comments found.|-
status|string|false||No comments found.|-
lastHeartbeatTime|int64|false||No comments found.|-
projectId|string|false||No comments found.|-
createUser|string|false||No comments found.|-
updateUser|string|false||No comments found.|-
createTime|int64|false||No comments found.|-
updateTime|int64|false||No comments found.|-

**Request-example:**
```
curl -X POST -H 'Content-Type: application/json' -i http://localhost:8080/autotest/engine/delete --data '{
  "id": "90",
  "name": "laronda.predovic",
  "engineType": "zodos4",
  "secret": "jbv2cn",
  "status": "xpwa2f",
  "lastHeartbeatTime": 1759765053864,
  "projectId": "90",
  "createUser": "p5u37m",
  "updateUser": "1pvphs",
  "createTime": 1759765053864,
  "updateTime": 1759765053864
}'
```

**Response-example:**
```
Return void.
```

### 功能：停止引擎上的指定任务
**URL:** http://localhost}/autotest/engine/stop/task

**Type:** POST


**Content-Type:** application/json

**Description:** 功能：停止引擎上的指定任务

**Body-parameters:**

Parameter | Type|Required|Description|Since
---|---|---|---|---
id|string|false||No comments found.|-
name|string|false||No comments found.|-
type|string|false||No comments found.|-
status|string|false||No comments found.|-
engineId|string|false||No comments found.|-
projectId|string|false||No comments found.|-
createTime|int64|false||No comments found.|-
updateTime|int64|false||No comments found.|-
createUser|string|false||No comments found.|-
updateUser|string|false||No comments found.|-

**Request-example:**
```
curl -X POST -H 'Content-Type: application/json' -i http://localhost:8080/autotest/engine/stop/task --data '{
  "id": "90",
  "name": "laronda.predovic",
  "type": "n9jyvl",
  "status": "8je07s",
  "engineId": "90",
  "projectId": "90",
  "createTime": 1759765053864,
  "updateTime": 1759765053864,
  "createUser": "xxt9kl",
  "updateUser": "vrl2pg"
}'
```

**Response-example:**
```
Return void.
```

### 功能：停止引擎上所有任务
**URL:** http://localhost}/autotest/engine/stop/all/task

**Type:** POST


**Content-Type:** application/json

**Description:** 功能：停止引擎上所有任务

**Body-parameters:**

Parameter | Type|Required|Description|Since
---|---|---|---|---
id|string|false||No comments found.|-
name|string|false||No comments found.|-
engineType|string|false||No comments found.|-
secret|string|false||No comments found.|-
status|string|false||No comments found.|-
lastHeartbeatTime|int64|false||No comments found.|-
projectId|string|false||No comments found.|-
createUser|string|false||No comments found.|-
updateUser|string|false||No comments found.|-
createTime|int64|false||No comments found.|-
updateTime|int64|false||No comments found.|-

**Request-example:**
```
curl -X POST -H 'Content-Type: application/json' -i http://localhost:8080/autotest/engine/stop/all/task --data '{
  "id": "90",
  "name": "laronda.predovic",
  "engineType": "6wt4dr",
  "secret": "n71fzq",
  "status": "m39j3z",
  "lastHeartbeatTime": 1759765053864,
  "projectId": "90",
  "createUser": "yi8fnp",
  "updateUser": "qwjzyp",
  "createTime": 1759765053864,
  "updateTime": 1759765053864
}'
```

**Response-example:**
```
Return void.
```

### 功能：查询项目下所有自定义引擎
**URL:** http://localhost}/autotest/engine/all/{projectId}

**Type:** GET


**Content-Type:** application/x-www-form-urlencoded;charset=UTF-8

**Description:** 功能：查询项目下所有自定义引擎

**Path-parameters:**

Parameter | Type|Required|Description|Since
---|---|---|---|---
projectId|string|true|// 项目ID|-

**Request-example:**
```
curl -X GET -i http://localhost:8080/autotest/engine/all/90
```
**Response-fields:**

Field | Type|Description|Since
---|---|---|---
id|string|No comments found.|-
name|string|No comments found.|-
engineType|string|No comments found.|-
secret|string|No comments found.|-
status|string|No comments found.|-
lastHeartbeatTime|int64|No comments found.|-
projectId|string|No comments found.|-
createUser|string|No comments found.|-
updateUser|string|No comments found.|-
createTime|int64|No comments found.|-
updateTime|int64|No comments found.|-

**Response-example:**
```
[
  {
    "id": "90",
    "name": "laronda.predovic",
    "engineType": "msudg3",
    "secret": "my62xe",
    "status": "xs56qb",
    "lastHeartbeatTime": 1759765053864,
    "projectId": "90",
    "createUser": "o0vhgd",
    "updateUser": "lo1c90",
    "createTime": 1759765053864,
    "updateTime": 1759765053864
  }
]
```

### 功能：查询引擎详情
**URL:** http://localhost}/autotest/engine/detail/{engineId}

**Type:** GET


**Content-Type:** application/x-www-form-urlencoded;charset=UTF-8

**Description:** 功能：查询引擎详情

**Path-parameters:**

Parameter | Type|Required|Description|Since
---|---|---|---|---
engineId|string|true|// 引擎ID|-

**Request-example:**
```
curl -X GET -i http://localhost:8080/autotest/engine/detail/90
```
**Response-fields:**

Field | Type|Description|Since
---|---|---|---
id|string|No comments found.|-
name|string|No comments found.|-
engineType|string|No comments found.|-
secret|string|No comments found.|-
status|string|No comments found.|-
lastHeartbeatTime|int64|No comments found.|-
projectId|string|No comments found.|-
createUser|string|No comments found.|-
updateUser|string|No comments found.|-
createTime|int64|No comments found.|-
updateTime|int64|No comments found.|-
username|string|No comments found.|-
taskList|array|No comments found.|-
└─id|string|No comments found.|-
└─name|string|No comments found.|-
└─type|string|No comments found.|-
└─status|string|No comments found.|-
└─engineId|string|No comments found.|-
└─projectId|string|No comments found.|-
└─createTime|int64|No comments found.|-
└─updateTime|int64|No comments found.|-
└─createUser|string|No comments found.|-
└─updateUser|string|No comments found.|-
└─username|string|No comments found.|-
└─reportId|string|No comments found.|-
└─sourceType|string|No comments found.|-
└─sourceId|string|No comments found.|-
└─environmentId|string|No comments found.|-
└─deviceId|string|No comments found.|-

**Response-example:**
```
{
  "id": "90",
  "name": "laronda.predovic",
  "engineType": "w9cr1w",
  "secret": "61757u",
  "status": "mp7dvq",
  "lastHeartbeatTime": 1759765053864,
  "projectId": "90",
  "createUser": "73tqrj",
  "updateUser": "1nn8xw",
  "createTime": 1759765053864,
  "updateTime": 1759765053864,
  "username": "laronda.predovic",
  "taskList": [
    {
      "id": "90",
      "name": "laronda.predovic",
      "type": "rw1n8t",
      "status": "k694oz",
      "engineId": "90",
      "projectId": "90",
      "createTime": 1759765053864,
      "updateTime": 1759765053864,
      "createUser": "61795x",
      "updateUser": "a1n9ea",
      "username": "laronda.predovic",
      "reportId": "90",
      "sourceType": "ppl6ol",
      "sourceId": "90",
      "environmentId": "90",
      "deviceId": "90"
    }
  ]
}
```

### 功能：分页查询引擎列表
**URL:** http://localhost}/autotest/engine/list/{goPage}/{pageSize}

**Type:** POST


**Content-Type:** application/json

**Description:** 功能：分页查询引擎列表

**Path-parameters:**

Parameter | Type|Required|Description|Since
---|---|---|---|---
goPage|int32|true|   // 页码|-
pageSize|int32|true| // 每页大小|-

**Body-parameters:**

Parameter | Type|Required|Description|Since
---|---|---|---|---
condition|string|false||No comments found.|-
moduleId|string|false||No comments found.|-
createUser|string|false||No comments found.|-
projectId|string|false||No comments found.|-
caseType|string|false||No comments found.|-
collectionId|string|false||No comments found.|-
planId|string|false||No comments found.|-
operationType|string|false||No comments found.|-
roleId|string|false||No comments found.|-
requestUser|string|false||No comments found.|-
uiType|string|false||No comments found.|-
system|string|false||No comments found.|-
status|string|false||No comments found.|-
filter|object|false||No comments found.|-
└─map|map|false||No comments found.|-
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;└─any object|object|false||any object.|-

**Request-example:**
```
curl -X POST -H 'Content-Type: application/json' -i http://localhost:8080/autotest/engine/list/1/10 --data '{
  "condition": "xl89lg",
  "moduleId": "90",
  "createUser": "gddtx9",
  "projectId": "90",
  "caseType": "cis7o9",
  "collectionId": "90",
  "planId": "90",
  "operationType": "375ypp",
  "roleId": "90",
  "requestUser": "4yrmf2",
  "uiType": "jmyq72",
  "system": "xpokx9",
  "status": "hfi1of",
  "filter": {
    "map": {
      "mapKey": {}
    }
  }
}'
```
**Response-fields:**

Field | Type|Description|Since
---|---|---|---
list|array|No comments found.|-
└─id|string|No comments found.|-
└─name|string|No comments found.|-
└─engineType|string|No comments found.|-
└─secret|string|No comments found.|-
└─status|string|No comments found.|-
└─lastHeartbeatTime|int64|No comments found.|-
└─projectId|string|No comments found.|-
└─createUser|string|No comments found.|-
└─updateUser|string|No comments found.|-
└─createTime|int64|No comments found.|-
└─updateTime|int64|No comments found.|-
└─username|string|No comments found.|-
└─taskList|array|No comments found.|-
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;└─id|string|No comments found.|-
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;└─name|string|No comments found.|-
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;└─type|string|No comments found.|-
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;└─status|string|No comments found.|-
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;└─engineId|string|No comments found.|-
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;└─projectId|string|No comments found.|-
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;└─createTime|int64|No comments found.|-
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;└─updateTime|int64|No comments found.|-
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;└─createUser|string|No comments found.|-
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;└─updateUser|string|No comments found.|-
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;└─username|string|No comments found.|-
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;└─reportId|string|No comments found.|-
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;└─sourceType|string|No comments found.|-
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;└─sourceId|string|No comments found.|-
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;└─environmentId|string|No comments found.|-
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;└─deviceId|string|No comments found.|-
total|int64|No comments found.|-

**Response-example:**
```
{
  "list": [
    {
      "id": "90",
      "name": "laronda.predovic",
      "engineType": "98l2ca",
      "secret": "rtnloa",
      "status": "ukgm1g",
      "lastHeartbeatTime": 1759765053864,
      "projectId": "90",
      "createUser": "5svsls",
      "updateUser": "c8h72s",
      "createTime": 1759765053864,
      "updateTime": 1759765053864,
      "username": "laronda.predovic",
      "taskList": [
        {
          "id": "90",
          "name": "laronda.predovic",
          "type": "f4720c",
          "status": "69dzj1",
          "engineId": "90",
          "projectId": "90",
          "createTime": 1759765053864,
          "updateTime": 1759765053864,
          "createUser": "zv98pa",
          "updateUser": "ff2rqe",
          "username": "laronda.predovic",
          "reportId": "90",
          "sourceType": "k67i5h",
          "sourceId": "90",
          "environmentId": "90",
          "deviceId": "90"
        }
      ]
    }
  ],
  "total": 498
}
```

## 控制器：环境管理入口
职责：保存、删除、查询全部环境与分页列表
### 功能：保存环境（新增或更新）
**URL:** http://localhost}/autotest/environment/save

**Type:** POST


**Content-Type:** application/json

**Description:** 功能：保存环境（新增或更新）

**Body-parameters:**

Parameter | Type|Required|Description|Since
---|---|---|---|---
id|string|false||No comments found.|-
name|string|false||No comments found.|-
projectId|string|false||No comments found.|-
description|string|false||No comments found.|-
createTime|int64|false||No comments found.|-
updateTime|int64|false||No comments found.|-
createUser|string|false||No comments found.|-
updateUser|string|false||No comments found.|-
status|int32|false||No comments found.|-

**Request-example:**
```
curl -X POST -H 'Content-Type: application/json' -i http://localhost:8080/autotest/environment/save --data '{
  "id": "90",
  "name": "laronda.predovic",
  "projectId": "90",
  "description": "ymt5d5",
  "createTime": 1759765053864,
  "updateTime": 1759765053864,
  "createUser": "cfa532",
  "updateUser": "hvay9g",
  "status": 172
}'
```

**Response-example:**
```
Return void.
```

### 功能：删除环境
**URL:** http://localhost}/autotest/environment/delete

**Type:** POST


**Content-Type:** application/json

**Description:** 功能：删除环境

**Body-parameters:**

Parameter | Type|Required|Description|Since
---|---|---|---|---
id|string|false||No comments found.|-
name|string|false||No comments found.|-
projectId|string|false||No comments found.|-
description|string|false||No comments found.|-
createTime|int64|false||No comments found.|-
updateTime|int64|false||No comments found.|-
createUser|string|false||No comments found.|-
updateUser|string|false||No comments found.|-
status|int32|false||No comments found.|-

**Request-example:**
```
curl -X POST -H 'Content-Type: application/json' -i http://localhost:8080/autotest/environment/delete --data '{
  "id": "90",
  "name": "laronda.predovic",
  "projectId": "90",
  "description": "7epd1t",
  "createTime": 1759765053864,
  "updateTime": 1759765053864,
  "createUser": "dea4j7",
  "updateUser": "kppxmq",
  "status": 951
}'
```

**Response-example:**
```
Return void.
```

### 功能：查询项目下所有环境
**URL:** http://localhost}/autotest/environment/all/{projectId}

**Type:** GET


**Content-Type:** application/x-www-form-urlencoded;charset=UTF-8

**Description:** 功能：查询项目下所有环境

**Path-parameters:**

Parameter | Type|Required|Description|Since
---|---|---|---|---
projectId|string|true|// 项目ID|-

**Request-example:**
```
curl -X GET -i http://localhost:8080/autotest/environment/all/90
```
**Response-fields:**

Field | Type|Description|Since
---|---|---|---
id|string|No comments found.|-
name|string|No comments found.|-
projectId|string|No comments found.|-
description|string|No comments found.|-
createTime|int64|No comments found.|-
updateTime|int64|No comments found.|-
createUser|string|No comments found.|-
updateUser|string|No comments found.|-
status|int32|No comments found.|-

**Response-example:**
```
[
  {
    "id": "90",
    "name": "laronda.predovic",
    "projectId": "90",
    "description": "9pmdnk",
    "createTime": 1759765053864,
    "updateTime": 1759765053864,
    "createUser": "n640xs",
    "updateUser": "cotxg5",
    "status": 19
  }
]
```

### 功能：分页查询环境列表
**URL:** http://localhost}/autotest/environment/list/{goPage}/{pageSize}

**Type:** POST


**Content-Type:** application/json

**Description:** 功能：分页查询环境列表

**Path-parameters:**

Parameter | Type|Required|Description|Since
---|---|---|---|---
goPage|int32|true|   // 页码|-
pageSize|int32|true| // 每页大小|-

**Body-parameters:**

Parameter | Type|Required|Description|Since
---|---|---|---|---
condition|string|false||No comments found.|-
moduleId|string|false||No comments found.|-
createUser|string|false||No comments found.|-
projectId|string|false||No comments found.|-
caseType|string|false||No comments found.|-
collectionId|string|false||No comments found.|-
planId|string|false||No comments found.|-
operationType|string|false||No comments found.|-
roleId|string|false||No comments found.|-
requestUser|string|false||No comments found.|-
uiType|string|false||No comments found.|-
system|string|false||No comments found.|-
status|string|false||No comments found.|-
filter|object|false||No comments found.|-
└─map|map|false||No comments found.|-
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;└─any object|object|false||any object.|-

**Request-example:**
```
curl -X POST -H 'Content-Type: application/json' -i http://localhost:8080/autotest/environment/list/1/10 --data '{
  "condition": "u8ne78",
  "moduleId": "90",
  "createUser": "sw0x71",
  "projectId": "90",
  "caseType": "r8msj3",
  "collectionId": "90",
  "planId": "90",
  "operationType": "vohmm1",
  "roleId": "90",
  "requestUser": "4pu9nj",
  "uiType": "0ri83d",
  "system": "dnzmfz",
  "status": "xse904",
  "filter": {
    "map": {
      "mapKey": {}
    }
  }
}'
```
**Response-fields:**

Field | Type|Description|Since
---|---|---|---
list|array|No comments found.|-
└─id|string|No comments found.|-
└─name|string|No comments found.|-
└─projectId|string|No comments found.|-
└─description|string|No comments found.|-
└─createTime|int64|No comments found.|-
└─updateTime|int64|No comments found.|-
└─createUser|string|No comments found.|-
└─updateUser|string|No comments found.|-
└─status|int32|No comments found.|-
└─username|string|No comments found.|-
total|int64|No comments found.|-

**Response-example:**
```
{
  "list": [
    {
      "id": "90",
      "name": "laronda.predovic",
      "projectId": "90",
      "description": "1n7xv8",
      "createTime": 1759765053864,
      "updateTime": 1759765053864,
      "createUser": "i327qg",
      "updateUser": "16ylq0",
      "status": 758,
      "username": "laronda.predovic"
    }
  ],
  "total": 473
}
```

## 控制层：函数管理
范围：提供函数的保存、删除、详情与列表查询接口，保持注释增量更新与合理密度。
### 保存函数（新增或更新）
**URL:** http://localhost}/autotest/function/save

**Type:** POST


**Content-Type:** application/json

**Description:** 保存函数（新增或更新）

**Body-parameters:**

Parameter | Type|Required|Description|Since
---|---|---|---|---
id|string|false||No comments found.|-
name|string|false||No comments found.|-
from|string|false||No comments found.|-
param|string|false||No comments found.|-
code|string|false||No comments found.|-
expression|string|false||No comments found.|-
projectId|string|false||No comments found.|-
description|string|false||No comments found.|-
createTime|int64|false||No comments found.|-
updateTime|int64|false||No comments found.|-
createUser|string|false||No comments found.|-
updateUser|string|false||No comments found.|-
status|int32|false||No comments found.|-

**Request-example:**
```
curl -X POST -H 'Content-Type: application/json' -i http://localhost:8080/autotest/function/save --data '{
  "id": "90",
  "name": "laronda.predovic",
  "from": "hkvcfx",
  "param": "cmz19j",
  "code": "15463",
  "expression": "7mdg1d",
  "projectId": "90",
  "description": "a9gtyk",
  "createTime": 1759765053864,
  "updateTime": 1759765053864,
  "createUser": "j2u7kw",
  "updateUser": "e57etz",
  "status": 83
}'
```

**Response-example:**
```
Return void.
```

### 删除函数（逻辑删除）
**URL:** http://localhost}/autotest/function/delete

**Type:** POST


**Content-Type:** application/json

**Description:** 删除函数（逻辑删除）

**Body-parameters:**

Parameter | Type|Required|Description|Since
---|---|---|---|---
id|string|false||No comments found.|-
name|string|false||No comments found.|-
from|string|false||No comments found.|-
param|string|false||No comments found.|-
code|string|false||No comments found.|-
expression|string|false||No comments found.|-
projectId|string|false||No comments found.|-
description|string|false||No comments found.|-
createTime|int64|false||No comments found.|-
updateTime|int64|false||No comments found.|-
createUser|string|false||No comments found.|-
updateUser|string|false||No comments found.|-
status|int32|false||No comments found.|-

**Request-example:**
```
curl -X POST -H 'Content-Type: application/json' -i http://localhost:8080/autotest/function/delete --data '{
  "id": "90",
  "name": "laronda.predovic",
  "from": "5d6ez6",
  "param": "16hgrs",
  "code": "15463",
  "expression": "nxt5xa",
  "projectId": "90",
  "description": "38968t",
  "createTime": 1759765053864,
  "updateTime": 1759765053864,
  "createUser": "e73ly8",
  "updateUser": "osjyeg",
  "status": 285
}'
```

**Response-example:**
```
Return void.
```

### 获取函数详情（查看函数）
**URL:** http://localhost}/autotest/function/detail/{functionId}

**Type:** GET


**Content-Type:** application/x-www-form-urlencoded;charset=UTF-8

**Description:** 获取函数详情（查看函数）

**Path-parameters:**

Parameter | Type|Required|Description|Since
---|---|---|---|---
functionId|string|true|// 函数ID|-

**Request-example:**
```
curl -X GET -i http://localhost:8080/autotest/function/detail/90
```
**Response-fields:**

Field | Type|Description|Since
---|---|---|---
id|string|No comments found.|-
name|string|No comments found.|-
from|string|No comments found.|-
param|string|No comments found.|-
code|string|No comments found.|-
expression|string|No comments found.|-
projectId|string|No comments found.|-
description|string|No comments found.|-
createTime|int64|No comments found.|-
updateTime|int64|No comments found.|-
createUser|string|No comments found.|-
updateUser|string|No comments found.|-
status|int32|No comments found.|-

**Response-example:**
```
{
  "id": "90",
  "name": "laronda.predovic",
  "from": "c7kl6r",
  "param": "lx8fk7",
  "code": "15463",
  "expression": "wxb560",
  "projectId": "90",
  "description": "qjptro",
  "createTime": 1759765053864,
  "updateTime": 1759765053864,
  "createUser": "4tpjj3",
  "updateUser": "1bze7d",
  "status": 602
}
```

### 查询项目下自定义函数列表
**URL:** http://localhost}/autotest/function/custom/list/{projectId}

**Type:** GET


**Content-Type:** application/x-www-form-urlencoded;charset=UTF-8

**Description:** 查询项目下自定义函数列表

**Path-parameters:**

Parameter | Type|Required|Description|Since
---|---|---|---|---
projectId|string|true|        // 项目ID|-

**Request-example:**
```
curl -X GET -i http://localhost:8080/autotest/function/custom/list/90
```
**Response-fields:**

Field | Type|Description|Since
---|---|---|---
id|string|No comments found.|-
name|string|No comments found.|-
from|string|No comments found.|-
param|string|No comments found.|-
code|string|No comments found.|-
expression|string|No comments found.|-
projectId|string|No comments found.|-
description|string|No comments found.|-
createTime|int64|No comments found.|-
updateTime|int64|No comments found.|-
createUser|string|No comments found.|-
updateUser|string|No comments found.|-
status|int32|No comments found.|-

**Response-example:**
```
[
  {
    "id": "90",
    "name": "laronda.predovic",
    "from": "v3gjxw",
    "param": "ts60iq",
    "code": "15463",
    "expression": "4h6s0o",
    "projectId": "90",
    "description": "k8hgny",
    "createTime": 1759765053864,
    "updateTime": 1759765053864,
    "createUser": "fosp8g",
    "updateUser": "2j2gef",
    "status": 474
  }
]
```

### 分页查询函数列表（含创建人用户名）<br><br>关键点：<br>- 使用分页拦截器 PageHelper 统一分页<br>- 返回 Pager 携带分页信息与数据列表
**URL:** http://localhost}/autotest/function/list/{goPage}/{pageSize}

**Type:** POST


**Content-Type:** application/json

**Description:** 分页查询函数列表（含创建人用户名）

关键点：
- 使用分页拦截器 PageHelper 统一分页
- 返回 Pager 携带分页信息与数据列表

**Path-parameters:**

Parameter | Type|Required|Description|Since
---|---|---|---|---
goPage|int32|true|   // 页码|-
pageSize|int32|true| // 每页大小|-

**Body-parameters:**

Parameter | Type|Required|Description|Since
---|---|---|---|---
condition|string|false||No comments found.|-
moduleId|string|false||No comments found.|-
createUser|string|false||No comments found.|-
projectId|string|false||No comments found.|-
caseType|string|false||No comments found.|-
collectionId|string|false||No comments found.|-
planId|string|false||No comments found.|-
operationType|string|false||No comments found.|-
roleId|string|false||No comments found.|-
requestUser|string|false||No comments found.|-
uiType|string|false||No comments found.|-
system|string|false||No comments found.|-
status|string|false||No comments found.|-
filter|object|false||No comments found.|-
└─map|map|false||No comments found.|-
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;└─any object|object|false||any object.|-

**Request-example:**
```
curl -X POST -H 'Content-Type: application/json' -i http://localhost:8080/autotest/function/list/1/10 --data '{
  "condition": "44e22v",
  "moduleId": "90",
  "createUser": "8kkuqs",
  "projectId": "90",
  "caseType": "kybq3o",
  "collectionId": "90",
  "planId": "90",
  "operationType": "49hnk4",
  "roleId": "90",
  "requestUser": "fdn714",
  "uiType": "x77un9",
  "system": "bvdnq3",
  "status": "niplyw",
  "filter": {
    "map": {
      "mapKey": {}
    }
  }
}'
```
**Response-fields:**

Field | Type|Description|Since
---|---|---|---
list|array|No comments found.|-
└─id|string|No comments found.|-
└─name|string|No comments found.|-
└─from|string|No comments found.|-
└─param|string|No comments found.|-
└─code|string|No comments found.|-
└─expression|string|No comments found.|-
└─projectId|string|No comments found.|-
└─description|string|No comments found.|-
└─createTime|int64|No comments found.|-
└─updateTime|int64|No comments found.|-
└─createUser|string|No comments found.|-
└─updateUser|string|No comments found.|-
└─status|int32|No comments found.|-
└─username|string|No comments found.|-
total|int64|No comments found.|-

**Response-example:**
```
{
  "list": [
    {
      "id": "90",
      "name": "laronda.predovic",
      "from": "u2hekn",
      "param": "tejdba",
      "code": "15463",
      "expression": "af6p4r",
      "projectId": "90",
      "description": "i75z3l",
      "createTime": 1759765053864,
      "updateTime": 1759765053864,
      "createUser": "ygizro",
      "updateUser": "yamoz2",
      "status": 300,
      "username": "laronda.predovic"
    }
  ],
  "total": 215
}
```

## 控制器：登录认证入口
用途：校验账号密码，生成并返回平台token
### 功能：登录并签发平台token
**URL:** http://localhost}/autotest/login

**Type:** POST


**Content-Type:** application/json

**Description:** 功能：登录并签发平台token

**Body-parameters:**

Parameter | Type|Required|Description|Since
---|---|---|---|---
account|string|false||No comments found.|-
password|string|false||No comments found.|-

**Request-example:**
```
curl -X POST -H 'Content-Type: application/json' -i http://localhost:8080/autotest/login --data '{
  "account": "l4m04q",
  "password": "5jqjtw"
}'
```
**Response-fields:**

Field | Type|Description|Since
---|---|---|---
id|string|No comments found.|-
username|string|No comments found.|-
account|string|No comments found.|-
password|string|No comments found.|-
status|string|No comments found.|-
createTime|int64|No comments found.|-
updateTime|int64|No comments found.|-
mobile|int64|No comments found.|-
lastProject|string|No comments found.|-
email|string|No comments found.|-
permissions|array|No comments found.|-

**Response-example:**
```
{
  "id": "90",
  "username": "laronda.predovic",
  "account": "7txf7p",
  "password": "7efmte",
  "status": "rrzalp",
  "createTime": 1759765053864,
  "updateTime": 1759765053864,
  "mobile": 200,
  "lastProject": "ir6rkl",
  "email": "kerstin.spencer@yahoo.com",
  "permissions": [
    "iyv6g9"
  ]
}
```

## 控制器：模块入口
用途：保存、删除、树列表查询
### 保存模块
**URL:** http://localhost}/autotest/module/save

**Type:** POST


**Content-Type:** application/json

**Description:** 保存模块

**Body-parameters:**

Parameter | Type|Required|Description|Since
---|---|---|---|---
id|string|false||No comments found.|-
name|string|false||No comments found.|-
parentId|string|false||No comments found.|-
projectId|string|false||No comments found.|-
createTime|int64|false||No comments found.|-
updateTime|int64|false||No comments found.|-
createUser|string|false||No comments found.|-
updateUser|string|false||No comments found.|-
children|array|false||No comments found.|-
label|string|false||No comments found.|-
moduleType|string|false||No comments found.|-

**Request-example:**
```
curl -X POST -H 'Content-Type: application/json' -i http://localhost:8080/autotest/module/save --data '{
  "id": "90",
  "name": "laronda.predovic",
  "parentId": "90",
  "projectId": "90",
  "createTime": 1759765053864,
  "updateTime": 1759765053864,
  "createUser": "rujjjf",
  "updateUser": "mv2nex",
  "children": [
    {
      "$ref": ".."
    }
  ],
  "label": "yt155o",
  "moduleType": "7lz1q7"
}'
```
**Response-fields:**

Field | Type|Description|Since
---|---|---|---
id|string|No comments found.|-
name|string|No comments found.|-
parentId|string|No comments found.|-
projectId|string|No comments found.|-
createTime|int64|No comments found.|-
updateTime|int64|No comments found.|-
createUser|string|No comments found.|-
updateUser|string|No comments found.|-
children|array|No comments found.|-
label|string|No comments found.|-
moduleType|string|No comments found.|-

**Response-example:**
```
{
  "id": "90",
  "name": "laronda.predovic",
  "parentId": "90",
  "projectId": "90",
  "createTime": 1759765053864,
  "updateTime": 1759765053864,
  "createUser": "4paxmx",
  "updateUser": "xuo6fr",
  "children": [
    {
      "$ref": ".."
    }
  ],
  "label": "tfksge",
  "moduleType": "zk9fbl"
}
```

### 删除模块
**URL:** http://localhost}/autotest/module/delete

**Type:** POST


**Content-Type:** application/json

**Description:** 删除模块

**Body-parameters:**

Parameter | Type|Required|Description|Since
---|---|---|---|---
id|string|false||No comments found.|-
name|string|false||No comments found.|-
parentId|string|false||No comments found.|-
projectId|string|false||No comments found.|-
createTime|int64|false||No comments found.|-
updateTime|int64|false||No comments found.|-
createUser|string|false||No comments found.|-
updateUser|string|false||No comments found.|-
children|array|false||No comments found.|-
label|string|false||No comments found.|-
moduleType|string|false||No comments found.|-

**Request-example:**
```
curl -X POST -H 'Content-Type: application/json' -i http://localhost:8080/autotest/module/delete --data '{
  "id": "90",
  "name": "laronda.predovic",
  "parentId": "90",
  "projectId": "90",
  "createTime": 1759765053864,
  "updateTime": 1759765053864,
  "createUser": "vzjwdw",
  "updateUser": "wcwbh8",
  "children": [
    {
      "$ref": ".."
    }
  ],
  "label": "pxl80f",
  "moduleType": "zikxs8"
}'
```

**Response-example:**
```
Return void.
```

### 获取模块树列表
**URL:** http://localhost}/autotest/module/list/{moduleType}/{projectId}

**Type:** GET


**Content-Type:** application/x-www-form-urlencoded;charset=UTF-8

**Description:** 获取模块树列表

**Path-parameters:**

Parameter | Type|Required|Description|Since
---|---|---|---|---
moduleType|string|true|    // 模块类型|-
projectId|string|true|     // 项目ID|-

**Request-example:**
```
curl -X GET -i http://localhost:8080/autotest/module/list/tfmxh9/90
```
**Response-fields:**

Field | Type|Description|Since
---|---|---|---
id|string|No comments found.|-
name|string|No comments found.|-
parentId|string|No comments found.|-
projectId|string|No comments found.|-
createTime|int64|No comments found.|-
updateTime|int64|No comments found.|-
createUser|string|No comments found.|-
updateUser|string|No comments found.|-
children|array|No comments found.|-
label|string|No comments found.|-
moduleType|string|No comments found.|-

**Response-example:**
```
[
  {
    "id": "90",
    "name": "laronda.predovic",
    "parentId": "90",
    "projectId": "90",
    "createTime": 1759765053864,
    "updateTime": 1759765053864,
    "createUser": "ete0re",
    "updateUser": "hv8dpa",
    "children": [
      {
        "$ref": ".."
      }
    ],
    "label": "xs2lrz",
    "moduleType": "f9j5r4"
  }
]
```

## 控制器：通知配置入口
职责：保存、删除、项目通知查询与分页列表
### 功能：保存通知配置
**URL:** http://localhost}/autotest/notification/save

**Type:** POST


**Content-Type:** application/json

**Description:** 功能：保存通知配置

**Body-parameters:**

Parameter | Type|Required|Description|Since
---|---|---|---|---
id|string|false||No comments found.|-
name|string|false||No comments found.|-
type|string|false||No comments found.|-
params|string|false||No comments found.|-
webhookUrl|string|false||No comments found.|-
projectId|string|false||No comments found.|-
createTime|int64|false||No comments found.|-
updateTime|int64|false||No comments found.|-
status|string|false||No comments found.|-

**Request-example:**
```
curl -X POST -H 'Content-Type: application/json' -i http://localhost:8080/autotest/notification/save --data '{
  "id": "90",
  "name": "laronda.predovic",
  "type": "s9bu6k",
  "params": "6crggp",
  "webhookUrl": "www.enid-hackett.biz",
  "projectId": "90",
  "createTime": 1759765053864,
  "updateTime": 1759765053864,
  "status": "rkz40e"
}'
```

**Response-example:**
```
Return void.
```

### 功能：删除通知配置
**URL:** http://localhost}/autotest/notification/delete

**Type:** POST


**Content-Type:** application/json

**Description:** 功能：删除通知配置

**Body-parameters:**

Parameter | Type|Required|Description|Since
---|---|---|---|---
id|string|false||No comments found.|-
name|string|false||No comments found.|-
type|string|false||No comments found.|-
params|string|false||No comments found.|-
webhookUrl|string|false||No comments found.|-
projectId|string|false||No comments found.|-
createTime|int64|false||No comments found.|-
updateTime|int64|false||No comments found.|-
status|string|false||No comments found.|-

**Request-example:**
```
curl -X POST -H 'Content-Type: application/json' -i http://localhost:8080/autotest/notification/delete --data '{
  "id": "90",
  "name": "laronda.predovic",
  "type": "w5oa9m",
  "params": "goa9w3",
  "webhookUrl": "www.enid-hackett.biz",
  "projectId": "90",
  "createTime": 1759765053864,
  "updateTime": 1759765053864,
  "status": "j8trfs"
}'
```

**Response-example:**
```
Return void.
```

### 功能：查询项目下所有通知配置
**URL:** http://localhost}/autotest/notification/list/{projectId}

**Type:** GET


**Content-Type:** application/x-www-form-urlencoded;charset=UTF-8

**Description:** 功能：查询项目下所有通知配置

**Path-parameters:**

Parameter | Type|Required|Description|Since
---|---|---|---|---
projectId|string|true|// 项目ID|-

**Request-example:**
```
curl -X GET -i http://localhost:8080/autotest/notification/list/90
```
**Response-fields:**

Field | Type|Description|Since
---|---|---|---
id|string|No comments found.|-
name|string|No comments found.|-
type|string|No comments found.|-
params|string|No comments found.|-
webhookUrl|string|No comments found.|-
projectId|string|No comments found.|-
createTime|int64|No comments found.|-
updateTime|int64|No comments found.|-
status|string|No comments found.|-

**Response-example:**
```
[
  {
    "id": "90",
    "name": "laronda.predovic",
    "type": "a00y39",
    "params": "zmms5e",
    "webhookUrl": "www.enid-hackett.biz",
    "projectId": "90",
    "createTime": 1759765053864,
    "updateTime": 1759765053864,
    "status": "xunqf8"
  }
]
```

### 功能：分页查询通知列表
**URL:** http://localhost}/autotest/notification/list/{goPage}/{pageSize}

**Type:** POST


**Content-Type:** application/json

**Description:** 功能：分页查询通知列表

**Path-parameters:**

Parameter | Type|Required|Description|Since
---|---|---|---|---
goPage|int32|true|   // 页码|-
pageSize|int32|true| // 每页大小|-

**Body-parameters:**

Parameter | Type|Required|Description|Since
---|---|---|---|---
condition|string|false||No comments found.|-
moduleId|string|false||No comments found.|-
createUser|string|false||No comments found.|-
projectId|string|false||No comments found.|-
caseType|string|false||No comments found.|-
collectionId|string|false||No comments found.|-
planId|string|false||No comments found.|-
operationType|string|false||No comments found.|-
roleId|string|false||No comments found.|-
requestUser|string|false||No comments found.|-
uiType|string|false||No comments found.|-
system|string|false||No comments found.|-
status|string|false||No comments found.|-
filter|object|false||No comments found.|-
└─map|map|false||No comments found.|-
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;└─any object|object|false||any object.|-

**Request-example:**
```
curl -X POST -H 'Content-Type: application/json' -i http://localhost:8080/autotest/notification/list/1/10 --data '{
  "condition": "cef2tf",
  "moduleId": "90",
  "createUser": "gxhpue",
  "projectId": "90",
  "caseType": "r2xnhu",
  "collectionId": "90",
  "planId": "90",
  "operationType": "1wkj4g",
  "roleId": "90",
  "requestUser": "ch862t",
  "uiType": "vufi94",
  "system": "i9x4by",
  "status": "d1xoz4",
  "filter": {
    "map": {
      "mapKey": {}
    }
  }
}'
```
**Response-fields:**

Field | Type|Description|Since
---|---|---|---
list|array|No comments found.|-
└─id|string|No comments found.|-
└─name|string|No comments found.|-
└─type|string|No comments found.|-
└─params|string|No comments found.|-
└─webhookUrl|string|No comments found.|-
└─projectId|string|No comments found.|-
└─createTime|int64|No comments found.|-
└─updateTime|int64|No comments found.|-
└─status|string|No comments found.|-
total|int64|No comments found.|-

**Response-example:**
```
{
  "list": [
    {
      "id": "90",
      "name": "laronda.predovic",
      "type": "96xk09",
      "params": "qq2ay3",
      "webhookUrl": "www.enid-hackett.biz",
      "projectId": "90",
      "createTime": 1759765053864,
      "updateTime": 1759765053864,
      "status": "50lzy3"
    }
  ],
  "total": 513
}
```

## 控制器：开放接口（引擎对接与外部触发）
职责：提供引擎令牌、心跳、任务拉取与回传、附件下载、截图预览、外部触发计划执行等入口。
### 申请引擎访问令牌
**URL:** http://localhost}/openapi/engine/token/apply

**Type:** POST


**Content-Type:** application/json

**Description:** 申请引擎访问令牌

**Body-parameters:**

Parameter | Type|Required|Description|Since
---|---|---|---|---
engineCode|string|false||No comments found.|-
engineSecret|string|false||No comments found.|-
timestamp|string|false||No comments found.|-
taskId|string|false||No comments found.|-
fileName|string|false||No comments found.|-
base64String|string|false||No comments found.|-
caseResultList|array|false||No comments found.|-
└─status|int32|false||No comments found.|-
└─startTime|int64|false||No comments found.|-
└─endTime|int64|false||No comments found.|-
└─collectionId|string|false||No comments found.|-
└─caseId|string|false||No comments found.|-
└─caseType|string|false||No comments found.|-
└─caseName|string|false||No comments found.|-
└─caseDesc|string|false||No comments found.|-
└─index|int32|false||No comments found.|-
└─runTimes|int32|false||No comments found.|-
└─transactionList|array|false||No comments found.|-
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;└─id|string|false||No comments found.|-
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;└─name|string|false||No comments found.|-
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;└─content|string|false||No comments found.|-
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;└─description|string|false||No comments found.|-
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;└─log|string|false||No comments found.|-
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;└─during|int32|false||No comments found.|-
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;└─status|int32|false||No comments found.|-
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;└─screenShotList|array|false||No comments found.|-

**Request-example:**
```
curl -X POST -H 'Content-Type: application/json' -i http://localhost:8080/openapi/engine/token/apply --data '{
  "engineCode": "15463",
  "engineSecret": "y0iqqx",
  "timestamp": "2025-10-06 23:37:33",
  "taskId": "90",
  "fileName": "laronda.predovic",
  "base64String": "dsqz4y",
  "caseResultList": [
    {
      "status": 721,
      "startTime": 1759765053864,
      "endTime": 1759765053864,
      "collectionId": "90",
      "caseId": "90",
      "caseType": "wcjrvd",
      "caseName": "laronda.predovic",
      "caseDesc": "qrpabf",
      "index": 1,
      "runTimes": 483,
      "transactionList": [
        {
          "id": "90",
          "name": "laronda.predovic",
          "content": "xhz82p",
          "description": "z705fe",
          "log": "kv11b9",
          "during": 395,
          "status": 84,
          "screenShotList": [
            "u1n6t5"
          ]
        }
      ]
    }
  ]
}'
```

**Response-example:**
```
string
```

### 引擎心跳上报
**URL:** http://localhost}/openapi/engine/heartbeat/send

**Type:** POST


**Content-Type:** application/json

**Description:** 引擎心跳上报

**Body-parameters:**

Parameter | Type|Required|Description|Since
---|---|---|---|---
engineCode|string|false||No comments found.|-
engineSecret|string|false||No comments found.|-
timestamp|string|false||No comments found.|-
taskId|string|false||No comments found.|-
fileName|string|false||No comments found.|-
base64String|string|false||No comments found.|-
caseResultList|array|false||No comments found.|-
└─status|int32|false||No comments found.|-
└─startTime|int64|false||No comments found.|-
└─endTime|int64|false||No comments found.|-
└─collectionId|string|false||No comments found.|-
└─caseId|string|false||No comments found.|-
└─caseType|string|false||No comments found.|-
└─caseName|string|false||No comments found.|-
└─caseDesc|string|false||No comments found.|-
└─index|int32|false||No comments found.|-
└─runTimes|int32|false||No comments found.|-
└─transactionList|array|false||No comments found.|-
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;└─id|string|false||No comments found.|-
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;└─name|string|false||No comments found.|-
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;└─content|string|false||No comments found.|-
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;└─description|string|false||No comments found.|-
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;└─log|string|false||No comments found.|-
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;└─during|int32|false||No comments found.|-
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;└─status|int32|false||No comments found.|-
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;└─screenShotList|array|false||No comments found.|-

**Request-example:**
```
curl -X POST -H 'Content-Type: application/json' -i http://localhost:8080/openapi/engine/heartbeat/send --data '{
  "engineCode": "15463",
  "engineSecret": "rz6u5g",
  "timestamp": "2025-10-06 23:37:33",
  "taskId": "90",
  "fileName": "laronda.predovic",
  "base64String": "qaz8g9",
  "caseResultList": [
    {
      "status": 629,
      "startTime": 1759765053864,
      "endTime": 1759765053864,
      "collectionId": "90",
      "caseId": "90",
      "caseType": "332czg",
      "caseName": "laronda.predovic",
      "caseDesc": "dnxqjd",
      "index": 1,
      "runTimes": 536,
      "transactionList": [
        {
          "id": "90",
          "name": "laronda.predovic",
          "content": "g6zfu8",
          "description": "oj9ib9",
          "log": "sohgo2",
          "during": 327,
          "status": 914,
          "screenShotList": [
            "yrf4ov"
          ]
        }
      ]
    }
  ]
}'
```

**Response-example:**
```
string
```

### 引擎拉取待执行任务
**URL:** http://localhost}/openapi/engine/task/fetch

**Type:** POST


**Content-Type:** application/json

**Description:** 引擎拉取待执行任务

**Body-parameters:**

Parameter | Type|Required|Description|Since
---|---|---|---|---
engineCode|string|false||No comments found.|-
engineSecret|string|false||No comments found.|-
timestamp|string|false||No comments found.|-
taskId|string|false||No comments found.|-
fileName|string|false||No comments found.|-
base64String|string|false||No comments found.|-
caseResultList|array|false||No comments found.|-
└─status|int32|false||No comments found.|-
└─startTime|int64|false||No comments found.|-
└─endTime|int64|false||No comments found.|-
└─collectionId|string|false||No comments found.|-
└─caseId|string|false||No comments found.|-
└─caseType|string|false||No comments found.|-
└─caseName|string|false||No comments found.|-
└─caseDesc|string|false||No comments found.|-
└─index|int32|false||No comments found.|-
└─runTimes|int32|false||No comments found.|-
└─transactionList|array|false||No comments found.|-
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;└─id|string|false||No comments found.|-
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;└─name|string|false||No comments found.|-
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;└─content|string|false||No comments found.|-
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;└─description|string|false||No comments found.|-
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;└─log|string|false||No comments found.|-
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;└─during|int32|false||No comments found.|-
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;└─status|int32|false||No comments found.|-
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;└─screenShotList|array|false||No comments found.|-

**Request-example:**
```
curl -X POST -H 'Content-Type: application/json' -i http://localhost:8080/openapi/engine/task/fetch --data '{
  "engineCode": "15463",
  "engineSecret": "7vgz2b",
  "timestamp": "2025-10-06 23:37:33",
  "taskId": "90",
  "fileName": "laronda.predovic",
  "base64String": "wrhq2g",
  "caseResultList": [
    {
      "status": 913,
      "startTime": 1759765053864,
      "endTime": 1759765053864,
      "collectionId": "90",
      "caseId": "90",
      "caseType": "9k1fq5",
      "caseName": "laronda.predovic",
      "caseDesc": "5yblxp",
      "index": 1,
      "runTimes": 624,
      "transactionList": [
        {
          "id": "90",
          "name": "laronda.predovic",
          "content": "e33vto",
          "description": "b0l36u",
          "log": "ds0qlx",
          "during": 92,
          "status": 633,
          "screenShotList": [
            "l0zcyv"
          ]
        }
      ]
    }
  ]
}'
```
**Response-fields:**

Field | Type|Description|Since
---|---|---|---
taskId|string|No comments found.|-
taskType|string|No comments found.|-
downloadUrl|string|No comments found.|-
maxThread|int32|No comments found.|-
reRun|boolean|No comments found.|-
testCollectionList|array|No comments found.|-
└─collectionId|string|No comments found.|-
└─deviceId|string|No comments found.|-
└─testCaseList|array|No comments found.|-
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;└─index|int64|No comments found.|-
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;└─caseId|string|No comments found.|-
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;└─caseType|string|No comments found.|-
debugData|object|No comments found.|-
└─map|map|No comments found.|-
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;└─any object|object|any object.|-

**Response-example:**
```
{
  "taskId": "90",
  "taskType": "bzmaqf",
  "downloadUrl": "www.enid-hackett.biz",
  "maxThread": 776,
  "reRun": true,
  "testCollectionList": [
    {
      "collectionId": "90",
      "deviceId": "90",
      "testCaseList": [
        {
          "index": 524,
          "caseId": "90",
          "caseType": "av70ln"
        }
      ]
    }
  ],
  "debugData": {
    "map": {
      "mapKey": {}
    }
  }
}
```

### 查询任务状态
**URL:** http://localhost}/openapi/engine/task/status

**Type:** POST


**Content-Type:** application/json

**Description:** 查询任务状态

**Body-parameters:**

Parameter | Type|Required|Description|Since
---|---|---|---|---
engineCode|string|false||No comments found.|-
engineSecret|string|false||No comments found.|-
timestamp|string|false||No comments found.|-
taskId|string|false||No comments found.|-
fileName|string|false||No comments found.|-
base64String|string|false||No comments found.|-
caseResultList|array|false||No comments found.|-
└─status|int32|false||No comments found.|-
└─startTime|int64|false||No comments found.|-
└─endTime|int64|false||No comments found.|-
└─collectionId|string|false||No comments found.|-
└─caseId|string|false||No comments found.|-
└─caseType|string|false||No comments found.|-
└─caseName|string|false||No comments found.|-
└─caseDesc|string|false||No comments found.|-
└─index|int32|false||No comments found.|-
└─runTimes|int32|false||No comments found.|-
└─transactionList|array|false||No comments found.|-
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;└─id|string|false||No comments found.|-
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;└─name|string|false||No comments found.|-
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;└─content|string|false||No comments found.|-
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;└─description|string|false||No comments found.|-
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;└─log|string|false||No comments found.|-
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;└─during|int32|false||No comments found.|-
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;└─status|int32|false||No comments found.|-
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;└─screenShotList|array|false||No comments found.|-

**Request-example:**
```
curl -X POST -H 'Content-Type: application/json' -i http://localhost:8080/openapi/engine/task/status --data '{
  "engineCode": "15463",
  "engineSecret": "mgvdq8",
  "timestamp": "2025-10-06 23:37:33",
  "taskId": "90",
  "fileName": "laronda.predovic",
  "base64String": "n46l7u",
  "caseResultList": [
    {
      "status": 338,
      "startTime": 1759765053864,
      "endTime": 1759765053864,
      "collectionId": "90",
      "caseId": "90",
      "caseType": "upotyt",
      "caseName": "laronda.predovic",
      "caseDesc": "2u66eb",
      "index": 1,
      "runTimes": 561,
      "transactionList": [
        {
          "id": "90",
          "name": "laronda.predovic",
          "content": "kqqfuo",
          "description": "3cuzfk",
          "log": "lyrdbt",
          "during": 439,
          "status": 203,
          "screenShotList": [
            "40j2xw"
          ]
        }
      ]
    }
  ]
}'
```

**Response-example:**
```
string
```

### 上传用例执行结果
**URL:** http://localhost}/openapi/engine/result/upload

**Type:** POST


**Content-Type:** application/json

**Description:** 上传用例执行结果

**Body-parameters:**

Parameter | Type|Required|Description|Since
---|---|---|---|---
engineCode|string|false||No comments found.|-
engineSecret|string|false||No comments found.|-
timestamp|string|false||No comments found.|-
taskId|string|false||No comments found.|-
fileName|string|false||No comments found.|-
base64String|string|false||No comments found.|-
caseResultList|array|false||No comments found.|-
└─status|int32|false||No comments found.|-
└─startTime|int64|false||No comments found.|-
└─endTime|int64|false||No comments found.|-
└─collectionId|string|false||No comments found.|-
└─caseId|string|false||No comments found.|-
└─caseType|string|false||No comments found.|-
└─caseName|string|false||No comments found.|-
└─caseDesc|string|false||No comments found.|-
└─index|int32|false||No comments found.|-
└─runTimes|int32|false||No comments found.|-
└─transactionList|array|false||No comments found.|-
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;└─id|string|false||No comments found.|-
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;└─name|string|false||No comments found.|-
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;└─content|string|false||No comments found.|-
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;└─description|string|false||No comments found.|-
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;└─log|string|false||No comments found.|-
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;└─during|int32|false||No comments found.|-
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;└─status|int32|false||No comments found.|-
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;└─screenShotList|array|false||No comments found.|-

**Request-example:**
```
curl -X POST -H 'Content-Type: application/json' -i http://localhost:8080/openapi/engine/result/upload --data '{
  "engineCode": "15463",
  "engineSecret": "rla285",
  "timestamp": "2025-10-06 23:37:33",
  "taskId": "90",
  "fileName": "laronda.predovic",
  "base64String": "eqfhg5",
  "caseResultList": [
    {
      "status": 580,
      "startTime": 1759765053864,
      "endTime": 1759765053864,
      "collectionId": "90",
      "caseId": "90",
      "caseType": "hcy24z",
      "caseName": "laronda.predovic",
      "caseDesc": "257nut",
      "index": 1,
      "runTimes": 729,
      "transactionList": [
        {
          "id": "90",
          "name": "laronda.predovic",
          "content": "7n6bz8",
          "description": "9p6w4s",
          "log": "q3avhj",
          "during": 6,
          "status": 653,
          "screenShotList": [
            "yvl6as"
          ]
        }
      ]
    }
  ]
}'
```

**Response-example:**
```
Return void.
```

### 完成任务回调（更新状态并通知）
**URL:** http://localhost}/openapi/engine/task/complete

**Type:** POST


**Content-Type:** application/json

**Description:** 完成任务回调（更新状态并通知）

**Body-parameters:**

Parameter | Type|Required|Description|Since
---|---|---|---|---
engineCode|string|false||No comments found.|-
engineSecret|string|false||No comments found.|-
timestamp|string|false||No comments found.|-
taskId|string|false||No comments found.|-
fileName|string|false||No comments found.|-
base64String|string|false||No comments found.|-
caseResultList|array|false||No comments found.|-
└─status|int32|false||No comments found.|-
└─startTime|int64|false||No comments found.|-
└─endTime|int64|false||No comments found.|-
└─collectionId|string|false||No comments found.|-
└─caseId|string|false||No comments found.|-
└─caseType|string|false||No comments found.|-
└─caseName|string|false||No comments found.|-
└─caseDesc|string|false||No comments found.|-
└─index|int32|false||No comments found.|-
└─runTimes|int32|false||No comments found.|-
└─transactionList|array|false||No comments found.|-
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;└─id|string|false||No comments found.|-
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;└─name|string|false||No comments found.|-
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;└─content|string|false||No comments found.|-
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;└─description|string|false||No comments found.|-
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;└─log|string|false||No comments found.|-
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;└─during|int32|false||No comments found.|-
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;└─status|int32|false||No comments found.|-
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;└─screenShotList|array|false||No comments found.|-

**Request-example:**
```
curl -X POST -H 'Content-Type: application/json' -i http://localhost:8080/openapi/engine/task/complete --data '{
  "engineCode": "15463",
  "engineSecret": "2cdhu0",
  "timestamp": "2025-10-06 23:37:33",
  "taskId": "90",
  "fileName": "laronda.predovic",
  "base64String": "6xooq7",
  "caseResultList": [
    {
      "status": 631,
      "startTime": 1759765053864,
      "endTime": 1759765053864,
      "collectionId": "90",
      "caseId": "90",
      "caseType": "ba021a",
      "caseName": "laronda.predovic",
      "caseDesc": "x37bhi",
      "index": 1,
      "runTimes": 587,
      "transactionList": [
        {
          "id": "90",
          "name": "laronda.predovic",
          "content": "819n8p",
          "description": "xk3oip",
          "log": "r6cq3q",
          "during": 986,
          "status": 500,
          "screenShotList": [
            "d65v6p"
          ]
        }
      ]
    }
  ]
}'
```

**Response-example:**
```
Return void.
```

### 上传截图
**URL:** http://localhost}/openapi/engine/screenshot/upload

**Type:** POST


**Content-Type:** application/json

**Description:** 上传截图

**Body-parameters:**

Parameter | Type|Required|Description|Since
---|---|---|---|---
engineCode|string|false||No comments found.|-
engineSecret|string|false||No comments found.|-
timestamp|string|false||No comments found.|-
taskId|string|false||No comments found.|-
fileName|string|false||No comments found.|-
base64String|string|false||No comments found.|-
caseResultList|array|false||No comments found.|-
└─status|int32|false||No comments found.|-
└─startTime|int64|false||No comments found.|-
└─endTime|int64|false||No comments found.|-
└─collectionId|string|false||No comments found.|-
└─caseId|string|false||No comments found.|-
└─caseType|string|false||No comments found.|-
└─caseName|string|false||No comments found.|-
└─caseDesc|string|false||No comments found.|-
└─index|int32|false||No comments found.|-
└─runTimes|int32|false||No comments found.|-
└─transactionList|array|false||No comments found.|-
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;└─id|string|false||No comments found.|-
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;└─name|string|false||No comments found.|-
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;└─content|string|false||No comments found.|-
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;└─description|string|false||No comments found.|-
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;└─log|string|false||No comments found.|-
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;└─during|int32|false||No comments found.|-
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;└─status|int32|false||No comments found.|-
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;└─screenShotList|array|false||No comments found.|-

**Request-example:**
```
curl -X POST -H 'Content-Type: application/json' -i http://localhost:8080/openapi/engine/screenshot/upload --data '{
  "engineCode": "15463",
  "engineSecret": "9wl22w",
  "timestamp": "2025-10-06 23:37:33",
  "taskId": "90",
  "fileName": "laronda.predovic",
  "base64String": "4lv8ht",
  "caseResultList": [
    {
      "status": 59,
      "startTime": 1759765053864,
      "endTime": 1759765053864,
      "collectionId": "90",
      "caseId": "90",
      "caseType": "4p1tgr",
      "caseName": "laronda.predovic",
      "caseDesc": "kct4fs",
      "index": 1,
      "runTimes": 47,
      "transactionList": [
        {
          "id": "90",
          "name": "laronda.predovic",
          "content": "qmg161",
          "description": "txkw6w",
          "log": "c6opkb",
          "during": 653,
          "status": 524,
          "screenShotList": [
            "mwknw4"
          ]
        }
      ]
    }
  ]
}'
```

**Response-example:**
```
Return void.
```

### 下载任务打包文件
**URL:** http://localhost}/openapi/task/file/download/{taskId}

**Type:** GET


**Content-Type:** application/x-www-form-urlencoded;charset=UTF-8

**Description:** 下载任务打包文件

**Path-parameters:**

Parameter | Type|Required|Description|Since
---|---|---|---|---
taskId|string|true|  任务ID|-

**Request-example:**
```
curl -X GET -i http://localhost:8080/openapi/task/file/download/90
```

**Response-example:**
```
Return void.
```

### 下载测试文件
**URL:** http://localhost}/openapi/download/test/file/{fileId}

**Type:** GET


**Content-Type:** application/x-www-form-urlencoded;charset=UTF-8

**Description:** 下载测试文件

**Path-parameters:**

Parameter | Type|Required|Description|Since
---|---|---|---|---
fileId|string|true|  文件ID|-

**Request-example:**
```
curl -X GET -i http://localhost:8080/openapi/download/test/file/90
```

**Response-example:**
```
Return void.
```

### 下载应用安装包
**URL:** http://localhost}/openapi/download/package/{date}/{fileId}/{packageName}

**Type:** GET


**Content-Type:** application/x-www-form-urlencoded;charset=UTF-8

**Description:** 下载应用安装包

**Path-parameters:**

Parameter | Type|Required|Description|Since
---|---|---|---|---
date|string|true|       日期目录|-
fileId|string|true|     文件ID|-
packageName|string|true|包名|-

**Request-example:**
```
curl -X GET -i http://localhost:8080/openapi/download/package/2025-10-06/90/laronda.predovic
```

**Response-example:**
```
Return void.
```

### 预览截图
**URL:** http://localhost}/openapi/screenshot/{date}/{imageId}

**Type:** GET


**Content-Type:** application/x-www-form-urlencoded;charset=UTF-8

**Description:** 预览截图

**Path-parameters:**

Parameter | Type|Required|Description|Since
---|---|---|---|---
date|string|true|   日期目录|-
imageId|string|true|图片ID|-

**Request-example:**
```
curl -X GET -i http://localhost:8080/openapi/screenshot/2025-10-06/90
```
**Response-fields:**

Field | Type|Description|Since
---|---|---|---
-|int8|Return int8.|-

**Response-example:**
```
[
  "121",
  "125"
]
```

### 外部触发执行测试计划
**URL:** http://localhost}/openapi/exec/test/plan

**Type:** POST


**Content-Type:** application/json

**Description:** 外部触发执行测试计划

**Body-parameters:**

Parameter | Type|Required|Description|Since
---|---|---|---|---
engineId|string|false||No comments found.|-
environmentId|string|false||No comments found.|-
deviceId|string|false||No comments found.|-
sourceType|string|false||No comments found.|-
sourceId|string|false||No comments found.|-
sourceName|string|false||No comments found.|-
taskType|string|false||No comments found.|-
runUser|string|false||No comments found.|-
projectId|string|false||No comments found.|-
debugData|object|false||No comments found.|-
└─id|string|false||No comments found.|-
└─num|int64|false||No comments found.|-
└─name|string|false||No comments found.|-
└─level|string|false||No comments found.|-
└─moduleId|string|false||No comments found.|-
└─moduleName|string|false||No comments found.|-
└─projectId|string|false||No comments found.|-
└─type|string|false||No comments found.|-
└─thirdParty|string|false||No comments found.|-
└─description|string|false||No comments found.|-
└─environmentIds|object|false||No comments found.|-
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;└─list|array|false||No comments found.|-
└─system|string|false||No comments found.|-
└─commonParam|object|false||No comments found.|-
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;└─map|map|false||No comments found.|-
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;└─any object|object|false||any object.|-
└─createTime|int64|false||No comments found.|-
└─updateTime|int64|false||No comments found.|-
└─createUser|string|false||No comments found.|-
└─updateUser|string|false||No comments found.|-
└─status|string|false||No comments found.|-
└─caseApis|array|false||No comments found.|-
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;└─id|string|false||No comments found.|-
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;└─index|int64|false||No comments found.|-
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;└─caseId|string|false||No comments found.|-
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;└─apiId|string|false||No comments found.|-
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;└─description|string|false||No comments found.|-
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;└─header|object|false||No comments found.|-
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;└─list|array|false||No comments found.|-
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;└─body|object|false||No comments found.|-
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;└─map|map|false||No comments found.|-
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;└─any object|object|false||any object.|-
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;└─query|object|false||No comments found.|-
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;└─list|array|false||No comments found.|-
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;└─rest|object|false||No comments found.|-
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;└─list|array|false||No comments found.|-
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;└─assertion|object|false||No comments found.|-
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;└─list|array|false||No comments found.|-
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;└─relation|object|false||No comments found.|-
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;└─list|array|false||No comments found.|-
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;└─controller|object|false||No comments found.|-
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;└─list|array|false||No comments found.|-
└─caseWebs|array|false||No comments found.|-
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;└─id|string|false||No comments found.|-
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;└─index|int64|false||No comments found.|-
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;└─caseId|string|false||No comments found.|-
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;└─operationId|string|false||No comments found.|-
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;└─description|string|false||No comments found.|-
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;└─element|object|false||No comments found.|-
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;└─list|array|false||No comments found.|-
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;└─data|object|false||No comments found.|-
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;└─list|array|false||No comments found.|-
└─caseApps|array|false||No comments found.|-
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;└─id|string|false||No comments found.|-
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;└─index|int64|false||No comments found.|-
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;└─caseId|string|false||No comments found.|-
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;└─operationId|string|false||No comments found.|-
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;└─description|string|false||No comments found.|-
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;└─element|object|false||No comments found.|-
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;└─list|array|false||No comments found.|-
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;└─data|object|false||No comments found.|-
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;└─list|array|false||No comments found.|-
user|string|false||No comments found.|-
planId|string|false||No comments found.|-

**Request-example:**
```
curl -X POST -H 'Content-Type: application/json' -i http://localhost:8080/openapi/exec/test/plan --data '{
  "engineId": "90",
  "environmentId": "90",
  "deviceId": "90",
  "sourceType": "hy05r2",
  "sourceId": "90",
  "sourceName": "laronda.predovic",
  "taskType": "gcsm56",
  "runUser": "a7fpic",
  "projectId": "90",
  "debugData": {
    "id": "90",
    "num": 950,
    "name": "laronda.predovic",
    "level": "2muasa",
    "moduleId": "90",
    "moduleName": "laronda.predovic",
    "projectId": "90",
    "type": "0n9lnq",
    "thirdParty": "rjh6br",
    "description": "lxews3",
    "environmentIds": {
      "list": [
        {
          "object": "any object"
        }
      ]
    },
    "system": "m40ha8",
    "commonParam": {
      "map": {
        "mapKey": {}
      }
    },
    "createTime": 1759765053864,
    "updateTime": 1759765053864,
    "createUser": "lxeyos",
    "updateUser": "cx0z71",
    "status": "g72708",
    "caseApis": [
      {
        "id": "90",
        "index": 753,
        "caseId": "90",
        "apiId": "90",
        "description": "gkdea3",
        "header": {
          "list": [
            {
              "object": "any object"
            }
          ]
        },
        "body": {
          "map": {
            "mapKey": {}
          }
        },
        "query": {
          "list": [
            {
              "object": "any object"
            }
          ]
        },
        "rest": {
          "list": [
            {
              "object": "any object"
            }
          ]
        },
        "assertion": {
          "list": [
            {
              "object": "any object"
            }
          ]
        },
        "relation": {
          "list": [
            {
              "object": "any object"
            }
          ]
        },
        "controller": {
          "list": [
            {
              "object": "any object"
            }
          ]
        }
      }
    ],
    "caseWebs": [
      {
        "id": "90",
        "index": 104,
        "caseId": "90",
        "operationId": "90",
        "description": "c3u6pj",
        "element": {
          "list": [
            {
              "object": "any object"
            }
          ]
        },
        "data": {
          "list": [
            {
              "object": "any object"
            }
          ]
        }
      }
    ],
    "caseApps": [
      {
        "id": "90",
        "index": 278,
        "caseId": "90",
        "operationId": "90",
        "description": "pikpu5",
        "element": {
          "list": [
            {
              "object": "any object"
            }
          ]
        },
        "data": {
          "list": [
            {
              "object": "any object"
            }
          ]
        }
      }
    ]
  },
  "user": "9jzawd",
  "planId": "90"
}'
```

**Response-example:**
```
string
```

### 获取计划执行报告
**URL:** http://localhost}/openapi/exec/result/{taskId}

**Type:** POST


**Content-Type:** application/x-www-form-urlencoded;charset=UTF-8

**Description:** 获取计划执行报告

**Path-parameters:**

Parameter | Type|Required|Description|Since
---|---|---|---|---
taskId|string|true|任务ID|-

**Request-example:**
```
curl -X POST -i http://localhost:8080/openapi/exec/result/90
```
**Response-fields:**

Field | Type|Description|Since
---|---|---|---
id|string|No comments found.|-
name|string|No comments found.|-
taskId|string|No comments found.|-
environmentId|string|No comments found.|-
deviceId|string|No comments found.|-
sourceType|string|No comments found.|-
sourceId|string|No comments found.|-
startTime|int64|No comments found.|-
endTime|int64|No comments found.|-
status|string|No comments found.|-
projectId|string|No comments found.|-
createTime|int64|No comments found.|-
updateTime|int64|No comments found.|-
createUser|string|No comments found.|-
updateUser|string|No comments found.|-
username|string|No comments found.|-
total|int64|No comments found.|-
passCount|int64|No comments found.|-
failCount|int64|No comments found.|-
errorCount|int64|No comments found.|-
passRate|string|No comments found.|-
progress|int32|No comments found.|-
collectionList|array|No comments found.|-
└─id|string|No comments found.|-
└─reportId|string|No comments found.|-
└─collectionId|string|No comments found.|-
└─collectionName|string|No comments found.|-
└─collectionVersion|string|No comments found.|-
└─caseTotal|int32|No comments found.|-
└─passCount|int32|No comments found.|-
└─failCount|int32|No comments found.|-
└─errorCount|int32|No comments found.|-
└─caseList|array|No comments found.|-
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;└─id|string|No comments found.|-
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;└─reportCollectionId|string|No comments found.|-
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;└─collectionCaseIndex|int32|No comments found.|-
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;└─caseId|string|No comments found.|-
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;└─caseType|string|No comments found.|-
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;└─caseName|string|No comments found.|-
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;└─caseDesc|string|No comments found.|-
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;└─runTimes|int32|No comments found.|-
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;└─startTime|int64|No comments found.|-
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;└─endTime|int64|No comments found.|-
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;└─during|string|No comments found.|-
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;└─status|string|No comments found.|-
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;└─transList|array|No comments found.|-
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;└─status|string|No comments found.|-
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;└─transId|string|No comments found.|-
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;└─transName|string|No comments found.|-
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;└─content|string|No comments found.|-
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;└─description|string|No comments found.|-
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;└─execLog|string|No comments found.|-
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;└─during|string|No comments found.|-
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;└─screenshotList|string|No comments found.|-
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;└─showViewer|boolean|No comments found.|-

**Response-example:**
```
{
  "id": "90",
  "name": "laronda.predovic",
  "taskId": "90",
  "environmentId": "90",
  "deviceId": "90",
  "sourceType": "6ih7in",
  "sourceId": "90",
  "startTime": 1759765053864,
  "endTime": 1759765053864,
  "status": "5c7g8b",
  "projectId": "90",
  "createTime": 1759765053864,
  "updateTime": 1759765053864,
  "createUser": "n9bd7m",
  "updateUser": "hoictp",
  "username": "laronda.predovic",
  "total": 223,
  "passCount": 267,
  "failCount": 684,
  "errorCount": 762,
  "passRate": "pxroey",
  "progress": 879,
  "collectionList": [
    {
      "id": "90",
      "reportId": "90",
      "collectionId": "90",
      "collectionName": "laronda.predovic",
      "collectionVersion": "0.8.1",
      "caseTotal": 612,
      "passCount": 322,
      "failCount": 775,
      "errorCount": 229,
      "caseList": [
        {
          "id": "90",
          "reportCollectionId": "90",
          "collectionCaseIndex": 1,
          "caseId": "90",
          "caseType": "wcz4rg",
          "caseName": "laronda.predovic",
          "caseDesc": "fd2s3c",
          "runTimes": 356,
          "startTime": 1759765053864,
          "endTime": 1759765053864,
          "during": "ii8i1c",
          "status": "nc34pf",
          "transList": [
            {
              "status": "srbdzz",
              "transId": "90",
              "transName": "laronda.predovic",
              "content": "pwo8w8",
              "description": "j78spd",
              "execLog": "ya0ai2",
              "during": "ebpzfz",
              "screenshotList": "2lo9bf",
              "showViewer": true
            }
          ]
        }
      ]
    }
  ]
}
```

## 控制器：操作管理入口
用途：提供操作的保存、删除、详情、分组与分页列表接口。
### 保存操作
**URL:** http://localhost}/autotest/operation/save

**Type:** POST


**Content-Type:** application/json

**Description:** 保存操作

**Body-parameters:**

Parameter | Type|Required|Description|Since
---|---|---|---|---
id|string|false||No comments found.|-
name|string|false||No comments found.|-
type|string|false||No comments found.|-
uiType|string|false||No comments found.|-
from|string|false||No comments found.|-
system|string|false||No comments found.|-
element|string|false||No comments found.|-
data|string|false||No comments found.|-
code|string|false||No comments found.|-
projectId|string|false||No comments found.|-
description|string|false||No comments found.|-
createTime|int64|false||No comments found.|-
updateTime|int64|false||No comments found.|-
createUser|string|false||No comments found.|-
updateUser|string|false||No comments found.|-
status|int32|false||No comments found.|-

**Request-example:**
```
curl -X POST -H 'Content-Type: application/json' -i http://localhost:8080/autotest/operation/save --data '{
  "id": "90",
  "name": "laronda.predovic",
  "type": "xm7m4i",
  "uiType": "s8vc8e",
  "from": "310gn1",
  "system": "cccd1n",
  "element": "xiv2li",
  "data": "mrqc19",
  "code": "15463",
  "projectId": "90",
  "description": "xnubgh",
  "createTime": 1759765053864,
  "updateTime": 1759765053864,
  "createUser": "1zqawc",
  "updateUser": "xo0qi1",
  "status": 864
}'
```

**Response-example:**
```
Return void.
```

### 删除操作（软删除）
**URL:** http://localhost}/autotest/operation/delete

**Type:** POST


**Content-Type:** application/json

**Description:** 删除操作（软删除）

**Body-parameters:**

Parameter | Type|Required|Description|Since
---|---|---|---|---
id|string|false||No comments found.|-
name|string|false||No comments found.|-
type|string|false||No comments found.|-
uiType|string|false||No comments found.|-
from|string|false||No comments found.|-
system|string|false||No comments found.|-
element|string|false||No comments found.|-
data|string|false||No comments found.|-
code|string|false||No comments found.|-
projectId|string|false||No comments found.|-
description|string|false||No comments found.|-
createTime|int64|false||No comments found.|-
updateTime|int64|false||No comments found.|-
createUser|string|false||No comments found.|-
updateUser|string|false||No comments found.|-
status|int32|false||No comments found.|-

**Request-example:**
```
curl -X POST -H 'Content-Type: application/json' -i http://localhost:8080/autotest/operation/delete --data '{
  "id": "90",
  "name": "laronda.predovic",
  "type": "c2spbq",
  "uiType": "z5ehl7",
  "from": "20rxiy",
  "system": "di7ryf",
  "element": "7bon1f",
  "data": "izrj7e",
  "code": "15463",
  "projectId": "90",
  "description": "8v41dd",
  "createTime": 1759765053864,
  "updateTime": 1759765053864,
  "createUser": "a7a5h5",
  "updateUser": "etu9ji",
  "status": 618
}'
```

**Response-example:**
```
Return void.
```

### 获取操作详情
**URL:** http://localhost}/autotest/operation/detail/{uiType}/{operationId}

**Type:** GET


**Content-Type:** application/x-www-form-urlencoded;charset=UTF-8

**Description:** 获取操作详情

**Path-parameters:**

Parameter | Type|Required|Description|Since
---|---|---|---|---
uiType|string|true|      // UI类型（web/app）|-
operationId|string|true| // 操作ID|-

**Request-example:**
```
curl -X GET -i http://localhost:8080/autotest/operation/detail/4gvzi9/90
```
**Response-fields:**

Field | Type|Description|Since
---|---|---|---
id|string|No comments found.|-
name|string|No comments found.|-
type|string|No comments found.|-
uiType|string|No comments found.|-
from|string|No comments found.|-
system|string|No comments found.|-
element|string|No comments found.|-
data|string|No comments found.|-
code|string|No comments found.|-
projectId|string|No comments found.|-
description|string|No comments found.|-
createTime|int64|No comments found.|-
updateTime|int64|No comments found.|-
createUser|string|No comments found.|-
updateUser|string|No comments found.|-
status|int32|No comments found.|-

**Response-example:**
```
{
  "id": "90",
  "name": "laronda.predovic",
  "type": "c4ec45",
  "uiType": "20fjxh",
  "from": "8bh1po",
  "system": "hlhjdd",
  "element": "w7riiu",
  "data": "4u4vn6",
  "code": "15463",
  "projectId": "90",
  "description": "40fnkg",
  "createTime": 1759765053864,
  "updateTime": 1759765053864,
  "createUser": "b6i8em",
  "updateUser": "3ug4ez",
  "status": 280
}
```

### 获取分组操作列表
**URL:** http://localhost}/autotest/operation/group/{uiType}/list/{projectId}

**Type:** GET


**Content-Type:** application/x-www-form-urlencoded;charset=UTF-8

**Description:** 获取分组操作列表

**Path-parameters:**

Parameter | Type|Required|Description|Since
---|---|---|---|---
uiType|string|true|   // UI类型|-
projectId|string|true|// 项目ID|-

**Query-parameters:**

Parameter | Type|Required|Description|Since
---|---|---|---|---
system|string|true|   // 系统标识（app）|-

**Request-example:**
```
curl -X GET -i http://localhost:8080/autotest/operation/group/v5erpy/list/90?system=jeplsc --data '&jeplsc'
```
**Response-fields:**

Field | Type|Description|Since
---|---|---|---
id|string|No comments found.|-
name|string|No comments found.|-
operationList|array|No comments found.|-
└─id|string|No comments found.|-
└─name|string|No comments found.|-
└─type|string|No comments found.|-
└─uiType|string|No comments found.|-
└─from|string|No comments found.|-
└─system|string|No comments found.|-
└─element|string|No comments found.|-
└─data|string|No comments found.|-
└─code|string|No comments found.|-
└─projectId|string|No comments found.|-
└─description|string|No comments found.|-
└─createTime|int64|No comments found.|-
└─updateTime|int64|No comments found.|-
└─createUser|string|No comments found.|-
└─updateUser|string|No comments found.|-
└─status|int32|No comments found.|-
└─username|string|No comments found.|-
└─dataList|object|No comments found.|-
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;└─list|array|No comments found.|-
└─elementList|object|No comments found.|-
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;└─list|array|No comments found.|-

**Response-example:**
```
[
  {
    "id": "90",
    "name": "laronda.predovic",
    "operationList": [
      {
        "id": "90",
        "name": "laronda.predovic",
        "type": "7670lr",
        "uiType": "9aso8i",
        "from": "ntwjs7",
        "system": "rz3h7p",
        "element": "kfgx9l",
        "data": "ke896u",
        "code": "15463",
        "projectId": "90",
        "description": "6ejbad",
        "createTime": 1759765053864,
        "updateTime": 1759765053864,
        "createUser": "k18e0f",
        "updateUser": "xdtsk7",
        "status": 630,
        "username": "laronda.predovic",
        "dataList": {
          "list": [
            {
              "object": "any object"
            }
          ]
        },
        "elementList": {
          "list": [
            {
              "object": "any object"
            }
          ]
        }
      }
    ]
  }
]
```

### 分页查询操作列表
**URL:** http://localhost}/autotest/operation/list/{goPage}/{pageSize}

**Type:** POST


**Content-Type:** application/json

**Description:** 分页查询操作列表

**Path-parameters:**

Parameter | Type|Required|Description|Since
---|---|---|---|---
goPage|int32|true|  // 页码|-
pageSize|int32|true|// 每页大小|-

**Body-parameters:**

Parameter | Type|Required|Description|Since
---|---|---|---|---
condition|string|false||No comments found.|-
moduleId|string|false||No comments found.|-
createUser|string|false||No comments found.|-
projectId|string|false||No comments found.|-
caseType|string|false||No comments found.|-
collectionId|string|false||No comments found.|-
planId|string|false||No comments found.|-
operationType|string|false||No comments found.|-
roleId|string|false||No comments found.|-
requestUser|string|false||No comments found.|-
uiType|string|false||No comments found.|-
system|string|false||No comments found.|-
status|string|false||No comments found.|-
filter|object|false||No comments found.|-
└─map|map|false||No comments found.|-
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;└─any object|object|false||any object.|-

**Request-example:**
```
curl -X POST -H 'Content-Type: application/json' -i http://localhost:8080/autotest/operation/list/1/10 --data '{
  "condition": "53vce2",
  "moduleId": "90",
  "createUser": "uj8u25",
  "projectId": "90",
  "caseType": "sdjds6",
  "collectionId": "90",
  "planId": "90",
  "operationType": "1qrfa2",
  "roleId": "90",
  "requestUser": "pcgm1e",
  "uiType": "6zhyq7",
  "system": "qi8mma",
  "status": "x8apqg",
  "filter": {
    "map": {
      "mapKey": {}
    }
  }
}'
```
**Response-fields:**

Field | Type|Description|Since
---|---|---|---
list|array|No comments found.|-
└─id|string|No comments found.|-
└─name|string|No comments found.|-
└─type|string|No comments found.|-
└─uiType|string|No comments found.|-
└─from|string|No comments found.|-
└─system|string|No comments found.|-
└─element|string|No comments found.|-
└─data|string|No comments found.|-
└─code|string|No comments found.|-
└─projectId|string|No comments found.|-
└─description|string|No comments found.|-
└─createTime|int64|No comments found.|-
└─updateTime|int64|No comments found.|-
└─createUser|string|No comments found.|-
└─updateUser|string|No comments found.|-
└─status|int32|No comments found.|-
└─username|string|No comments found.|-
└─dataList|object|No comments found.|-
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;└─list|array|No comments found.|-
└─elementList|object|No comments found.|-
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;└─list|array|No comments found.|-
total|int64|No comments found.|-

**Response-example:**
```
{
  "list": [
    {
      "id": "90",
      "name": "laronda.predovic",
      "type": "27scgf",
      "uiType": "xczmux",
      "from": "yq9e5e",
      "system": "att3is",
      "element": "xc7wkf",
      "data": "70xf6v",
      "code": "15463",
      "projectId": "90",
      "description": "hfz305",
      "createTime": 1759765053864,
      "updateTime": 1759765053864,
      "createUser": "t2d0on",
      "updateUser": "kgov67",
      "status": 722,
      "username": "laronda.predovic",
      "dataList": {
        "list": [
          {
            "object": "any object"
          }
        ]
      },
      "elementList": {
        "list": [
          {
            "object": "any object"
          }
        ]
      }
    }
  ],
  "total": 816
}
```

## 控制器：权限与菜单入口
职责：根据用户与项目返回导航菜单，并判断设置入口的权限。
### 获取当前用户在项目下的菜单列表
**URL:** http://localhost}/autotest/menu/list

**Type:** GET


**Content-Type:** application/x-www-form-urlencoded;charset=UTF-8

**Description:** 获取当前用户在项目下的菜单列表

**Query-parameters:**

Parameter | Type|Required|Description|Since
---|---|---|---|---
userId|string|true|   // 用户ID（请求参数）|-
projectId|string|true|// 项目ID（请求参数）|-

**Request-example:**
```
curl -X GET -i http://localhost:8080/autotest/menu/list?userId=90&projectId=90 --data '&90&90'
```
**Response-fields:**

Field | Type|Description|Since
---|---|---|---
id|int32|No comments found.|-
name|string|No comments found.|-
icon|string|No comments found.|-
path|string|No comments found.|-
menus|array|No comments found.|-

**Response-example:**
```
[
  {
    "id": 909,
    "name": "laronda.predovic",
    "icon": "pj3fm0",
    "path": "g3brk8",
    "menus": [
      {
        "$ref": ".."
      }
    ]
  }
]
```

### 判断用户是否具备项目设置入口的权限
**URL:** http://localhost}/autotest/setting/permission

**Type:** GET


**Content-Type:** application/x-www-form-urlencoded;charset=UTF-8

**Description:** 判断用户是否具备项目设置入口的权限

**Query-parameters:**

Parameter | Type|Required|Description|Since
---|---|---|---|---
userId|string|true|   // 用户ID（请求参数）|-
projectId|string|true|// 项目ID（请求参数）|-

**Request-example:**
```
curl -X GET -i http://localhost:8080/autotest/setting/permission?userId=90&projectId=90 --data '&90&90'
```

**Response-example:**
```
true
```

## 控制器：测试计划入口
职责：计划保存/删除、通知配置、详情与分页列表
### 功能：保存测试计划
**URL:** http://localhost}/autotest/plan/save

**Type:** POST


**Content-Type:** application/json

**Description:** 功能：保存测试计划

**Body-parameters:**

Parameter | Type|Required|Description|Since
---|---|---|---|---
id|string|false||No comments found.|-
name|string|false||No comments found.|-
versionId|string|false||No comments found.|-
description|string|false||No comments found.|-
environmentId|string|false||No comments found.|-
maxThread|int32|false||No comments found.|-
retry|string|false||No comments found.|-
engineId|string|false||No comments found.|-
projectId|string|false||No comments found.|-
createTime|int64|false||No comments found.|-
updateTime|int64|false||No comments found.|-
createUser|string|false||No comments found.|-
updateUser|string|false||No comments found.|-
status|int32|false||No comments found.|-
startTime|string|false||No comments found.|-
frequency|string|false||No comments found.|-
username|string|false||No comments found.|-
versionName|string|false||No comments found.|-
environmentName|string|false||No comments found.|-
planCollections|array|false||No comments found.|-
└─id|string|false||No comments found.|-
└─planId|string|false||No comments found.|-
└─collectionId|string|false||No comments found.|-
└─collectionName|string|false||No comments found.|-
└─collectionVersion|string|false||No comments found.|-

**Request-example:**
```
curl -X POST -H 'Content-Type: application/json' -i http://localhost:8080/autotest/plan/save --data '{
  "id": "90",
  "name": "laronda.predovic",
  "versionId": "90",
  "description": "1735xt",
  "environmentId": "90",
  "maxThread": 543,
  "retry": "jw7c04",
  "engineId": "90",
  "projectId": "90",
  "createTime": 1759765053864,
  "updateTime": 1759765053864,
  "createUser": "0hzs34",
  "updateUser": "5sq01f",
  "status": 603,
  "startTime": "2025-10-06 23:37:33",
  "frequency": "iuvdmj",
  "username": "laronda.predovic",
  "versionName": "laronda.predovic",
  "environmentName": "laronda.predovic",
  "planCollections": [
    {
      "id": "90",
      "planId": "90",
      "collectionId": "90",
      "collectionName": "laronda.predovic",
      "collectionVersion": "0.8.1"
    }
  ]
}'
```

**Response-example:**
```
Return void.
```

### 功能：保存计划通知配置
**URL:** http://localhost}/autotest/plan/save/notice

**Type:** POST


**Content-Type:** application/json

**Description:** 功能：保存计划通知配置

**Body-parameters:**

Parameter | Type|Required|Description|Since
---|---|---|---|---
id|string|false||No comments found.|-
planId|string|false||No comments found.|-
notificationId|string|false||No comments found.|-
condition|string|false||No comments found.|-

**Request-example:**
```
curl -X POST -H 'Content-Type: application/json' -i http://localhost:8080/autotest/plan/save/notice --data '{
  "id": "90",
  "planId": "90",
  "notificationId": "90",
  "condition": "nnik0f"
}'
```

**Response-example:**
```
Return void.
```

### 功能：删除测试计划
**URL:** http://localhost}/autotest/plan/delete

**Type:** POST


**Content-Type:** application/json

**Description:** 功能：删除测试计划

**Body-parameters:**

Parameter | Type|Required|Description|Since
---|---|---|---|---
id|string|false||No comments found.|-
name|string|false||No comments found.|-
versionId|string|false||No comments found.|-
description|string|false||No comments found.|-
environmentId|string|false||No comments found.|-
maxThread|int32|false||No comments found.|-
retry|string|false||No comments found.|-
engineId|string|false||No comments found.|-
projectId|string|false||No comments found.|-
createTime|int64|false||No comments found.|-
updateTime|int64|false||No comments found.|-
createUser|string|false||No comments found.|-
updateUser|string|false||No comments found.|-
status|int32|false||No comments found.|-
startTime|string|false||No comments found.|-
frequency|string|false||No comments found.|-
username|string|false||No comments found.|-
versionName|string|false||No comments found.|-
environmentName|string|false||No comments found.|-
planCollections|array|false||No comments found.|-
└─id|string|false||No comments found.|-
└─planId|string|false||No comments found.|-
└─collectionId|string|false||No comments found.|-
└─collectionName|string|false||No comments found.|-
└─collectionVersion|string|false||No comments found.|-

**Request-example:**
```
curl -X POST -H 'Content-Type: application/json' -i http://localhost:8080/autotest/plan/delete --data '{
  "id": "90",
  "name": "laronda.predovic",
  "versionId": "90",
  "description": "u49m7l",
  "environmentId": "90",
  "maxThread": 849,
  "retry": "405x86",
  "engineId": "90",
  "projectId": "90",
  "createTime": 1759765053864,
  "updateTime": 1759765053864,
  "createUser": "nkt8r6",
  "updateUser": "j5cj7g",
  "status": 850,
  "startTime": "2025-10-06 23:37:33",
  "frequency": "3l32nv",
  "username": "laronda.predovic",
  "versionName": "laronda.predovic",
  "environmentName": "laronda.predovic",
  "planCollections": [
    {
      "id": "90",
      "planId": "90",
      "collectionId": "90",
      "collectionName": "laronda.predovic",
      "collectionVersion": "0.8.1"
    }
  ]
}'
```

**Response-example:**
```
Return void.
```

### 功能：查询计划通知配置
**URL:** http://localhost}/autotest/plan/notice/{planId}

**Type:** GET


**Content-Type:** application/x-www-form-urlencoded;charset=UTF-8

**Description:** 功能：查询计划通知配置

**Path-parameters:**

Parameter | Type|Required|Description|Since
---|---|---|---|---
planId|string|true|// 计划ID|-

**Request-example:**
```
curl -X GET -i http://localhost:8080/autotest/plan/notice/90
```
**Response-fields:**

Field | Type|Description|Since
---|---|---|---
id|string|No comments found.|-
planId|string|No comments found.|-
notificationId|string|No comments found.|-
condition|string|No comments found.|-

**Response-example:**
```
{
  "id": "90",
  "planId": "90",
  "notificationId": "90",
  "condition": "tbiv2n"
}
```

### 功能：查询计划详情
**URL:** http://localhost}/autotest/plan/detail/{planId}

**Type:** GET


**Content-Type:** application/x-www-form-urlencoded;charset=UTF-8

**Description:** 功能：查询计划详情

**Path-parameters:**

Parameter | Type|Required|Description|Since
---|---|---|---|---
planId|string|true|// 计划ID|-

**Request-example:**
```
curl -X GET -i http://localhost:8080/autotest/plan/detail/90
```
**Response-fields:**

Field | Type|Description|Since
---|---|---|---
id|string|No comments found.|-
name|string|No comments found.|-
versionId|string|No comments found.|-
description|string|No comments found.|-
environmentId|string|No comments found.|-
maxThread|int32|No comments found.|-
retry|string|No comments found.|-
engineId|string|No comments found.|-
projectId|string|No comments found.|-
createTime|int64|No comments found.|-
updateTime|int64|No comments found.|-
createUser|string|No comments found.|-
updateUser|string|No comments found.|-
status|int32|No comments found.|-
startTime|string|No comments found.|-
frequency|string|No comments found.|-
username|string|No comments found.|-
versionName|string|No comments found.|-
environmentName|string|No comments found.|-
planCollections|array|No comments found.|-
└─id|string|No comments found.|-
└─planId|string|No comments found.|-
└─collectionId|string|No comments found.|-
└─collectionName|string|No comments found.|-
└─collectionVersion|string|No comments found.|-

**Response-example:**
```
{
  "id": "90",
  "name": "laronda.predovic",
  "versionId": "90",
  "description": "key64i",
  "environmentId": "90",
  "maxThread": 739,
  "retry": "e8ovrl",
  "engineId": "90",
  "projectId": "90",
  "createTime": 1759765053864,
  "updateTime": 1759765053864,
  "createUser": "zt6ozg",
  "updateUser": "3kq9c2",
  "status": 175,
  "startTime": "2025-10-06 23:37:33",
  "frequency": "wkvksf",
  "username": "laronda.predovic",
  "versionName": "laronda.predovic",
  "environmentName": "laronda.predovic",
  "planCollections": [
    {
      "id": "90",
      "planId": "90",
      "collectionId": "90",
      "collectionName": "laronda.predovic",
      "collectionVersion": "0.8.1"
    }
  ]
}
```

### 功能：分页查询计划列表
**URL:** http://localhost}/autotest/plan/list/{goPage}/{pageSize}

**Type:** POST


**Content-Type:** application/json

**Description:** 功能：分页查询计划列表

**Path-parameters:**

Parameter | Type|Required|Description|Since
---|---|---|---|---
goPage|int32|true|   // 页码|-
pageSize|int32|true| // 每页大小|-

**Body-parameters:**

Parameter | Type|Required|Description|Since
---|---|---|---|---
condition|string|false||No comments found.|-
moduleId|string|false||No comments found.|-
createUser|string|false||No comments found.|-
projectId|string|false||No comments found.|-
caseType|string|false||No comments found.|-
collectionId|string|false||No comments found.|-
planId|string|false||No comments found.|-
operationType|string|false||No comments found.|-
roleId|string|false||No comments found.|-
requestUser|string|false||No comments found.|-
uiType|string|false||No comments found.|-
system|string|false||No comments found.|-
status|string|false||No comments found.|-
filter|object|false||No comments found.|-
└─map|map|false||No comments found.|-
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;└─any object|object|false||any object.|-

**Request-example:**
```
curl -X POST -H 'Content-Type: application/json' -i http://localhost:8080/autotest/plan/list/1/10 --data '{
  "condition": "tbgx12",
  "moduleId": "90",
  "createUser": "tmkt73",
  "projectId": "90",
  "caseType": "zmlcqg",
  "collectionId": "90",
  "planId": "90",
  "operationType": "e8h134",
  "roleId": "90",
  "requestUser": "nw51uk",
  "uiType": "g0lviy",
  "system": "yxy8u3",
  "status": "olyufn",
  "filter": {
    "map": {
      "mapKey": {}
    }
  }
}'
```
**Response-fields:**

Field | Type|Description|Since
---|---|---|---
list|array|No comments found.|-
└─id|string|No comments found.|-
└─name|string|No comments found.|-
└─versionId|string|No comments found.|-
└─description|string|No comments found.|-
└─environmentId|string|No comments found.|-
└─maxThread|int32|No comments found.|-
└─retry|string|No comments found.|-
└─engineId|string|No comments found.|-
└─projectId|string|No comments found.|-
└─createTime|int64|No comments found.|-
└─updateTime|int64|No comments found.|-
└─createUser|string|No comments found.|-
└─updateUser|string|No comments found.|-
└─status|int32|No comments found.|-
└─startTime|string|No comments found.|-
└─frequency|string|No comments found.|-
└─username|string|No comments found.|-
└─versionName|string|No comments found.|-
└─environmentName|string|No comments found.|-
└─planCollections|array|No comments found.|-
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;└─id|string|No comments found.|-
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;└─planId|string|No comments found.|-
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;└─collectionId|string|No comments found.|-
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;└─collectionName|string|No comments found.|-
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;└─collectionVersion|string|No comments found.|-
total|int64|No comments found.|-

**Response-example:**
```
{
  "list": [
    {
      "id": "90",
      "name": "laronda.predovic",
      "versionId": "90",
      "description": "0tiw5k",
      "environmentId": "90",
      "maxThread": 46,
      "retry": "tzhqqi",
      "engineId": "90",
      "projectId": "90",
      "createTime": 1759765053864,
      "updateTime": 1759765053864,
      "createUser": "hrh7fx",
      "updateUser": "esovs8",
      "status": 225,
      "startTime": "2025-10-06 23:37:33",
      "frequency": "jy01xd",
      "username": "laronda.predovic",
      "versionName": "laronda.predovic",
      "environmentName": "laronda.predovic",
      "planCollections": [
        {
          "id": "90",
          "planId": "90",
          "collectionId": "90",
          "collectionName": "laronda.predovic",
          "collectionVersion": "0.8.1"
        }
      ]
    }
  ],
  "total": 17
}
```

## 控制器：项目管理接口
职责：提供项目基本信息、成员管理、分页列表等接口
### 功能：获取指定用户的项目列表
**URL:** http://localhost}/autotest/project/user/{userId}

**Type:** GET


**Content-Type:** application/x-www-form-urlencoded;charset=UTF-8

**Description:** 功能：获取指定用户的项目列表

**Path-parameters:**

Parameter | Type|Required|Description|Since
---|---|---|---|---
userId|string|true| // 用户ID|-

**Request-example:**
```
curl -X GET -i http://localhost:8080/autotest/project/user/90
```
**Response-fields:**

Field | Type|Description|Since
---|---|---|---
id|string|No comments found.|-
name|string|No comments found.|-
description|string|No comments found.|-
projectAdmin|string|No comments found.|-
status|string|No comments found.|-
createTime|int64|No comments found.|-
updateTime|int64|No comments found.|-

**Response-example:**
```
[
  {
    "id": "90",
    "name": "laronda.predovic",
    "description": "q9pjug",
    "projectAdmin": "8223ko",
    "status": "ihg6to",
    "createTime": 1759765053864,
    "updateTime": 1759765053864
  }
]
```

### 功能：获取项目信息
**URL:** http://localhost}/autotest/project/info

**Type:** GET


**Content-Type:** application/x-www-form-urlencoded;charset=UTF-8

**Description:** 功能：获取项目信息

**Query-parameters:**

Parameter | Type|Required|Description|Since
---|---|---|---|---
projectId|string|true| // 项目ID|-

**Request-example:**
```
curl -X GET -i http://localhost:8080/autotest/project/info?projectId=90 --data '&90'
```
**Response-fields:**

Field | Type|Description|Since
---|---|---|---
id|string|No comments found.|-
name|string|No comments found.|-
description|string|No comments found.|-
projectAdmin|string|No comments found.|-
status|string|No comments found.|-
createTime|int64|No comments found.|-
updateTime|int64|No comments found.|-

**Response-example:**
```
{
  "id": "90",
  "name": "laronda.predovic",
  "description": "nrxmzj",
  "projectAdmin": "u2drrl",
  "status": "n68z4x",
  "createTime": 1759765053864,
  "updateTime": 1759765053864
}
```

### 功能：新增项目
**URL:** http://localhost}/autotest/project/add

**Type:** POST


**Content-Type:** application/json

**Description:** 功能：新增项目

**Body-parameters:**

Parameter | Type|Required|Description|Since
---|---|---|---|---
id|string|false||No comments found.|-
name|string|false||No comments found.|-
description|string|false||No comments found.|-
projectAdmin|string|false||No comments found.|-
status|string|false||No comments found.|-
createTime|int64|false||No comments found.|-
updateTime|int64|false||No comments found.|-

**Request-example:**
```
curl -X POST -H 'Content-Type: application/json' -i http://localhost:8080/autotest/project/add --data '{
  "id": "90",
  "name": "laronda.predovic",
  "description": "3wd4js",
  "projectAdmin": "yqidh2",
  "status": "mkyoo7",
  "createTime": 1759765053864,
  "updateTime": 1759765053864
}'
```

**Response-example:**
```
Return void.
```

### 功能：保存或更新项目成员关系
**URL:** http://localhost}/autotest/project/user/save

**Type:** POST


**Content-Type:** application/json

**Description:** 功能：保存或更新项目成员关系

**Body-parameters:**

Parameter | Type|Required|Description|Since
---|---|---|---|---
isEdit|boolean|false||No comments found.|-
projectId|string|false||No comments found.|-
userIds|array|false||No comments found.|-
roleIds|array|false||No comments found.|-

**Request-example:**
```
curl -X POST -H 'Content-Type: application/json' -i http://localhost:8080/autotest/project/user/save --data '{
  "isEdit": true,
  "projectId": "90",
  "userIds": [
    "zp6hig"
  ],
  "roleIds": [
    "tdg4wb"
  ]
}'
```

**Response-example:**
```
Return void.
```

### 功能：删除项目成员
**URL:** http://localhost}/autotest/project/user/delete

**Type:** POST


**Content-Type:** application/json

**Description:** 功能：删除项目成员

**Body-parameters:**

Parameter | Type|Required|Description|Since
---|---|---|---|---
id|string|false||No comments found.|-
userId|string|false||No comments found.|-
projectId|string|false||No comments found.|-
createTime|int64|false||No comments found.|-
updateTime|int64|false||No comments found.|-

**Request-example:**
```
curl -X POST -H 'Content-Type: application/json' -i http://localhost:8080/autotest/project/user/delete --data '{
  "id": "90",
  "userId": "90",
  "projectId": "90",
  "createTime": 1759765053864,
  "updateTime": 1759765053864
}'
```

**Response-example:**
```
Return void.
```

### 功能：逻辑删除项目
**URL:** http://localhost}/autotest/project/delete

**Type:** POST


**Content-Type:** application/json

**Description:** 功能：逻辑删除项目

**Body-parameters:**

Parameter | Type|Required|Description|Since
---|---|---|---|---
id|string|false||No comments found.|-
name|string|false||No comments found.|-
description|string|false||No comments found.|-
projectAdmin|string|false||No comments found.|-
status|string|false||No comments found.|-
createTime|int64|false||No comments found.|-
updateTime|int64|false||No comments found.|-

**Request-example:**
```
curl -X POST -H 'Content-Type: application/json' -i http://localhost:8080/autotest/project/delete --data '{
  "id": "90",
  "name": "laronda.predovic",
  "description": "bkeca4",
  "projectAdmin": "tqv0we",
  "status": "534cnq",
  "createTime": 1759765053864,
  "updateTime": 1759765053864
}'
```

**Response-example:**
```
Return void.
```

### 功能：恢复已删除项目
**URL:** http://localhost}/autotest/project/recover

**Type:** POST


**Content-Type:** application/json

**Description:** 功能：恢复已删除项目

**Body-parameters:**

Parameter | Type|Required|Description|Since
---|---|---|---|---
id|string|false||No comments found.|-
name|string|false||No comments found.|-
description|string|false||No comments found.|-
projectAdmin|string|false||No comments found.|-
status|string|false||No comments found.|-
createTime|int64|false||No comments found.|-
updateTime|int64|false||No comments found.|-

**Request-example:**
```
curl -X POST -H 'Content-Type: application/json' -i http://localhost:8080/autotest/project/recover --data '{
  "id": "90",
  "name": "laronda.predovic",
  "description": "t8ve15",
  "projectAdmin": "9l6ken",
  "status": "tpwioe",
  "createTime": 1759765053864,
  "updateTime": 1759765053864
}'
```

**Response-example:**
```
Return void.
```

### 功能：分页查询项目列表
**URL:** http://localhost}/autotest/project/list/{goPage}/{pageSize}

**Type:** POST


**Content-Type:** application/json

**Description:** 功能：分页查询项目列表

**Path-parameters:**

Parameter | Type|Required|Description|Since
---|---|---|---|---
goPage|int32|true|   // 页码|-
pageSize|int32|true| // 每页大小|-

**Body-parameters:**

Parameter | Type|Required|Description|Since
---|---|---|---|---
condition|string|false||No comments found.|-
moduleId|string|false||No comments found.|-
createUser|string|false||No comments found.|-
projectId|string|false||No comments found.|-
caseType|string|false||No comments found.|-
collectionId|string|false||No comments found.|-
planId|string|false||No comments found.|-
operationType|string|false||No comments found.|-
roleId|string|false||No comments found.|-
requestUser|string|false||No comments found.|-
uiType|string|false||No comments found.|-
system|string|false||No comments found.|-
status|string|false||No comments found.|-
filter|object|false||No comments found.|-
└─map|map|false||No comments found.|-
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;└─any object|object|false||any object.|-

**Request-example:**
```
curl -X POST -H 'Content-Type: application/json' -i http://localhost:8080/autotest/project/list/1/10 --data '{
  "condition": "9qix39",
  "moduleId": "90",
  "createUser": "zj0oq4",
  "projectId": "90",
  "caseType": "ywb3ho",
  "collectionId": "90",
  "planId": "90",
  "operationType": "usn5vo",
  "roleId": "90",
  "requestUser": "zu0msv",
  "uiType": "8dhl19",
  "system": "7824bf",
  "status": "kp61nj",
  "filter": {
    "map": {
      "mapKey": {}
    }
  }
}'
```
**Response-fields:**

Field | Type|Description|Since
---|---|---|---
list|array|No comments found.|-
└─id|string|No comments found.|-
└─name|string|No comments found.|-
└─description|string|No comments found.|-
└─projectAdmin|string|No comments found.|-
└─status|string|No comments found.|-
└─createTime|int64|No comments found.|-
└─updateTime|int64|No comments found.|-
└─username|string|No comments found.|-
total|int64|No comments found.|-

**Response-example:**
```
{
  "list": [
    {
      "id": "90",
      "name": "laronda.predovic",
      "description": "r9h85t",
      "projectAdmin": "3vatc8",
      "status": "gi3jzq",
      "createTime": 1759765053864,
      "updateTime": 1759765053864,
      "username": "laronda.predovic"
    }
  ],
  "total": 775
}
```

### 功能：分页查询项目成员列表
**URL:** http://localhost}/autotest/project/user/list/{goPage}/{pageSize}

**Type:** POST


**Content-Type:** application/json

**Description:** 功能：分页查询项目成员列表

**Path-parameters:**

Parameter | Type|Required|Description|Since
---|---|---|---|---
goPage|int32|true|      // 页码|-
pageSize|int32|true|    // 每页大小|-

**Body-parameters:**

Parameter | Type|Required|Description|Since
---|---|---|---|---
condition|string|false||No comments found.|-
moduleId|string|false||No comments found.|-
createUser|string|false||No comments found.|-
projectId|string|false||No comments found.|-
caseType|string|false||No comments found.|-
collectionId|string|false||No comments found.|-
planId|string|false||No comments found.|-
operationType|string|false||No comments found.|-
roleId|string|false||No comments found.|-
requestUser|string|false||No comments found.|-
uiType|string|false||No comments found.|-
system|string|false||No comments found.|-
status|string|false||No comments found.|-
filter|object|false||No comments found.|-
└─map|map|false||No comments found.|-
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;└─any object|object|false||any object.|-

**Request-example:**
```
curl -X POST -H 'Content-Type: application/json' -i http://localhost:8080/autotest/project/user/list/1/10 --data '{
  "condition": "msb5rk",
  "moduleId": "90",
  "createUser": "mbqvbc",
  "projectId": "90",
  "caseType": "v2opws",
  "collectionId": "90",
  "planId": "90",
  "operationType": "2r0ckp",
  "roleId": "90",
  "requestUser": "w5tggu",
  "uiType": "exgg92",
  "system": "pne7k4",
  "status": "pcq6ll",
  "filter": {
    "map": {
      "mapKey": {}
    }
  }
}'
```
**Response-fields:**

Field | Type|Description|Since
---|---|---|---
list|array|No comments found.|-
└─id|string|No comments found.|-
└─username|string|No comments found.|-
└─account|string|No comments found.|-
└─password|string|No comments found.|-
└─status|string|No comments found.|-
└─createTime|int64|No comments found.|-
└─updateTime|int64|No comments found.|-
└─mobile|int64|No comments found.|-
└─lastProject|string|No comments found.|-
└─email|string|No comments found.|-
total|int64|No comments found.|-

**Response-example:**
```
{
  "list": [
    {
      "id": "90",
      "username": "laronda.predovic",
      "account": "mt0b74",
      "password": "n55fya",
      "status": "vst1zv",
      "createTime": 1759765053864,
      "updateTime": 1759765053864,
      "mobile": 887,
      "lastProject": "lvx2sd",
      "email": "kerstin.spencer@yahoo.com"
    }
  ],
  "total": 43
}
```

### 功能：获取项目角色列表
**URL:** http://localhost}/autotest/project/role/list

**Type:** GET


**Content-Type:** application/x-www-form-urlencoded;charset=UTF-8

**Description:** 功能：获取项目角色列表

**Query-parameters:**

Parameter | Type|Required|Description|Since
---|---|---|---|---
projectId|string|true| // 项目ID|-

**Request-example:**
```
curl -X GET -i http://localhost:8080/autotest/project/role/list?projectId=90 --data '&90'
```
**Response-fields:**

Field | Type|Description|Since
---|---|---|---
id|string|No comments found.|-
name|string|No comments found.|-
projectId|string|No comments found.|-
createTime|int64|No comments found.|-
updateTime|int64|No comments found.|-

**Response-example:**
```
[
  {
    "id": "90",
    "name": "laronda.predovic",
    "projectId": "90",
    "createTime": 1759765053864,
    "updateTime": 1759765053864
  }
]
```

## 控制器：用户注册入口
职责：接收注册请求并调用服务层完成注册流程。
### 注册用户
**URL:** http://localhost}/autotest/register

**Type:** POST


**Content-Type:** application/json

**Description:** 注册用户

**Body-parameters:**

Parameter | Type|Required|Description|Since
---|---|---|---|---
account|string|false||No comments found.|-
mobile|int64|false||No comments found.|-
username|string|false||No comments found.|-
email|string|false||No comments found.|-
password|string|false||No comments found.|-

**Request-example:**
```
curl -X POST -H 'Content-Type: application/json' -i http://localhost:8080/autotest/register --data '{
  "account": "sdg2me",
  "mobile": 15,
  "username": "laronda.predovic",
  "email": "kerstin.spencer@yahoo.com",
  "password": "kuh4fu"
}'
```

**Response-example:**
```
string
```

## 控制层：报告管理入口
职责：调试报告查询、计划报告查询、删除与分页列表
示例：入口函数 getReportList -&gt; PageHelper.startPage -&gt; ReportService.getReportList
### 获取调试用例执行结果
**URL:** http://localhost}/autotest/report/debug/{taskId}

**Type:** GET


**Content-Type:** application/x-www-form-urlencoded;charset=UTF-8

**Description:** 获取调试用例执行结果

**Path-parameters:**

Parameter | Type|Required|Description|Since
---|---|---|---|---
taskId|string|true|                        // 任务ID|-

**Request-example:**
```
curl -X GET -i http://localhost:8080/autotest/report/debug/90
```
**Response-fields:**

Field | Type|Description|Since
---|---|---|---
id|string|No comments found.|-
reportCollectionId|string|No comments found.|-
collectionCaseIndex|int32|No comments found.|-
caseId|string|No comments found.|-
caseType|string|No comments found.|-
caseName|string|No comments found.|-
caseDesc|string|No comments found.|-
runTimes|int32|No comments found.|-
startTime|int64|No comments found.|-
endTime|int64|No comments found.|-
during|string|No comments found.|-
status|string|No comments found.|-
transList|array|No comments found.|-
└─status|string|No comments found.|-
└─transId|string|No comments found.|-
└─transName|string|No comments found.|-
└─content|string|No comments found.|-
└─description|string|No comments found.|-
└─execLog|string|No comments found.|-
└─during|string|No comments found.|-
└─screenshotList|string|No comments found.|-
└─showViewer|boolean|No comments found.|-

**Response-example:**
```
{
  "id": "90",
  "reportCollectionId": "90",
  "collectionCaseIndex": 1,
  "caseId": "90",
  "caseType": "zb9q5q",
  "caseName": "laronda.predovic",
  "caseDesc": "c913fe",
  "runTimes": 858,
  "startTime": 1759765053864,
  "endTime": 1759765053864,
  "during": "kx79se",
  "status": "4o3y2s",
  "transList": [
    {
      "status": "u1mc75",
      "transId": "90",
      "transName": "laronda.predovic",
      "content": "m4hj3k",
      "description": "w9m95x",
      "execLog": "p8ewll",
      "during": "la7cyl",
      "screenshotList": "woiluw",
      "showViewer": true
    }
  ]
}
```

### 获取计划执行结果
**URL:** http://localhost}/autotest/report/run/{reportId}

**Type:** GET


**Content-Type:** application/x-www-form-urlencoded;charset=UTF-8

**Description:** 获取计划执行结果

**Path-parameters:**

Parameter | Type|Required|Description|Since
---|---|---|---|---
reportId|string|true|         // 报告ID|-

**Request-example:**
```
curl -X GET -i http://localhost:8080/autotest/report/run/90
```
**Response-fields:**

Field | Type|Description|Since
---|---|---|---
id|string|No comments found.|-
name|string|No comments found.|-
taskId|string|No comments found.|-
environmentId|string|No comments found.|-
deviceId|string|No comments found.|-
sourceType|string|No comments found.|-
sourceId|string|No comments found.|-
startTime|int64|No comments found.|-
endTime|int64|No comments found.|-
status|string|No comments found.|-
projectId|string|No comments found.|-
createTime|int64|No comments found.|-
updateTime|int64|No comments found.|-
createUser|string|No comments found.|-
updateUser|string|No comments found.|-
username|string|No comments found.|-
total|int64|No comments found.|-
passCount|int64|No comments found.|-
failCount|int64|No comments found.|-
errorCount|int64|No comments found.|-
passRate|string|No comments found.|-
progress|int32|No comments found.|-
collectionList|array|No comments found.|-
└─id|string|No comments found.|-
└─reportId|string|No comments found.|-
└─collectionId|string|No comments found.|-
└─collectionName|string|No comments found.|-
└─collectionVersion|string|No comments found.|-
└─caseTotal|int32|No comments found.|-
└─passCount|int32|No comments found.|-
└─failCount|int32|No comments found.|-
└─errorCount|int32|No comments found.|-
└─caseList|array|No comments found.|-
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;└─id|string|No comments found.|-
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;└─reportCollectionId|string|No comments found.|-
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;└─collectionCaseIndex|int32|No comments found.|-
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;└─caseId|string|No comments found.|-
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;└─caseType|string|No comments found.|-
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;└─caseName|string|No comments found.|-
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;└─caseDesc|string|No comments found.|-
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;└─runTimes|int32|No comments found.|-
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;└─startTime|int64|No comments found.|-
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;└─endTime|int64|No comments found.|-
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;└─during|string|No comments found.|-
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;└─status|string|No comments found.|-
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;└─transList|array|No comments found.|-
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;└─status|string|No comments found.|-
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;└─transId|string|No comments found.|-
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;└─transName|string|No comments found.|-
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;└─content|string|No comments found.|-
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;└─description|string|No comments found.|-
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;└─execLog|string|No comments found.|-
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;└─during|string|No comments found.|-
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;└─screenshotList|string|No comments found.|-
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;└─showViewer|boolean|No comments found.|-

**Response-example:**
```
{
  "id": "90",
  "name": "laronda.predovic",
  "taskId": "90",
  "environmentId": "90",
  "deviceId": "90",
  "sourceType": "cxjc4v",
  "sourceId": "90",
  "startTime": 1759765053864,
  "endTime": 1759765053864,
  "status": "qegkdv",
  "projectId": "90",
  "createTime": 1759765053864,
  "updateTime": 1759765053864,
  "createUser": "s8rh72",
  "updateUser": "4jmva6",
  "username": "laronda.predovic",
  "total": 424,
  "passCount": 983,
  "failCount": 742,
  "errorCount": 806,
  "passRate": "9h7lw8",
  "progress": 95,
  "collectionList": [
    {
      "id": "90",
      "reportId": "90",
      "collectionId": "90",
      "collectionName": "laronda.predovic",
      "collectionVersion": "0.8.1",
      "caseTotal": 993,
      "passCount": 856,
      "failCount": 550,
      "errorCount": 534,
      "caseList": [
        {
          "id": "90",
          "reportCollectionId": "90",
          "collectionCaseIndex": 1,
          "caseId": "90",
          "caseType": "adojid",
          "caseName": "laronda.predovic",
          "caseDesc": "egq75q",
          "runTimes": 463,
          "startTime": 1759765053864,
          "endTime": 1759765053864,
          "during": "xj7q0r",
          "status": "7wf048",
          "transList": [
            {
              "status": "echl3w",
              "transId": "90",
              "transName": "laronda.predovic",
              "content": "xjhm84",
              "description": "rrlkoy",
              "execLog": "cncfdd",
              "during": "kxn9s9",
              "screenshotList": "2z2b69",
              "showViewer": true
            }
          ]
        }
      ]
    }
  ]
}
```

### 删除报告
**URL:** http://localhost}/autotest/report/delete

**Type:** POST


**Content-Type:** application/json

**Description:** 删除报告

**Body-parameters:**

Parameter | Type|Required|Description|Since
---|---|---|---|---
id|string|false||No comments found.|-
name|string|false||No comments found.|-
taskId|string|false||No comments found.|-
environmentId|string|false||No comments found.|-
deviceId|string|false||No comments found.|-
sourceType|string|false||No comments found.|-
sourceId|string|false||No comments found.|-
startTime|int64|false||No comments found.|-
endTime|int64|false||No comments found.|-
status|string|false||No comments found.|-
projectId|string|false||No comments found.|-
createTime|int64|false||No comments found.|-
updateTime|int64|false||No comments found.|-
createUser|string|false||No comments found.|-
updateUser|string|false||No comments found.|-

**Request-example:**
```
curl -X POST -H 'Content-Type: application/json' -i http://localhost:8080/autotest/report/delete --data '{
  "id": "90",
  "name": "laronda.predovic",
  "taskId": "90",
  "environmentId": "90",
  "deviceId": "90",
  "sourceType": "48dpy5",
  "sourceId": "90",
  "startTime": 1759765053864,
  "endTime": 1759765053864,
  "status": "jjrm1o",
  "projectId": "90",
  "createTime": 1759765053864,
  "updateTime": 1759765053864,
  "createUser": "bd9zx5",
  "updateUser": "vwmso5"
}'
```

**Response-example:**
```
Return void.
```

### 分页查询报告列表
**URL:** http://localhost}/autotest/report/list/{goPage}/{pageSize}

**Type:** POST


**Content-Type:** application/json

**Description:** 分页查询报告列表

**Path-parameters:**

Parameter | Type|Required|Description|Since
---|---|---|---|---
goPage|int32|true|           // 页码|-
pageSize|int32|true|         // 页大小|-

**Body-parameters:**

Parameter | Type|Required|Description|Since
---|---|---|---|---
condition|string|false||No comments found.|-
moduleId|string|false||No comments found.|-
createUser|string|false||No comments found.|-
projectId|string|false||No comments found.|-
caseType|string|false||No comments found.|-
collectionId|string|false||No comments found.|-
planId|string|false||No comments found.|-
operationType|string|false||No comments found.|-
roleId|string|false||No comments found.|-
requestUser|string|false||No comments found.|-
uiType|string|false||No comments found.|-
system|string|false||No comments found.|-
status|string|false||No comments found.|-
filter|object|false||No comments found.|-
└─map|map|false||No comments found.|-
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;└─any object|object|false||any object.|-

**Request-example:**
```
curl -X POST -H 'Content-Type: application/json' -i http://localhost:8080/autotest/report/list/1/10 --data '{
  "condition": "yzqhda",
  "moduleId": "90",
  "createUser": "yuo0vl",
  "projectId": "90",
  "caseType": "uqengg",
  "collectionId": "90",
  "planId": "90",
  "operationType": "8b92i6",
  "roleId": "90",
  "requestUser": "6y1kgp",
  "uiType": "jy03e5",
  "system": "jqyfrb",
  "status": "z2zh16",
  "filter": {
    "map": {
      "mapKey": {}
    }
  }
}'
```
**Response-fields:**

Field | Type|Description|Since
---|---|---|---
list|array|No comments found.|-
└─id|string|No comments found.|-
└─name|string|No comments found.|-
└─taskId|string|No comments found.|-
└─environmentId|string|No comments found.|-
└─deviceId|string|No comments found.|-
└─sourceType|string|No comments found.|-
└─sourceId|string|No comments found.|-
└─startTime|int64|No comments found.|-
└─endTime|int64|No comments found.|-
└─status|string|No comments found.|-
└─projectId|string|No comments found.|-
└─createTime|int64|No comments found.|-
└─updateTime|int64|No comments found.|-
└─createUser|string|No comments found.|-
└─updateUser|string|No comments found.|-
└─username|string|No comments found.|-
└─total|int64|No comments found.|-
└─passCount|int64|No comments found.|-
└─failCount|int64|No comments found.|-
└─errorCount|int64|No comments found.|-
└─passRate|string|No comments found.|-
└─progress|int32|No comments found.|-
└─collectionList|array|No comments found.|-
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;└─id|string|No comments found.|-
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;└─reportId|string|No comments found.|-
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;└─collectionId|string|No comments found.|-
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;└─collectionName|string|No comments found.|-
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;└─collectionVersion|string|No comments found.|-
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;└─caseTotal|int32|No comments found.|-
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;└─passCount|int32|No comments found.|-
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;└─failCount|int32|No comments found.|-
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;└─errorCount|int32|No comments found.|-
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;└─caseList|array|No comments found.|-
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;└─id|string|No comments found.|-
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;└─reportCollectionId|string|No comments found.|-
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;└─collectionCaseIndex|int32|No comments found.|-
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;└─caseId|string|No comments found.|-
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;└─caseType|string|No comments found.|-
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;└─caseName|string|No comments found.|-
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;└─caseDesc|string|No comments found.|-
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;└─runTimes|int32|No comments found.|-
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;└─startTime|int64|No comments found.|-
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;└─endTime|int64|No comments found.|-
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;└─during|string|No comments found.|-
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;└─status|string|No comments found.|-
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;└─transList|array|No comments found.|-
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;└─status|string|No comments found.|-
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;└─transId|string|No comments found.|-
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;└─transName|string|No comments found.|-
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;└─content|string|No comments found.|-
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;└─description|string|No comments found.|-
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;└─execLog|string|No comments found.|-
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;└─during|string|No comments found.|-
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;└─screenshotList|string|No comments found.|-
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;└─showViewer|boolean|No comments found.|-
total|int64|No comments found.|-

**Response-example:**
```
{
  "list": [
    {
      "id": "90",
      "name": "laronda.predovic",
      "taskId": "90",
      "environmentId": "90",
      "deviceId": "90",
      "sourceType": "aqgps8",
      "sourceId": "90",
      "startTime": 1759765053864,
      "endTime": 1759765053864,
      "status": "0a5tdp",
      "projectId": "90",
      "createTime": 1759765053864,
      "updateTime": 1759765053864,
      "createUser": "ewwnvx",
      "updateUser": "edbjfb",
      "username": "laronda.predovic",
      "total": 177,
      "passCount": 942,
      "failCount": 193,
      "errorCount": 378,
      "passRate": "i1hl7d",
      "progress": 811,
      "collectionList": [
        {
          "id": "90",
          "reportId": "90",
          "collectionId": "90",
          "collectionName": "laronda.predovic",
          "collectionVersion": "0.8.1",
          "caseTotal": 698,
          "passCount": 19,
          "failCount": 423,
          "errorCount": 566,
          "caseList": [
            {
              "id": "90",
              "reportCollectionId": "90",
              "collectionCaseIndex": 1,
              "caseId": "90",
              "caseType": "z7u3hj",
              "caseName": "laronda.predovic",
              "caseDesc": "fdtqpx",
              "runTimes": 535,
              "startTime": 1759765053864,
              "endTime": 1759765053864,
              "during": "jogaho",
              "status": "03vbnw",
              "transList": [
                {
                  "status": "1bc29s",
                  "transId": "90",
                  "transName": "laronda.predovic",
                  "content": "a4tzo8",
                  "description": "9swp22",
                  "execLog": "8p4ypf",
                  "during": "x8ecyu",
                  "screenshotList": "iybp05",
                  "showViewer": true
                }
              ]
            }
          ]
        }
      ]
    }
  ],
  "total": 326
}
```

## 控制器：角色管理入口
职责：提供角色分页列表、角色下用户分页列表与删除用户角色绑定的接口。
### 分页查询角色列表
**URL:** http://localhost}/autotest/role/list/{goPage}/{pageSize}

**Type:** POST


**Content-Type:** application/json

**Description:** 分页查询角色列表

**Path-parameters:**

Parameter | Type|Required|Description|Since
---|---|---|---|---
goPage|int32|true|      页码|-
pageSize|int32|true|    每页大小|-

**Body-parameters:**

Parameter | Type|Required|Description|Since
---|---|---|---|---
condition|string|false||No comments found.|-
moduleId|string|false||No comments found.|-
createUser|string|false||No comments found.|-
projectId|string|false||No comments found.|-
caseType|string|false||No comments found.|-
collectionId|string|false||No comments found.|-
planId|string|false||No comments found.|-
operationType|string|false||No comments found.|-
roleId|string|false||No comments found.|-
requestUser|string|false||No comments found.|-
uiType|string|false||No comments found.|-
system|string|false||No comments found.|-
status|string|false||No comments found.|-
filter|object|false||No comments found.|-
└─map|map|false||No comments found.|-
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;└─any object|object|false||any object.|-

**Request-example:**
```
curl -X POST -H 'Content-Type: application/json' -i http://localhost:8080/autotest/role/list/1/10 --data '{
  "condition": "1opo5y",
  "moduleId": "90",
  "createUser": "2btfqy",
  "projectId": "90",
  "caseType": "cf77p6",
  "collectionId": "90",
  "planId": "90",
  "operationType": "5yxngx",
  "roleId": "90",
  "requestUser": "7osf00",
  "uiType": "ie0kr9",
  "system": "z7erzg",
  "status": "vf3q7m",
  "filter": {
    "map": {
      "mapKey": {}
    }
  }
}'
```
**Response-fields:**

Field | Type|Description|Since
---|---|---|---
list|array|No comments found.|-
└─id|string|No comments found.|-
└─name|string|No comments found.|-
└─projectId|string|No comments found.|-
└─createTime|int64|No comments found.|-
└─updateTime|int64|No comments found.|-
└─projectName|string|No comments found.|-
total|int64|No comments found.|-

**Response-example:**
```
{
  "list": [
    {
      "id": "90",
      "name": "laronda.predovic",
      "projectId": "90",
      "createTime": 1759765053864,
      "updateTime": 1759765053864,
      "projectName": "laronda.predovic"
    }
  ],
  "total": 663
}
```

### 分页查询角色下的用户列表
**URL:** http://localhost}/autotest/role/user/list/{goPage}/{pageSize}

**Type:** POST


**Content-Type:** application/json

**Description:** 分页查询角色下的用户列表

**Path-parameters:**

Parameter | Type|Required|Description|Since
---|---|---|---|---
goPage|int32|true|  页码|-
pageSize|int32|true|每页大小|-

**Body-parameters:**

Parameter | Type|Required|Description|Since
---|---|---|---|---
condition|string|false||No comments found.|-
moduleId|string|false||No comments found.|-
createUser|string|false||No comments found.|-
projectId|string|false||No comments found.|-
caseType|string|false||No comments found.|-
collectionId|string|false||No comments found.|-
planId|string|false||No comments found.|-
operationType|string|false||No comments found.|-
roleId|string|false||No comments found.|-
requestUser|string|false||No comments found.|-
uiType|string|false||No comments found.|-
system|string|false||No comments found.|-
status|string|false||No comments found.|-
filter|object|false||No comments found.|-
└─map|map|false||No comments found.|-
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;└─any object|object|false||any object.|-

**Request-example:**
```
curl -X POST -H 'Content-Type: application/json' -i http://localhost:8080/autotest/role/user/list/1/10 --data '{
  "condition": "eb0v1d",
  "moduleId": "90",
  "createUser": "x9wkx2",
  "projectId": "90",
  "caseType": "q9xanj",
  "collectionId": "90",
  "planId": "90",
  "operationType": "38ferw",
  "roleId": "90",
  "requestUser": "3zb79d",
  "uiType": "eeubal",
  "system": "t67zo2",
  "status": "tkyuia",
  "filter": {
    "map": {
      "mapKey": {}
    }
  }
}'
```
**Response-fields:**

Field | Type|Description|Since
---|---|---|---
list|array|No comments found.|-
└─id|string|No comments found.|-
└─username|string|No comments found.|-
└─account|string|No comments found.|-
└─password|string|No comments found.|-
└─status|string|No comments found.|-
└─createTime|int64|No comments found.|-
└─updateTime|int64|No comments found.|-
└─mobile|int64|No comments found.|-
└─lastProject|string|No comments found.|-
└─email|string|No comments found.|-
total|int64|No comments found.|-

**Response-example:**
```
{
  "list": [
    {
      "id": "90",
      "username": "laronda.predovic",
      "account": "d5el94",
      "password": "vme68b",
      "status": "4qitfo",
      "createTime": 1759765053864,
      "updateTime": 1759765053864,
      "mobile": 820,
      "lastProject": "irvffq",
      "email": "kerstin.spencer@yahoo.com"
    }
  ],
  "total": 61
}
```

### 删除用户与角色的绑定关系
**URL:** http://localhost}/autotest/role/user/delete

**Type:** POST


**Content-Type:** application/json

**Description:** 删除用户与角色的绑定关系

**Body-parameters:**

Parameter | Type|Required|Description|Since
---|---|---|---|---
id|string|false||No comments found.|-
userId|string|false||No comments found.|-
roleId|string|false||No comments found.|-
createTime|int64|false||No comments found.|-
updateTime|int64|false||No comments found.|-

**Request-example:**
```
curl -X POST -H 'Content-Type: application/json' -i http://localhost:8080/autotest/role/user/delete --data '{
  "id": "90",
  "userId": "90",
  "roleId": "90",
  "createTime": 1759765053864,
  "updateTime": 1759765053864
}'
```

**Response-example:**
```
Return void.
```

## 控制器：任务执行入口
职责：接收前端执行请求，补齐运行用户信息并委派至服务层。
### 发起执行任务
**URL:** http://localhost}/autotest/run

**Type:** POST


**Content-Type:** application/json

**Description:** 发起执行任务

**Body-parameters:**

Parameter | Type|Required|Description|Since
---|---|---|---|---
engineId|string|false||No comments found.|-
environmentId|string|false||No comments found.|-
deviceId|string|false||No comments found.|-
sourceType|string|false||No comments found.|-
sourceId|string|false||No comments found.|-
sourceName|string|false||No comments found.|-
taskType|string|false||No comments found.|-
runUser|string|false||No comments found.|-
projectId|string|false||No comments found.|-
debugData|object|false||No comments found.|-
└─id|string|false||No comments found.|-
└─num|int64|false||No comments found.|-
└─name|string|false||No comments found.|-
└─level|string|false||No comments found.|-
└─moduleId|string|false||No comments found.|-
└─moduleName|string|false||No comments found.|-
└─projectId|string|false||No comments found.|-
└─type|string|false||No comments found.|-
└─thirdParty|string|false||No comments found.|-
└─description|string|false||No comments found.|-
└─environmentIds|object|false||No comments found.|-
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;└─list|array|false||No comments found.|-
└─system|string|false||No comments found.|-
└─commonParam|object|false||No comments found.|-
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;└─map|map|false||No comments found.|-
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;└─any object|object|false||any object.|-
└─createTime|int64|false||No comments found.|-
└─updateTime|int64|false||No comments found.|-
└─createUser|string|false||No comments found.|-
└─updateUser|string|false||No comments found.|-
└─status|string|false||No comments found.|-
└─caseApis|array|false||No comments found.|-
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;└─id|string|false||No comments found.|-
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;└─index|int64|false||No comments found.|-
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;└─caseId|string|false||No comments found.|-
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;└─apiId|string|false||No comments found.|-
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;└─description|string|false||No comments found.|-
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;└─header|object|false||No comments found.|-
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;└─list|array|false||No comments found.|-
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;└─body|object|false||No comments found.|-
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;└─map|map|false||No comments found.|-
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;└─any object|object|false||any object.|-
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;└─query|object|false||No comments found.|-
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;└─list|array|false||No comments found.|-
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;└─rest|object|false||No comments found.|-
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;└─list|array|false||No comments found.|-
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;└─assertion|object|false||No comments found.|-
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;└─list|array|false||No comments found.|-
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;└─relation|object|false||No comments found.|-
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;└─list|array|false||No comments found.|-
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;└─controller|object|false||No comments found.|-
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;└─list|array|false||No comments found.|-
└─caseWebs|array|false||No comments found.|-
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;└─id|string|false||No comments found.|-
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;└─index|int64|false||No comments found.|-
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;└─caseId|string|false||No comments found.|-
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;└─operationId|string|false||No comments found.|-
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;└─description|string|false||No comments found.|-
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;└─element|object|false||No comments found.|-
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;└─list|array|false||No comments found.|-
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;└─data|object|false||No comments found.|-
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;└─list|array|false||No comments found.|-
└─caseApps|array|false||No comments found.|-
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;└─id|string|false||No comments found.|-
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;└─index|int64|false||No comments found.|-
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;└─caseId|string|false||No comments found.|-
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;└─operationId|string|false||No comments found.|-
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;└─description|string|false||No comments found.|-
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;└─element|object|false||No comments found.|-
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;└─list|array|false||No comments found.|-
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;└─data|object|false||No comments found.|-
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;└─list|array|false||No comments found.|-
user|string|false||No comments found.|-
planId|string|false||No comments found.|-

**Request-example:**
```
curl -X POST -H 'Content-Type: application/json' -i http://localhost:8080/autotest/run --data '{
  "engineId": "90",
  "environmentId": "90",
  "deviceId": "90",
  "sourceType": "742dqa",
  "sourceId": "90",
  "sourceName": "laronda.predovic",
  "taskType": "weynww",
  "runUser": "uyvmyk",
  "projectId": "90",
  "debugData": {
    "id": "90",
    "num": 952,
    "name": "laronda.predovic",
    "level": "3d8jdk",
    "moduleId": "90",
    "moduleName": "laronda.predovic",
    "projectId": "90",
    "type": "k4iqem",
    "thirdParty": "ihdbw1",
    "description": "qqbxfl",
    "environmentIds": {
      "list": [
        {
          "object": "any object"
        }
      ]
    },
    "system": "46o9jc",
    "commonParam": {
      "map": {
        "mapKey": {}
      }
    },
    "createTime": 1759765053864,
    "updateTime": 1759765053864,
    "createUser": "hagszq",
    "updateUser": "hcvnhb",
    "status": "ptckze",
    "caseApis": [
      {
        "id": "90",
        "index": 44,
        "caseId": "90",
        "apiId": "90",
        "description": "e6qyjy",
        "header": {
          "list": [
            {
              "object": "any object"
            }
          ]
        },
        "body": {
          "map": {
            "mapKey": {}
          }
        },
        "query": {
          "list": [
            {
              "object": "any object"
            }
          ]
        },
        "rest": {
          "list": [
            {
              "object": "any object"
            }
          ]
        },
        "assertion": {
          "list": [
            {
              "object": "any object"
            }
          ]
        },
        "relation": {
          "list": [
            {
              "object": "any object"
            }
          ]
        },
        "controller": {
          "list": [
            {
              "object": "any object"
            }
          ]
        }
      }
    ],
    "caseWebs": [
      {
        "id": "90",
        "index": 469,
        "caseId": "90",
        "operationId": "90",
        "description": "x56i7a",
        "element": {
          "list": [
            {
              "object": "any object"
            }
          ]
        },
        "data": {
          "list": [
            {
              "object": "any object"
            }
          ]
        }
      }
    ],
    "caseApps": [
      {
        "id": "90",
        "index": 739,
        "caseId": "90",
        "operationId": "90",
        "description": "1qsxcx",
        "element": {
          "list": [
            {
              "object": "any object"
            }
          ]
        },
        "data": {
          "list": [
            {
              "object": "any object"
            }
          ]
        }
      }
    ]
  },
  "user": "9ir01n",
  "planId": "90"
}'
```
**Response-fields:**

Field | Type|Description|Since
---|---|---|---
id|string|No comments found.|-
name|string|No comments found.|-
type|string|No comments found.|-
status|string|No comments found.|-
engineId|string|No comments found.|-
projectId|string|No comments found.|-
createTime|int64|No comments found.|-
updateTime|int64|No comments found.|-
createUser|string|No comments found.|-
updateUser|string|No comments found.|-
username|string|No comments found.|-
reportId|string|No comments found.|-
sourceType|string|No comments found.|-
sourceId|string|No comments found.|-
environmentId|string|No comments found.|-
deviceId|string|No comments found.|-

**Response-example:**
```
{
  "id": "90",
  "name": "laronda.predovic",
  "type": "lvaauw",
  "status": "qa838j",
  "engineId": "90",
  "projectId": "90",
  "createTime": 1759765053864,
  "updateTime": 1759765053864,
  "createUser": "xaslyu",
  "updateUser": "98jtog",
  "username": "laronda.predovic",
  "reportId": "90",
  "sourceType": "2kbqqp",
  "sourceId": "90",
  "environmentId": "90",
  "deviceId": "90"
}
```

## 控制器：系统配置相关入口
职责：提供断言列表等系统级配置信息查询接口。
### 查询断言规则列表
**URL:** http://localhost}/autotest/system/assertion/list

**Type:** GET


**Content-Type:** application/x-www-form-urlencoded;charset=UTF-8

**Description:** 查询断言规则列表

**Request-example:**
```
curl -X GET -i http://localhost:8080/autotest/system/assertion/list
```
**Response-fields:**

Field | Type|Description|Since
---|---|---|---
id|string|No comments found.|-
name|string|No comments found.|-

**Response-example:**
```
[
  {
    "id": "90",
    "name": "laronda.predovic"
  }
]
```

## 控制器：测试文件管理入口
职责：提供测试文件与测试包的上传、删除、查询全部与分页列表接口。
说明：控制器负责轻量的会话用户注入与分页包装，业务逻辑在 Service 层实现。
### 上传测试文件（multipart/form-data）
**URL:** http://localhost}/autotest/file/upload

**Type:** POST


**Content-Type:** multipart/form-data

**Description:** 上传测试文件（multipart/form-data）

**Query-parameters:**

Parameter | Type|Required|Description|Since
---|---|---|---|---
name|string|true|  文件名称|-
projectId|string|true| 项目ID|-
description|string|true|文件描述|-
file|file|false|      上传文件（可选）|-

**Request-example:**
```
curl -X POST -H 'Content-Type: multipart/form-data' -F 'file=' -i http://localhost:8080/autotest/file/upload --data 'name=laronda.predovic&projectId=90&description=e5703o'
```

**Response-example:**
```
Return void.
```

### 上传测试包（multipart/form-data）（app）
**URL:** http://localhost}/autotest/file/package/upload

**Type:** POST


**Content-Type:** multipart/form-data

**Description:** 上传测试包（multipart/form-data）（app）

**Query-parameters:**

Parameter | Type|Required|Description|Since
---|---|---|---|---
name|string|true|包名称|-
file|file|false|       上传包文件（可选）|-

**Request-example:**
```
curl -X POST -H 'Content-Type: multipart/form-data' -F 'file=' -i http://localhost:8080/autotest/file/package/upload --data 'name=laronda.predovic'
```

**Response-example:**
```
string
```

### 删除测试文件
**URL:** http://localhost}/autotest/file/delete

**Type:** POST


**Content-Type:** application/json

**Description:** 删除测试文件

**Body-parameters:**

Parameter | Type|Required|Description|Since
---|---|---|---|---
id|string|false||No comments found.|-
name|string|false||No comments found.|-
filePath|string|false||No comments found.|-
projectId|string|false||No comments found.|-
description|string|false||No comments found.|-
createTime|int64|false||No comments found.|-
updateTime|int64|false||No comments found.|-
createUser|string|false||No comments found.|-
updateUser|string|false||No comments found.|-
status|int32|false||No comments found.|-

**Request-example:**
```
curl -X POST -H 'Content-Type: application/json' -i http://localhost:8080/autotest/file/delete --data '{
  "id": "90",
  "name": "laronda.predovic",
  "filePath": "7vfsbs",
  "projectId": "90",
  "description": "0iqtsm",
  "createTime": 1759765053864,
  "updateTime": 1759765053864,
  "createUser": "yd4uey",
  "updateUser": "cqre1m",
  "status": 440
}'
```

**Response-example:**
```
Return void.
```

### 查询项目下所有测试文件
**URL:** http://localhost}/autotest/file/all/{projectId}

**Type:** GET


**Content-Type:** application/x-www-form-urlencoded;charset=UTF-8

**Description:** 查询项目下所有测试文件

**Path-parameters:**

Parameter | Type|Required|Description|Since
---|---|---|---|---
projectId|string|true|项目ID|-

**Request-example:**
```
curl -X GET -i http://localhost:8080/autotest/file/all/90
```
**Response-fields:**

Field | Type|Description|Since
---|---|---|---
id|string|No comments found.|-
name|string|No comments found.|-
filePath|string|No comments found.|-
projectId|string|No comments found.|-
description|string|No comments found.|-
createTime|int64|No comments found.|-
updateTime|int64|No comments found.|-
createUser|string|No comments found.|-
updateUser|string|No comments found.|-
status|int32|No comments found.|-

**Response-example:**
```
[
  {
    "id": "90",
    "name": "laronda.predovic",
    "filePath": "x6sn9o",
    "projectId": "90",
    "description": "yt444d",
    "createTime": 1759765053864,
    "updateTime": 1759765053864,
    "createUser": "9wbmkf",
    "updateUser": "m20by2",
    "status": 289
  }
]
```

### 分页查询测试文件列表
**URL:** http://localhost}/autotest/file/list/{goPage}/{pageSize}

**Type:** POST


**Content-Type:** application/json

**Description:** 分页查询测试文件列表

**Path-parameters:**

Parameter | Type|Required|Description|Since
---|---|---|---|---
goPage|int32|true|  页码|-
pageSize|int32|true|每页大小|-

**Body-parameters:**

Parameter | Type|Required|Description|Since
---|---|---|---|---
condition|string|false||No comments found.|-
moduleId|string|false||No comments found.|-
createUser|string|false||No comments found.|-
projectId|string|false||No comments found.|-
caseType|string|false||No comments found.|-
collectionId|string|false||No comments found.|-
planId|string|false||No comments found.|-
operationType|string|false||No comments found.|-
roleId|string|false||No comments found.|-
requestUser|string|false||No comments found.|-
uiType|string|false||No comments found.|-
system|string|false||No comments found.|-
status|string|false||No comments found.|-
filter|object|false||No comments found.|-
└─map|map|false||No comments found.|-
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;└─any object|object|false||any object.|-

**Request-example:**
```
curl -X POST -H 'Content-Type: application/json' -i http://localhost:8080/autotest/file/list/1/10 --data '{
  "condition": "lslfsl",
  "moduleId": "90",
  "createUser": "q6v9k9",
  "projectId": "90",
  "caseType": "rvl0ss",
  "collectionId": "90",
  "planId": "90",
  "operationType": "0rb3vp",
  "roleId": "90",
  "requestUser": "jone88",
  "uiType": "cno94u",
  "system": "n8f2zj",
  "status": "4cau3f",
  "filter": {
    "map": {
      "mapKey": {}
    }
  }
}'
```
**Response-fields:**

Field | Type|Description|Since
---|---|---|---
list|array|No comments found.|-
└─id|string|No comments found.|-
└─name|string|No comments found.|-
└─filePath|string|No comments found.|-
└─projectId|string|No comments found.|-
└─description|string|No comments found.|-
└─createTime|int64|No comments found.|-
└─updateTime|int64|No comments found.|-
└─createUser|string|No comments found.|-
└─updateUser|string|No comments found.|-
└─status|int32|No comments found.|-
└─username|string|用户名称（创建/更新操作者的展示名）|-
total|int64|No comments found.|-

**Response-example:**
```
{
  "list": [
    {
      "id": "90",
      "name": "laronda.predovic",
      "filePath": "whyfw8",
      "projectId": "90",
      "description": "n0av93",
      "createTime": 1759765053864,
      "updateTime": 1759765053864,
      "createUser": "nsz9q9",
      "updateUser": "3gkeu0",
      "status": 937,
      "username": "laronda.predovic"
    }
  ],
  "total": 911
}
```

## 控制器：用户管理入口
职责：用户信息、项目切换、密码与资料更新、角色与查询
### 功能：查询用户信息
**URL:** http://localhost}/autotest/user/info/{id}

**Type:** GET


**Content-Type:** application/x-www-form-urlencoded;charset=UTF-8

**Description:** 功能：查询用户信息

**Path-parameters:**

Parameter | Type|Required|Description|Since
---|---|---|---|---
id|string|true|    // 用户ID|-

**Request-example:**
```
curl -X GET -i http://localhost:8080/autotest/user/info/90
```
**Response-fields:**

Field | Type|Description|Since
---|---|---|---
id|string|No comments found.|-
username|string|No comments found.|-
account|string|No comments found.|-
password|string|No comments found.|-
status|string|No comments found.|-
createTime|int64|No comments found.|-
updateTime|int64|No comments found.|-
mobile|int64|No comments found.|-
lastProject|string|No comments found.|-
email|string|No comments found.|-

**Response-example:**
```
{
  "id": "90",
  "username": "laronda.predovic",
  "account": "oksl8m",
  "password": "ns47g4",
  "status": "tide4n",
  "createTime": 1759765053864,
  "updateTime": 1759765053864,
  "mobile": 433,
  "lastProject": "q2ruym",
  "email": "kerstin.spencer@yahoo.com"
}
```

### 功能：切换所属项目
**URL:** http://localhost}/autotest/user/switch/project

**Type:** POST


**Content-Type:** application/json

**Description:** 功能：切换所属项目

**Body-parameters:**

Parameter | Type|Required|Description|Since
---|---|---|---|---
id|string|false||No comments found.|-
username|string|false||No comments found.|-
account|string|false||No comments found.|-
password|string|false||No comments found.|-
status|string|false||No comments found.|-
createTime|int64|false||No comments found.|-
updateTime|int64|false||No comments found.|-
mobile|int64|false||No comments found.|-
lastProject|string|false||No comments found.|-
email|string|false||No comments found.|-

**Request-example:**
```
curl -X POST -H 'Content-Type: application/json' -i http://localhost:8080/autotest/user/switch/project --data '{
  "id": "90",
  "username": "laronda.predovic",
  "account": "wve0i0",
  "password": "60uabf",
  "status": "e4zdw7",
  "createTime": 1759765053864,
  "updateTime": 1759765053864,
  "mobile": 821,
  "lastProject": "1r0ys2",
  "email": "kerstin.spencer@yahoo.com"
}'
```
**Response-fields:**

Field | Type|Description|Since
---|---|---|---
id|string|No comments found.|-
username|string|No comments found.|-
account|string|No comments found.|-
password|string|No comments found.|-
status|string|No comments found.|-
createTime|int64|No comments found.|-
updateTime|int64|No comments found.|-
mobile|int64|No comments found.|-
lastProject|string|No comments found.|-
email|string|No comments found.|-
permissions|array|No comments found.|-

**Response-example:**
```
{
  "id": "90",
  "username": "laronda.predovic",
  "account": "0fl6zu",
  "password": "ag6o47",
  "status": "7k7wv5",
  "createTime": 1759765053864,
  "updateTime": 1759765053864,
  "mobile": 835,
  "lastProject": "x35p80",
  "email": "kerstin.spencer@yahoo.com",
  "permissions": [
    "ze2klm"
  ]
}
```

### 功能：更新用户密码
**URL:** http://localhost}/autotest/user/update/password

**Type:** POST


**Content-Type:** application/json

**Description:** 功能：更新用户密码

**Body-parameters:**

Parameter | Type|Required|Description|Since
---|---|---|---|---
userId|string|false||No comments found.|-
oldPassword|string|false||No comments found.|-
newPassword|string|false||No comments found.|-

**Request-example:**
```
curl -X POST -H 'Content-Type: application/json' -i http://localhost:8080/autotest/user/update/password --data '{
  "userId": "90",
  "oldPassword": "7gm23a",
  "newPassword": "ifi7wb"
}'
```

**Response-example:**
```
Return void.
```

### 功能：更新用户资料
**URL:** http://localhost}/autotest/user/update/info

**Type:** POST


**Content-Type:** application/json

**Description:** 功能：更新用户资料

**Body-parameters:**

Parameter | Type|Required|Description|Since
---|---|---|---|---
id|string|false||No comments found.|-
username|string|false||No comments found.|-
account|string|false||No comments found.|-
password|string|false||No comments found.|-
status|string|false||No comments found.|-
createTime|int64|false||No comments found.|-
updateTime|int64|false||No comments found.|-
mobile|int64|false||No comments found.|-
lastProject|string|false||No comments found.|-
email|string|false||No comments found.|-

**Request-example:**
```
curl -X POST -H 'Content-Type: application/json' -i http://localhost:8080/autotest/user/update/info --data '{
  "id": "90",
  "username": "laronda.predovic",
  "account": "akewrs",
  "password": "mqy24f",
  "status": "gs4hjq",
  "createTime": 1759765053864,
  "updateTime": 1759765053864,
  "mobile": 915,
  "lastProject": "1nznr7",
  "email": "kerstin.spencer@yahoo.com"
}'
```

**Response-example:**
```
Return void.
```

### 功能：查询所有用户
**URL:** http://localhost}/autotest/user/all

**Type:** GET


**Content-Type:** application/x-www-form-urlencoded;charset=UTF-8

**Description:** 功能：查询所有用户

**Request-example:**
```
curl -X GET -i http://localhost:8080/autotest/user/all
```
**Response-fields:**

Field | Type|Description|Since
---|---|---|---
id|string|No comments found.|-
username|string|No comments found.|-
account|string|No comments found.|-
password|string|No comments found.|-
status|string|No comments found.|-
createTime|int64|No comments found.|-
updateTime|int64|No comments found.|-
mobile|int64|No comments found.|-
lastProject|string|No comments found.|-
email|string|No comments found.|-

**Response-example:**
```
[
  {
    "id": "90",
    "username": "laronda.predovic",
    "account": "rvxvey",
    "password": "rjog2v",
    "status": "3ewj3c",
    "createTime": 1759765053864,
    "updateTime": 1759765053864,
    "mobile": 683,
    "lastProject": "3s54cf",
    "email": "kerstin.spencer@yahoo.com"
  }
]
```

### 功能：查询用户在项目下的角色ID列表
**URL:** http://localhost}/autotest/user/role/list

**Type:** GET


**Content-Type:** application/x-www-form-urlencoded;charset=UTF-8

**Description:** 功能：查询用户在项目下的角色ID列表

**Query-parameters:**

Parameter | Type|Required|Description|Since
---|---|---|---|---
projectId|string|true| // 项目ID|-
userId|string|true|    // 用户ID|-

**Request-example:**
```
curl -X GET -i http://localhost:8080/autotest/user/role/list?projectId=90&userId=90 --data '&90&90'
```

**Response-example:**
```
[
  "1l5pb7",
  "6blzg0"
]
```

### 功能：模糊查询用户
**URL:** http://localhost}/autotest/user/query

**Type:** GET


**Content-Type:** application/x-www-form-urlencoded;charset=UTF-8

**Description:** 功能：模糊查询用户

**Query-parameters:**

Parameter | Type|Required|Description|Since
---|---|---|---|---
account|string|true|  // 账号关键字|-

**Request-example:**
```
curl -X GET -i http://localhost:8080/autotest/user/query?account=r1ahuz --data '&r1ahuz'
```
**Response-fields:**

Field | Type|Description|Since
---|---|---|---
id|string|No comments found.|-
username|string|No comments found.|-
account|string|No comments found.|-
password|string|No comments found.|-
status|string|No comments found.|-
createTime|int64|No comments found.|-
updateTime|int64|No comments found.|-
mobile|int64|No comments found.|-
lastProject|string|No comments found.|-
email|string|No comments found.|-

**Response-example:**
```
[
  {
    "id": "90",
    "username": "laronda.predovic",
    "account": "jkngfy",
    "password": "70rd2w",
    "status": "si12r0",
    "createTime": 1759765053864,
    "updateTime": 1759765053864,
    "mobile": 598,
    "lastProject": "50qmg7",
    "email": "kerstin.spencer@yahoo.com"
  }
]
```

## 控制器：版本管理入口
职责：提供版本的保存、删除、列表与分页查询接口。
### 保存版本（新增或更新）
**URL:** http://localhost}/autotest/version/save

**Type:** POST


**Content-Type:** application/json

**Description:** 保存版本（新增或更新）

**Body-parameters:**

Parameter | Type|Required|Description|Since
---|---|---|---|---
id|string|false||No comments found.|-
name|string|false||No comments found.|-
description|string|false||No comments found.|-
projectId|string|false||No comments found.|-
createTime|int64|false||No comments found.|-
updateTime|int64|false||No comments found.|-

**Request-example:**
```
curl -X POST -H 'Content-Type: application/json' -i http://localhost:8080/autotest/version/save --data '{
  "id": "90",
  "name": "laronda.predovic",
  "description": "dv6aqc",
  "projectId": "90",
  "createTime": 1759765053864,
  "updateTime": 1759765053864
}'
```

**Response-example:**
```
Return void.
```

### 删除版本（逻辑删除）
**URL:** http://localhost}/autotest/version/delete

**Type:** POST


**Content-Type:** application/json

**Description:** 删除版本（逻辑删除）

**Body-parameters:**

Parameter | Type|Required|Description|Since
---|---|---|---|---
id|string|false||No comments found.|-
name|string|false||No comments found.|-
description|string|false||No comments found.|-
projectId|string|false||No comments found.|-
createTime|int64|false||No comments found.|-
updateTime|int64|false||No comments found.|-

**Request-example:**
```
curl -X POST -H 'Content-Type: application/json' -i http://localhost:8080/autotest/version/delete --data '{
  "id": "90",
  "name": "laronda.predovic",
  "description": "n0rt8z",
  "projectId": "90",
  "createTime": 1759765053864,
  "updateTime": 1759765053864
}'
```

**Response-example:**
```
Return void.
```

### 查询项目下版本列表
**URL:** http://localhost}/autotest/version/list/{projectId}

**Type:** GET


**Content-Type:** application/x-www-form-urlencoded;charset=UTF-8

**Description:** 查询项目下版本列表

**Path-parameters:**

Parameter | Type|Required|Description|Since
---|---|---|---|---
projectId|string|true|    // 项目ID|-

**Request-example:**
```
curl -X GET -i http://localhost:8080/autotest/version/list/90
```
**Response-fields:**

Field | Type|Description|Since
---|---|---|---
id|string|No comments found.|-
name|string|No comments found.|-
description|string|No comments found.|-
projectId|string|No comments found.|-
createTime|int64|No comments found.|-
updateTime|int64|No comments found.|-

**Response-example:**
```
[
  {
    "id": "90",
    "name": "laronda.predovic",
    "description": "u0rk67",
    "projectId": "90",
    "createTime": 1759765053864,
    "updateTime": 1759765053864
  }
]
```

### 分页查询版本列表<br><br>说明：统一使用 PageHelper 进行分页拦截，返回 Pager。
**URL:** http://localhost}/autotest/version/list/{goPage}/{pageSize}

**Type:** POST


**Content-Type:** application/json

**Description:** 分页查询版本列表

说明：统一使用 PageHelper 进行分页拦截，返回 Pager。

**Path-parameters:**

Parameter | Type|Required|Description|Since
---|---|---|---|---
goPage|int32|true|   // 页码|-
pageSize|int32|true| // 每页大小|-

**Body-parameters:**

Parameter | Type|Required|Description|Since
---|---|---|---|---
condition|string|false||No comments found.|-
moduleId|string|false||No comments found.|-
createUser|string|false||No comments found.|-
projectId|string|false||No comments found.|-
caseType|string|false||No comments found.|-
collectionId|string|false||No comments found.|-
planId|string|false||No comments found.|-
operationType|string|false||No comments found.|-
roleId|string|false||No comments found.|-
requestUser|string|false||No comments found.|-
uiType|string|false||No comments found.|-
system|string|false||No comments found.|-
status|string|false||No comments found.|-
filter|object|false||No comments found.|-
└─map|map|false||No comments found.|-
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;└─any object|object|false||any object.|-

**Request-example:**
```
curl -X POST -H 'Content-Type: application/json' -i http://localhost:8080/autotest/version/list/1/10 --data '{
  "condition": "sjfm3y",
  "moduleId": "90",
  "createUser": "l0yck7",
  "projectId": "90",
  "caseType": "se68nb",
  "collectionId": "90",
  "planId": "90",
  "operationType": "fu3ejr",
  "roleId": "90",
  "requestUser": "aakz3v",
  "uiType": "ad8xkv",
  "system": "fhk4b1",
  "status": "zlx9jk",
  "filter": {
    "map": {
      "mapKey": {}
    }
  }
}'
```
**Response-fields:**

Field | Type|Description|Since
---|---|---|---
list|array|No comments found.|-
└─id|string|No comments found.|-
└─name|string|No comments found.|-
└─description|string|No comments found.|-
└─projectId|string|No comments found.|-
└─createTime|int64|No comments found.|-
└─updateTime|int64|No comments found.|-
total|int64|No comments found.|-

**Response-example:**
```
{
  "list": [
    {
      "id": "90",
      "name": "laronda.predovic",
      "description": "hodxw0",
      "projectId": "90",
      "createTime": 1759765053864,
      "updateTime": 1759765053864
    }
  ],
  "total": 513
}
```



import request from './api'

export const caseApi = {
  // 获取案例列表
  list(params) {
    return request.get('/cases', { params })
  },

  // 获取案例详情
  get(id) {
    return request.get(`/cases/${id}`)
  },

  // 创建案例
  create(data) {
    return request.post('/cases', data)
  },

  // 更新案例
  update(id, data) {
    return request.put(`/cases/${id}`, data)
  },

  // 删除案例
  delete(id) {
    return request.delete(`/cases/${id}`)
  }
}

export const searchApi = {
  // 坐席搜索
  searchCases(data) {
    return request.post('/search/cases', data)
  },

  // 用户搜索
  userSearch(params) {
    return request.get('/search/user', { params })
  }
}

export const approvalApi = {
  // 获取审批列表
  list(params) {
    return request.get('/approvals', { params })
  },

  // 审批通过
  approve(id, comment) {
    return request.post(`/approvals/${id}/approve`, { comment })
  },

  // 审批拒绝
  reject(id, comment) {
    return request.post(`/approvals/${id}/reject`, { comment })
  }
}

export const operationApi = {
  // 案例统计
  getCaseStats() {
    return request.get('/operation/stats/case')
  },

  // 问答统计
  getQAStats() {
    return request.get('/operation/stats/qa')
  },

  // 操作日志
  getLogs(params) {
    return request.get('/operation/logs', { params })
  }
}

export const qaApi = {
  // 智能问答
  ask(question) {
    return request.post('/graph/ask', { question })
  }
}

export const fileApi = {
  // 上传文件
  upload(formData, onProgress) {
    return request.post('/files/upload', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
      onUploadProgress: onProgress
    })
  },

  // 下载文件
  download(bucket, objectName) {
    return request.get(`/files/${bucket}/${objectName}`, {
      responseType: 'blob'
    })
  },

  // 删除文件
  delete(bucket, objectName) {
    return request.delete(`/files/${bucket}/${objectName}`)
  }
}

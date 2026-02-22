<template>
   <div class="app-container">
      <el-form :model="queryParams" ref="queryRef" :inline="true" v-show="showSearch">
         <el-form-item label="学校/班级" prop="deptName">
            <el-input
               v-model="queryParams.deptName"
               placeholder="请输入学校或班级名称"
               clearable
               style="width: 200px"
               @keyup.enter="handleQuery"
            />
         </el-form-item>
         <el-form-item label="状态" prop="status">
            <el-select v-model="queryParams.status" placeholder="状态" clearable style="width: 200px">
               <el-option
                  v-for="dict in sys_normal_disable"
                  :key="dict.value"
                  :label="dict.label"
                  :value="dict.value"
               />
            </el-select>
         </el-form-item>
         <el-form-item>
            <el-button type="primary" icon="Search" @click="handleQuery">搜索</el-button>
            <el-button icon="Refresh" @click="resetQuery">重置</el-button>
         </el-form-item>
      </el-form>

      <el-row :gutter="10" class="mb8">
         <el-col :span="1.5">
            <el-button
               type="primary"
               plain
               icon="Plus"
               @click="handleAdd"
               v-hasPermi="['system:dept:add']"
            >新增</el-button>
         </el-col>
         <el-col :span="1.5">
            <el-button
               type="info"
               plain
               icon="Sort"
               @click="toggleExpandAll"
            >展开/折叠</el-button>
         </el-col>
         <right-toolbar v-model:showSearch="showSearch" @queryTable="getList"></right-toolbar>
      </el-row>
      <el-alert
         title="组织管理说明：统一采用“大王集团 > 学校 > 班级”三级结构，禁止新增超过三级的节点。"
         type="info"
         :closable="false"
         style="margin-bottom: 12px"
      />

      <el-table
         v-if="refreshTable"
         v-loading="loading"
         :data="deptList"
         row-key="deptId"
         :default-expand-all="isExpandAll"
         :tree-props="{ children: 'children', hasChildren: 'hasChildren' }"
      >
         <el-table-column prop="deptName" label="学校/班级名称" width="240"></el-table-column>
         <el-table-column label="层级类型" width="120">
            <template #default="scope">
               <el-tag :type="resolveDeptType(scope.row).tag">
                  {{ resolveDeptType(scope.row).label }}
               </el-tag>
            </template>
         </el-table-column>
         <el-table-column prop="orderNum" label="排序" width="200"></el-table-column>
         <el-table-column prop="status" label="状态" width="100">
            <template #default="scope">
               <dict-tag :options="sys_normal_disable" :value="scope.row.status" />
            </template>
         </el-table-column>
         <el-table-column label="创建时间" align="center" prop="createTime" width="200">
            <template #default="scope">
               <span>{{ parseTime(scope.row.createTime) }}</span>
            </template>
         </el-table-column>
         <el-table-column label="操作" align="center" class-name="small-padding fixed-width">
            <template #default="scope">
               <el-button link type="primary" icon="Edit" @click="handleUpdate(scope.row)" v-hasPermi="['system:dept:edit']">修改</el-button>
               <el-button link type="primary" icon="Plus" @click="handleAdd(scope.row)" v-hasPermi="['system:dept:add']">新增</el-button>
               <el-button v-if="scope.row.parentId != 0" link type="primary" icon="Delete" @click="handleDelete(scope.row)" v-hasPermi="['system:dept:remove']">删除</el-button>
            </template>
         </el-table-column>
      </el-table>

      <!-- 添加或修改部门对话框 -->
      <el-dialog :title="title" v-model="open" width="600px" append-to-body>
         <el-form ref="deptRef" :model="form" :rules="rules" label-width="80px">
            <el-row>
               <el-col :span="24" v-if="form.parentId !== 0">
                  <el-form-item label="上级节点" prop="parentId">
                     <el-tree-select
                        v-model="form.parentId"
                        :data="deptOptions"
                        :props="{ value: 'deptId', label: 'deptName', children: 'children' }"
                        value-key="deptId"
                        placeholder="请选择上级节点"
                        check-strictly
                     />
                  </el-form-item>
               </el-col>
               <el-col :span="12">
                  <el-form-item label="学校/班级名" prop="deptName">
                     <el-input v-model="form.deptName" placeholder="请输入学校或班级名称" />
                  </el-form-item>
               </el-col>
               <el-col :span="12">
                  <el-form-item label="显示排序" prop="orderNum">
                     <el-input-number v-model="form.orderNum" controls-position="right" :min="0" />
                  </el-form-item>
               </el-col>
               <el-col :span="12">
                  <el-form-item label="负责人" prop="leader">
                     <el-input v-model="form.leader" placeholder="请输入负责人" maxlength="20" />
                  </el-form-item>
               </el-col>
               <el-col :span="12">
                  <el-form-item label="联系电话" prop="phone">
                     <el-input v-model="form.phone" placeholder="请输入联系电话" maxlength="11" />
                  </el-form-item>
               </el-col>
               <el-col :span="12">
                  <el-form-item label="邮箱" prop="email">
                     <el-input v-model="form.email" placeholder="请输入邮箱" maxlength="50" />
                  </el-form-item>
               </el-col>
               <el-col :span="12">
                  <el-form-item label="状态">
                     <el-radio-group v-model="form.status">
                        <el-radio
                           v-for="dict in sys_normal_disable"
                           :key="dict.value"
                           :value="dict.value"
                        >{{ dict.label }}</el-radio>
                     </el-radio-group>
                  </el-form-item>
               </el-col>
            </el-row>
         </el-form>
         <template #footer>
            <div class="dialog-footer">
               <el-button type="primary" @click="submitForm">确 定</el-button>
               <el-button @click="cancel">取 消</el-button>
            </div>
         </template>
      </el-dialog>
   </div>
</template>

<script setup name="Dept">
import { listDept, getDept, delDept, addDept, updateDept, listDeptExcludeChild } from "@/api/system/dept"

const { proxy } = getCurrentInstance()
const { sys_normal_disable } = proxy.useDict("sys_normal_disable")

const deptList = ref([])
const open = ref(false)
const loading = ref(true)
const showSearch = ref(true)
const title = ref("")
const deptOptions = ref([])
const isExpandAll = ref(true)
const refreshTable = ref(true)

const data = reactive({
  form: {},
  queryParams: {
    deptName: undefined,
    status: undefined
  },
  rules: {
    parentId: [{ required: true, message: "上级节点不能为空", trigger: "blur" }],
    deptName: [{ required: true, message: "学校/班级名称不能为空", trigger: "blur" }],
    orderNum: [{ required: true, message: "显示排序不能为空", trigger: "blur" }],
    email: [{ type: "email", message: "请输入正确的邮箱地址", trigger: ["blur", "change"] }],
    phone: [{ pattern: /^1[3|4|5|6|7|8|9][0-9]\d{8}$/, message: "请输入正确的手机号码", trigger: "blur" }]
  },
})

const { queryParams, form, rules } = toRefs(data)

/** 查询部门列表 */
function getList() {
  loading.value = true
  listDept(queryParams.value).then(response => {
    deptList.value = proxy.handleTree(response.data, "deptId")
    loading.value = false
  })
}

/** 取消按钮 */
function cancel() {
  open.value = false
  reset()
}

/** 表单重置 */
function reset() {
  form.value = {
    deptId: undefined,
    parentId: undefined,
    deptName: undefined,
    orderNum: 0,
    leader: undefined,
    phone: undefined,
    email: undefined,
    status: "0"
  }
  proxy.resetForm("deptRef")
}

/** 搜索按钮操作 */
function handleQuery() {
  getList()
}

/** 重置按钮操作 */
function resetQuery() {
  proxy.resetForm("queryRef")
  handleQuery()
}

/** 新增按钮操作 */
function handleAdd(row) {
  reset()
  listDept().then(response => {
    deptOptions.value = proxy.handleTree(response.data, "deptId")
    const topNodes = response.data.filter(item => item.parentId === 0)
    const groupNode = topNodes.find(item => item.deptName === "大王集团")
    if (!row) {
      if (groupNode) {
        form.value.parentId = groupNode.deptId
        title.value = "新增学校"
      } else {
        form.value.parentId = 0
        form.value.deptName = "大王集团"
        title.value = "初始化集团"
      }
    }
  })
  if (row != undefined) {
    const level = getDeptLevel(row)
    if (level >= 2) {
      proxy.$modal.msgWarning("班级下不能继续新增子节点")
      return
    }
    form.value.parentId = row.deptId
    title.value = level === 0 ? "新增学校" : "新增班级"
    open.value = true
    return
  }
  open.value = true
}

/** 展开/折叠操作 */
function toggleExpandAll() {
  refreshTable.value = false
  isExpandAll.value = !isExpandAll.value
  nextTick(() => {
    refreshTable.value = true
  })
}

/** 修改按钮操作 */
function handleUpdate(row) {
  reset()
  listDeptExcludeChild(row.deptId).then(response => {
    deptOptions.value = proxy.handleTree(response.data, "deptId")
  })
  getDept(row.deptId).then(response => {
    form.value = response.data
    open.value = true
    title.value = "修改学校/班级"
  })
}

/** 提交按钮 */
function submitForm() {
  proxy.$refs["deptRef"].validate(valid => {
    if (valid) {
      const parent = findDeptById(deptOptions.value, form.value.parentId)
      if (parent && getDeptLevel(parent) >= 2) {
        proxy.$modal.msgWarning("仅支持到班级层级，不能继续向下新增")
        return
      }
      if (form.value.deptId != undefined) {
        updateDept(form.value).then(response => {
          proxy.$modal.msgSuccess("修改成功")
          open.value = false
          getList()
        })
      } else {
        addDept(form.value).then(response => {
          proxy.$modal.msgSuccess("新增成功")
          open.value = false
          getList()
        })
      }
    }
  })
}

/** 删除按钮操作 */
function handleDelete(row) {
  proxy.$modal.confirm('是否确认删除“' + row.deptName + '”？').then(function() {
    return delDept(row.deptId)
  }).then(() => {
    getList()
    proxy.$modal.msgSuccess("删除成功")
  }).catch(() => {})
}

function findDeptById(list, deptId) {
  if (!list || deptId === undefined || deptId === null) return null
  for (const item of list) {
    if (item.deptId === deptId) return item
    if (item.children && item.children.length) {
      const found = findDeptById(item.children, deptId)
      if (found) return found
    }
  }
  return null
}

function getDeptLevel(row) {
  if (!row) return 0
  const arr = String(row.ancestors || "0").split(",").filter(Boolean)
  return row.parentId === 0 ? 0 : Math.max(arr.length - 1, 0)
}

function resolveDeptType(row) {
  const level = getDeptLevel(row)
  if (level === 0) return { label: "集团", tag: "danger" }
  if (level === 1) return { label: "学校", tag: "primary" }
  return { label: "班级", tag: "success" }
}

getList()
</script>

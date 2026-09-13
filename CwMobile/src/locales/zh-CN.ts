/**
 * 简体中文语言包（移动端，默认语言）。
 *
 * ## 与网页端的关系：**刻意各存一份**
 *
 * `CwMobile` 不是网页端的镜像（镜像只覆盖 `Cw_WebUi → CwClient`），它有自己的构建与发布节奏。
 * 两端文案**大部分相同、但并不完全一致**（列表 Tab 就叫「数据」「售价」，网页端叫
 * 「数据分析」「售价管理」），硬共享一份反而要开一堆「移动端特例」的开关。
 * 因此这里独立一份。代价是公共文案要改两处 —— 与 `ocr/` 和 `voice/` 各自留一份
 * `UpstreamRejectedError` 是同一个取舍：**用少量重复换两端互不牵制**。
 *
 * ## 两个分区
 *
 * - `app.*` —— **界面文案**，由本文件（移动端）拥有。必须在后端尚未应答时就能渲染。
 * - `backend.*` —— **后端自己产生的文案**的对照表，键就是后端返回的 `detail` 原文。
 *   后端目录在 `CwServer/locales/zh-CN.json`，**两边必须保持一致**。
 *   用 `translateBackendMessage()` 查询，查不到原样显示，绝不显示空串。
 *
 * ## 为什么导出 `MessageSchema`
 *
 * `en-US.ts` 用它约束自己 —— **漏翻一个键会在 `vue-tsc` 阶段直接报错**。
 */

const zhCN = {
  app: {
    nav: {
      inventory: '库存',
      analytics: '数据',
      ledger: '账本',
      pricing: '售价',
      settings: '设置',
    },

    // 「公共词汇」—— 先抽到这里再逐文件替换，否则同一个「保存」会在多个文件里各写一份。
    // 只在**字面确实相同**时才复用；语境不同就各自开 key。
    common: {
      cancel: '取消',
      close: '关闭',
      save: '保存',
      remove: '删除',
      create: '新增',
      name: '名称',
      description: '描述',
      price: '价格',
      stock: '库存',
      quantity: '库存数量',
      unit: '单位',
      notes: '备注',
      recorder: '录入人',
      expiresAt: '过期时间',
      expired: '已过期',
      icon: '图标',
      iconColor: '图标颜色',
      category: '分类',
      subCategory: '子分类',
      noData: '暂无数据',
      loading: '加载中',
      selectPlaceholder: '请选择',
      inputName: '请输入名称',
      inputDescription: '请输入描述',
      inputUnit: '请输入单位',
      inputRecorder: '请输入录入人',
      inputNotes: '请输入备注',
    },

    inventory: {
      selectSubCategoryHint: '选择子分类',
      // 「请选择子分类」（toast）与「选择子分类」（顶栏提示）字面不同、语气也不同，各开一个 key。
      pickSubCategory: '请选择子分类',
      pickSubCategoryEmpty: '请选择子分类后查看物品',
      selectFirst: '请先在左上角选择子分类',
      pickCategory: '选择分类',
      noItems: '暂无物品，点击下方按钮新增',
      addItem: '新增物品',
      editItem: '编辑物品',
      deleteItemTitle: '删除物品',
      confirmDeleteItem: '确定要删除「{name}」吗？',
      noRecorder: '未记录录入人',
      // 原来在模板里由「价格 ¥… · 库存」+ 下一行「数量 单位」拼成，合并成一条带插值的文案，
      // 英文语序才不会被中文写死。
      priceStock: '价格 ¥{price} · 库存 {quantity} {unit}',
      expiresOn: '过期 {date}',
    },

    ledger: {
      title: '账本',
      scopeDay: '按天',
      scopeWeek: '按周',
      scopeMonth: '按月',
      scopeYear: '按年',
      typeAll: '全部',
      typeIncome: '收入',
      typeExpense: '支出',
      amount: '金额',
      type: '类型',
      date: '日期',
      platform: '平台',
      person: '记账人',
      budgetOverview: '预算概览',
      chartTitle: '收支统计',
      chartAmountAxis: '金额 (¥)',
      searchPlaceholder: '搜索描述/平台/记账人',
      noEntries: '暂无账单记录',
      unnamed: '未命名',
      addBill: '新增账单',
      editBill: '编辑账单',
      deleteTitle: '删除账单',
      deleteConfirm: '确定要删除这条账单吗？',
      inputAmountInvalid: '请输入正确的金额',
      inputPlatform: '支付宝/微信/银行等',
      inputDescription: '消费描述',
      inputPerson: '谁记的',
    },

    // 录入区（导入 / 上传）与通知区。
    // 「上传单据」「导入数据」在**菜单项**与**弹层标题**两处出现，且指的是同一个东西，
    // 所以各只有一个 key，不是巧合重名。
    intake: {
      uploadReceipt: '上传单据',
      exportData: '导出数据',
      importData: '导入数据',
      dataTools: '库存数据工具',
      chooseImage: '点击选择图片上传',
      uploading: '上传中…',
      exportSuccess: '导出成功',
      exportFailed: '导出失败',
      uploadSuccess: '上传成功',
      uploadFailed: '上传失败',
      parseFailed: '文件解析失败',
      importFailed: '导入失败',
      importPickFile: '选择 JSON 备份文件',
      importConflicts: '发现以下冲突项，勾选的项目将被跳过：',
      importKindCategory: '大类',
      importKindSubCategory: '子分类',
      importConfirm: '确认导入',
      importDoneTitle: '导入完成',
      importDoneDesc: '新增大类 {categories} 个，子分类 {subCategories} 个，物品 {items} 个',
    },

    notify: {
      title: '消息中心',
      stockAlerts: '库存预警',
      lowStock: '低库存',
      systemNotifications: '系统通知',
      markRead: '已读',
      empty: '暂无通知',
    },

    categoryManager: {
      title: '分类管理',
      addCategory: '新增大类',
      editCategory: '编辑大类',
      addSubCategory: '新增子分类',
      editSubCategory: '编辑子分类',
      deleteCategory: '删除大类',
      deleteSubCategory: '删除子分类',
      confirmDeleteCategory: '确定要删除大类「{name}」吗？',
      confirmDeleteSubCategory: '确定要删除子分类「{name}」吗？',
      noCategories: '暂无分类，点击右上角新增',
      noSubCategories: '暂无子分类',
    },

    // 图标选择器的 48 个 tooltip。键就是 @vicons/ionicons5 的组件名 ——
    // 换图标库时键跟着变，比「按序号 icon1..icon48」可维护得多。
    icons: {
      FolderOutline: '文件夹',
      CartOutline: '购物车',
      ShirtOutline: '衣物',
      HardwareChipOutline: '芯片',
      NutritionOutline: '营养',
      CameraOutline: '相机',
      GameControllerOutline: '游戏',
      BookOutline: '书本',
      MusicalNotesOutline: '音乐',
      FitnessOutline: '健身',
      HeartOutline: '心形',
      StarOutline: '星形',
      FlashlightOutline: '手电',
      ColorPaletteOutline: '调色板',
      CubeOutline: '立方体',
      DiamondOutline: '钻石',
      HomeOutline: '家居',
      CarOutline: '汽车',
      WalkOutline: '步行',
      AirplaneOutline: '飞机',
      BoatOutline: '船',
      PawOutline: '宠物',
      LeafOutline: '植物',
      FlameOutline: '火焰',
      WaterOutline: '水滴',
      SunnyOutline: '太阳',
      MoonOutline: '月亮',
      CloudyOutline: '云朵',
      UmbrellaOutline: '雨伞',
      GiftOutline: '礼物',
      SparklesOutline: '闪光',
      TrophyOutline: '奖杯',
      WineOutline: '酒杯',
      CafeOutline: '咖啡',
      PizzaOutline: '披萨',
      MedicalOutline: '医疗',
      WalletOutline: '钱包',
      KeyOutline: '钥匙',
      LockClosedOutline: '锁',
      GlobeOutline: '地球',
      MapOutline: '地图',
      TimeOutline: '时间',
      BeerOutline: '啤酒',
      BugOutline: '昆虫',
      FishOutline: '鱼',
      BulbOutline: '灯泡',
      ExtensionPuzzleOutline: '拼图',
      RibbonOutline: '丝带',
    },
  },
  backend: {
    'Category not found': '分类不存在',
    'SubCategory not found': '子分类不存在',
    'Item not found': '物品不存在',
    'Tag not found': '标签不存在',
    'Notification not found': '通知不存在',
    'Budget not found': '预算不存在',
    'Ledger item not found': '账目不存在',
    'Recurring bill not found': '定时账单不存在',
    'Pricing not found': '售价记录不存在',
    'Pricing category not found': '售价分类不存在',
    'Pricing sub-category not found': '售价子分类不存在',
    'empty file': '上传的文件为空',
    '科学的管理每一颗螺丝钉': '科学的管理每一颗螺丝钉',
  },
}

export type MessageSchema = typeof zhCN
export default zhCN
